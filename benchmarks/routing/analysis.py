"""Credit estimates and paired routing analysis."""

from __future__ import annotations

import json
import math
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent


def load_prices() -> dict[str, Any]:
    return json.loads((HERE / "prices.json").read_text())


def session_credits(session: dict[str, Any], prices: dict[str, Any]) -> float | None:
    usage = session.get("usage")
    rates = prices["models"].get(session.get("model"))
    if not isinstance(usage, dict) or rates is None:
        return None
    raw = usage["input_tokens"] - usage["cached_input_tokens"]
    if raw < 0:
        return None
    return (
        raw * rates["input"]
        + usage["cached_input_tokens"] * rates["cached_input"]
        + usage["output_tokens"] * rates["output"]
    ) / 1_000_000


def route_credits(record: dict[str, Any], prices: dict[str, Any]) -> dict[str, Any]:
    sessions = record.get("telemetry", {}).get("sessions", [])
    if not sessions:
        return {"estimate": None, "minimum": None, "maximum": None, "reason": "sessions missing"}
    root_id = record["telemetry"].get("root_session_id")
    parts = []
    for session in sessions:
        base = session_credits(session, prices)
        if base is None:
            return {"estimate": None, "minimum": None, "maximum": None, "reason": "model or usage missing"}
        observed = session.get("observed_tier")
        configured = record["arm_config"]["tier"] if session["session_id"] == root_id else "default"
        multiplier = prices["fast_multiplier"]
        estimate = base * (multiplier if configured == "fast" else 1)
        minimum = base * (multiplier if observed == "fast" else 1)
        maximum = base * (1 if observed == "default" else multiplier)
        parts.append((estimate, minimum, maximum))
    return {
        "estimate": sum(part[0] for part in parts),
        "minimum": sum(part[1] for part in parts),
        "maximum": sum(part[2] for part in parts),
        "reason": "tier not observed" if any(s.get("observed_tier") is None for s in sessions) else None,
    }


def _task_measure(rows: list[dict[str, Any]], scenario: str) -> tuple[float, float, float]:
    successes = sum(bool(row.get("accepted")) for row in rows)
    quality = successes / len(rows) if rows else 0.0
    if not successes:
        return quality, math.inf, math.inf
    credits = [row.get("credits", {}).get(scenario) for row in rows]
    cost = sum(credits) / successes if all(value is not None for value in credits) else math.nan
    time = sum(row["elapsed_seconds"] for row in rows) / successes
    return quality, cost, time


def _ratio(best: float, current: float) -> float:
    if math.isnan(best) or math.isnan(current):
        return math.nan
    if math.isinf(current):
        return 0.0
    if current == 0:
        return 1.0
    return best / current


def paired_scores(records: list[dict[str, Any]], scenario: str | dict[str, str] = "estimate") -> dict[str, Any]:
    by_task: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for row in records:
        if row.get("calibration") or row.get("status") == "skipped":
            continue
        by_task[row["task_id"]][row["arm"]].append(row)
    per_task: dict[str, Any] = {}
    for task, arms in sorted(by_task.items()):
        if not all(arm in arms for arm in ("terra", "luna")):
            continue
        values = {arm: _task_measure(arms[arm], scenario[arm] if isinstance(scenario, dict) else scenario)
                  for arm in ("terra", "luna")}
        finite_costs = [v[1] for v in values.values() if math.isfinite(v[1])]
        finite_times = [v[2] for v in values.values() if math.isfinite(v[2])]
        best_cost = min(finite_costs) if finite_costs else math.inf
        best_time = min(finite_times) if finite_times else math.inf
        scores = {}
        for arm, (quality, cost, elapsed) in values.items():
            credit_component = _ratio(best_cost, cost) if finite_costs else 0.0
            time_component = _ratio(best_time, elapsed) if finite_times else 0.0
            scores[arm] = 100 * (0.5 * quality + 0.3 * credit_component + 0.2 * time_component)
        category = arms["terra"][0]["category"]
        per_task[task] = {"category": category, "scores": scores, "values": values}
    categories = defaultdict(list)
    for task in per_task.values():
        categories[task["category"]].append(task)
    summary = {
        arm: sum(task["scores"][arm] for task in per_task.values()) / len(per_task)
        if per_task else None for arm in ("terra", "luna")
    }
    by_category = {
        category: {arm: sum(t["scores"][arm] for t in tasks) / len(tasks) for arm in ("terra", "luna")}
        for category, tasks in sorted(categories.items())
    }
    return {"tasks": per_task, "scores": summary, "by_category": by_category}


def paired_bootstrap(records: list[dict[str, Any]], repetitions: int = 10000) -> dict[str, Any]:
    result = paired_scores(records)
    deltas = [task["scores"]["luna"] - task["scores"]["terra"] for task in result["tasks"].values()]
    quality_deltas = [task["values"]["luna"][0] - task["values"]["terra"][0] for task in result["tasks"].values()]
    if not deltas or any(math.isnan(value) for value in deltas):
        return {"delta": None, "interval_95": None, "reason": "paired cost data incomplete"}
    rng = random.Random(20260923)
    draws = sorted(sum(rng.choices(deltas, k=len(deltas))) / len(deltas) for _ in range(repetitions))
    quality_draws = sorted(sum(rng.choices(quality_deltas, k=len(quality_deltas))) / len(quality_deltas)
                           for _ in range(repetitions))
    return {
        "delta": sum(deltas) / len(deltas),
        "interval_95": [draws[int(0.025 * repetitions)], draws[int(0.975 * repetitions)]],
        "quality_delta": sum(quality_deltas) / len(quality_deltas),
        "quality_interval_95": [quality_draws[int(0.025 * repetitions)], quality_draws[int(0.975 * repetitions)]],
        "reason": None,
    }


def load_records(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def report(records: list[dict[str, Any]]) -> dict[str, Any]:
    prices = load_prices()
    for row in records:
        row["credits"] = route_credits(row, prices)
    paired = paired_scores(records)
    bounds = {
        "luna_pessimistic": paired_scores(records, {"luna": "maximum", "terra": "minimum"})["scores"],
        "luna_optimistic": paired_scores(records, {"luna": "minimum", "terra": "maximum"})["scores"],
    }
    totals = {}
    completeness = {"planned": 144, "recorded": len(records), "missing_runs": [], "skipped_runs": [],
                    "missing_root": [], "missing_usage": [], "unknown_tier": [],
                    "missing_expected_child": [], "malformed_rollouts": [], "missing_acceptance": []}
    index = {(row["task_id"], row["arm"], row.get("repeat", 1)): row for row in records}
    task_ids = [task["id"] for task in json.loads((HERE / "tasks.json").read_text())["tasks"]]
    for task_id in task_ids:
        for arm in ("terra", "luna"):
            for repeat in range(1, 4):
                if (task_id, arm, repeat) not in index:
                    completeness["missing_runs"].append([task_id, arm, repeat])
    for row in records:
        ident = [row["task_id"], row["arm"], row.get("repeat", 1)]
        if row.get("status") == "skipped":
            completeness["skipped_runs"].append({"run": ident, "reason": row.get("failure_reason")})
            continue
        telemetry = row.get("telemetry", {})
        sessions = telemetry.get("sessions", [])
        if not telemetry.get("root_session_id"):
            completeness["missing_root"].append(ident)
        if not sessions or any(session.get("usage") is None for session in sessions):
            completeness["missing_usage"].append(ident)
        if any(session.get("observed_tier") is None for session in sessions):
            completeness["unknown_tier"].append(ident)
        if row.get("expected_route") == "delegated" and row.get("sol_child_count", 0) == 0:
            completeness["missing_expected_child"].append(ident)
        if any(session.get("malformed_lines") for session in sessions):
            completeness["malformed_rollouts"].append(ident)
        if row.get("acceptance", {}).get("bench_result") is None:
            completeness["missing_acceptance"].append(ident)
    for arm in ("terra", "luna"):
        subset = [row for row in records if row.get("arm") == arm and not row.get("calibration")]
        attempted = [row for row in subset if row.get("status") != "skipped"]
        delegated = [row for row in attempted if row.get("route_observed") == "delegated"]
        estimates = [row["credits"]["estimate"] for row in attempted]
        totals[arm] = {
            "runs": len(attempted), "skipped": len(subset) - len(attempted),
            "accepted": sum(bool(row.get("accepted")) for row in attempted),
            "fallbacks": sum(row.get("route_observed") == "fallback" for row in attempted),
            "delegated_runs": len(delegated),
            "delegated_accepted": sum(bool(row.get("accepted")) for row in delegated),
            "runtime_failures": sum(row.get("status") in {"timeout", "error"} for row in attempted),
            "unknown_costs": sum(value is None for value in estimates),
            "elapsed_seconds": sum(row.get("elapsed_seconds", 0) for row in attempted),
            "estimated_credits": sum(estimates) if all(value is not None for value in estimates) else None,
            "minimum_credits": sum(row["credits"]["minimum"] for row in attempted)
            if all(row["credits"]["minimum"] is not None for row in attempted) else None,
            "maximum_credits": sum(row["credits"]["maximum"] for row in attempted)
            if all(row["credits"]["maximum"] is not None for row in attempted) else None,
            "child_followups": sum(row.get("child_followups", 0) for row in attempted),
            "repairs": sum(row.get("repair_count") or 0 for row in attempted),
            "repairs_unknown": sum(row.get("repair_count") is None for row in attempted),
            "astra_escalations": sum(row.get("astra_escalations", 0) for row in attempted),
        }
    bootstrap = paired_bootstrap(records)
    reasons = []
    expected = 24 * 3
    if any(totals[arm]["runs"] != expected for arm in ("terra", "luna")) or completeness["missing_runs"]:
        reasons.append("fewer than 24 tasks x 3 repeats per arm")
    if any(row.get("critical_defect") for row in records):
        reasons.append("critical acceptance defect")
    if any(totals[arm]["unknown_costs"] for arm in ("terra", "luna")):
        reasons.append("route credits incomplete")
    if bootstrap["interval_95"] is None or bootstrap["interval_95"][0] <= 0:
        reasons.append("score advantage not established")
    if bootstrap.get("quality_interval_95") is None or bootstrap["quality_interval_95"][0] < -0.05:
        reasons.append("quality non-inferiority not established")
    pessimistic = bounds["luna_pessimistic"]
    if pessimistic["luna"] is None or pessimistic["terra"] is None or pessimistic["luna"] <= pessimistic["terra"]:
        reasons.append("ranking changes under unknown tier")
    return {"completeness": completeness, "totals": totals, "paired": paired, "bootstrap": bootstrap, "tier_bounds": bounds,
            "recommendation": "consider_luna_default" if not reasons else "retain_current_default",
            "recommendation_reasons": reasons}
