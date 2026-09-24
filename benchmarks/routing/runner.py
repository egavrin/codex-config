#!/usr/bin/env python3
"""Run public routing fixtures in fresh, isolated Codex CLI sessions."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if __package__:
    from .analysis import load_records, report, route_credits, load_prices
    from .rollouts import collect_rollouts
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from routing.analysis import load_records, report, route_credits, load_prices  # type: ignore
    from routing.rollouts import collect_rollouts  # type: ignore

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ARMS = json.loads((HERE / "profiles" / "arms.json").read_text())
MANIFEST = HERE / "tasks.json"
ARTIFACTS = HERE / "artifacts"
SESSIONS = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "sessions"
CODEX_HOME = SESSIONS.parent


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def tree_hash(directory: Path) -> str:
    digest = hashlib.sha256()
    files = sorted(path for path in directory.rglob("*") if path.is_file() and ".git" not in path.parts)
    for path in files:
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        digest.update(str(path.relative_to(directory)).encode())
        digest.update(hash_file(path).encode())
    return digest.hexdigest()


def safe_json(value: Any) -> Any:
    """Represent missing numeric comparisons as JSON null."""
    import math

    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: safe_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe_json(item) for item in value]
    return value


def tasks() -> list[dict[str, Any]]:
    data = json.loads(MANIFEST.read_text())
    found = data["tasks"]
    if len({task["id"] for task in found}) != len(found):
        raise ValueError("duplicate task id")
    for task in found:
        source = HERE / task["source"]
        external = HERE / task["acceptance"]
        checks = HERE / task["checks"]
        if not source.is_dir() or not external.is_file() or not checks.is_file():
            raise ValueError(f"missing fixture files: {task['id']}")
        if (tree_hash(source) != task["source_sha256"] or hash_file(external) != task["acceptance_sha256"]
                or hash_file(checks) != task["checks_sha256"]):
            raise ValueError(f"fixture hash changed: {task['id']}")
    return found


def _git(workspace: Path, *args: str, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(["git", *args], cwd=workspace, env=env, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def prepare_workspace(task: dict[str, Any], target: Path) -> str:
    shutil.copytree(HERE / task["source"], target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".git"))
    _git(target, "init", "-q")
    _git(target, "add", "-A")
    env = os.environ.copy()
    env.update({"GIT_AUTHOR_DATE": "2026-09-23T00:00:00+00:00", "GIT_COMMITTER_DATE": "2026-09-23T00:00:00+00:00"})
    _git(target, "-c", "user.name=Routing Benchmark", "-c", "user.email=routing@local.invalid", "commit", "-q", "-m", "fixture seed", env=env)
    return _git(target, "rev-parse", "HEAD")


def profile_hash() -> str:
    digest = hashlib.sha256()
    for path in sorted((HERE / "profiles").iterdir()):
        digest.update(path.name.encode())
        digest.update(hash_file(path).encode())
    return digest.hexdigest()


def cycle_metadata() -> dict[str, Any]:
    return {
        "manifest_sha256": hash_file(MANIFEST),
        "profile_sha256": profile_hash(),
        "price_sha256": hash_file(HERE / "prices.json"),
        "runner_sha256": hash_file(HERE / "runner.py"),
        "rollout_importer_sha256": hash_file(HERE / "rollouts.py"),
        "active_config_sha256": hash_file(CODEX_HOME / "config.toml") if (CODEX_HOME / "config.toml").is_file() else None,
        "active_agents_sha256": hash_file(CODEX_HOME / "AGENTS.md") if (CODEX_HOME / "AGENTS.md").is_file() else None,
        "codex_version": subprocess.run(["codex", "--version"], capture_output=True, text=True).stdout.strip(),
    }


def codex_command(workspace: Path, arm: str, prompt: str) -> list[str]:
    config = ARMS[arm]
    fast = config["tier"] == "fast"
    # Explicit overrides avoid inheriting the active model, effort, tier, or old Sol role.
    return [
        "codex", "exec", "--json", "--skip-git-repo-check", "-C", str(workspace),
        "-m", config["model"],
        "-c", f'model_reasoning_effort="{config["effort"]}"',
        "-c", f'service_tier="{config["tier"]}"',
        "-c", f'features.fast_mode={str(fast).lower()}',
        "-c", "features.multi_agent=true",
        "-c", "agents.max_concurrent_threads_per_session=3",
        "-c", f'agents.senior_executor_standard.config_file="{HERE / "profiles" / "sol6.toml"}"',
        "-c", f'agents.astra_executor_standard.config_file="{HERE / "profiles" / "astra6.toml"}"',
        "-c", 'agents.default_subagent_model="gpt-6-sol"',
        "-c", 'agents.default_subagent_reasoning_effort="medium"',
        "-c", "notify=[]",
        prompt,
    ]


def run_check(command: list[str], cwd: Path, timeout: int, output: Path) -> dict[str, Any]:
    start = time.monotonic()
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        content = result.stdout + "\n--- stderr ---\n" + result.stderr
        code, timed_out = result.returncode, False
    except subprocess.TimeoutExpired as exc:
        content = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        content += "\n--- timeout ---\n"
        code, timed_out = None, True
    output.write_text(content)
    bench_result = None
    for line in content.splitlines():
        if line.startswith("BENCH_RESULT:"):
            try:
                bench_result = json.loads(line.removeprefix("BENCH_RESULT:").strip())
            except json.JSONDecodeError:
                pass
    return {"exit_code": code, "timed_out": timed_out, "elapsed_seconds": time.monotonic() - start,
            "critical_defect": bool(bench_result and bench_result.get("critical_defect")), "bench_result": bench_result}


def runtime_issue(events: Path) -> str | None:
    """Identify a known unresolved wait from events without reading private text."""
    pending: set[str] = set()
    for line in events.read_text(errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item")
        if not isinstance(item, dict):
            continue
        if event.get("type") == "item.started" and item.get("type") == "collab_tool_call":
            if item.get("tool") == "wait" and item.get("receiver_thread_ids") == []:
                pending.add(item.get("id"))
        elif event.get("type") == "item.completed":
            pending.discard(item.get("id"))
    return "unresolved_empty_collaboration_wait" if pending else None


def run_one(task: dict[str, Any], arm: str, repeat: int, cycle: Path, timeout_override: int | None = None) -> dict[str, Any]:
    case_id = f'{task["id"]}--{arm}--{repeat}'
    case_dir = cycle / case_id
    case_dir.mkdir(parents=True)
    workspace = case_dir / "workspace"
    seed_commit = prepare_workspace(task, workspace)
    if seed_commit != task["base_commit"]:
        raise ValueError(f"seed commit drift: {task['id']}")
    prompt_path = workspace / "PROMPT.md"
    prompt = prompt_path.read_text()
    protected = {name: hash_file(workspace / name) for name in task["protected"]}
    argv = codex_command(workspace, arm, prompt)
    timeout = timeout_override or task["timeout_seconds"]
    started = datetime.now(timezone.utc)
    before = time.monotonic()
    with (case_dir / "codex.stdout.jsonl").open("w") as stdout, (case_dir / "codex.stderr.txt").open("w") as stderr:
        process = subprocess.Popen(argv, cwd=workspace, stdout=stdout, stderr=stderr, text=True, start_new_session=True)
        try:
            exit_code = process.wait(timeout=timeout)
            timed_out = False
        except KeyboardInterrupt:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=5)
            raise
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            exit_code, timed_out = None, True
    elapsed = time.monotonic() - before
    ended = datetime.now(timezone.utc)
    assessment = run_check(
        [sys.executable, "-B", str(HERE / task["acceptance"]), str(workspace), task["id"]],
        workspace, task["acceptance_timeout_seconds"], case_dir / "acceptance.txt",
    )
    protected_ok = protected == {name: hash_file(workspace / name) for name in task["protected"]}
    telemetry = collect_rollouts(SESSIONS, workspace, started, ended)
    sessions = telemetry["sessions"]
    children = [s for s in sessions if s["session_id"] != telemetry["root_session_id"]]
    root = next((s for s in sessions if s["session_id"] == telemetry["root_session_id"]), None)
    sol_children = [s for s in children if s["model"] == "gpt-6-sol"]
    route = "unknown" if root is None else "delegated" if sol_children else "fallback" if task["expected_route"] == "delegated" else "direct"
    status = "timeout" if timed_out else "error" if exit_code != 0 else "complete"
    if root and root["model"] != ARMS[arm]["model"]:
        status = "model_mismatch"
    record = {
        "task_id": task["id"], "category": task["category"], "language": task["language"],
        "arm": arm, "repeat": repeat, "calibration": task.get("calibration", False),
        "source_sha256": task["source_sha256"], "prompt_sha256": hash_file(prompt_path),
        "profile_sha256": profile_hash(), "seed_commit": seed_commit,
        "codex_version": subprocess.run(["codex", "--version"], capture_output=True, text=True).stdout.strip(),
        "arm_config": ARMS[arm], "started_at": started.isoformat(), "ended_at": ended.isoformat(),
        "elapsed_seconds": elapsed, "exit_code": exit_code, "status": status,
        "runtime_issue": runtime_issue(case_dir / "codex.stdout.jsonl"),
        "timeout_seconds": timeout,
        "expected_route": task["expected_route"], "route_observed": route,
        "sol_child_count": len(sol_children), "astra_escalations": sum(s["model"] == "gpt-6-astra" for s in children),
        "child_followups": sum(max(0, s["turn_count"] - 1) for s in children),
        "repair_count": None, "telemetry": telemetry,
        "protected_unchanged": protected_ok, "acceptance": assessment,
        "accepted": status == "complete" and protected_ok and assessment["exit_code"] == 0 and not assessment["critical_defect"],
        "critical_defect": assessment["critical_defect"],
        "workspace": str(workspace),
    }
    record["credits"] = route_credits(record, load_prices())
    (case_dir / "record.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record


def schedule(selected: list[dict[str, Any]], repeats: int, arm_filter: str | None = None) -> list[tuple[dict[str, Any], str, int]]:
    planned = []
    for index, task in enumerate(selected):
        for repeat in range(1, repeats + 1):
            order = ("terra", "luna") if (index + repeat) % 2 else ("luna", "terra")
            planned.extend((task, arm, repeat) for arm in order if arm_filter is None or arm == arm_filter)
    return planned


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("list", "self-check", "dry-run", "run", "analyze", "verify"))
    parser.add_argument("--task", action="append", help="Run or inspect selected task IDs")
    parser.add_argument("--arm", choices=("terra", "luna"), help="Optional one-arm fixture trial")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--timeout", type=int, help="Override per-task timeout for a fixture trial")
    parser.add_argument("--cycle", type=Path, help="Existing or new artifact cycle directory")
    args = parser.parse_args()
    selected = [task for task in tasks() if not args.task or task["id"] in args.task]
    if args.action == "list":
        for task in selected:
            print(task["id"], task["category"], task["language"])
        return 0
    if args.action == "self-check":
        failed = []
        for task in selected:
            temp = ARTIFACTS / "self-check" / task["id"]
            if temp.exists():
                shutil.rmtree(temp)
            temp.parent.mkdir(parents=True, exist_ok=True)
            prepare_workspace(task, temp)
            result = run_check([sys.executable, "-B", str(HERE / task["acceptance"]), str(temp), task["id"]], temp, task["acceptance_timeout_seconds"], temp.parent / f'{task["id"]}.txt')
            bench = result["bench_result"] or {}
            if result["exit_code"] == 0 or result["timed_out"] or not bench.get("environment_ok") or (task["category"] != "review" and bench.get("baseline_passed", 0) == 0):
                failed.append(task["id"])
        print(json.dumps({"checked": len(selected), "unexpected_pass_or_timeout": failed}))
        return bool(failed)
    if args.action == "dry-run":
        print(json.dumps([(task["id"], arm, repeat) for task, arm, repeat in schedule(selected, args.repeats, args.arm)]))
        return 0
    cycle = args.cycle or ARTIFACTS / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if args.action == "run":
        cycle.mkdir(parents=True, exist_ok=True)
        meta_path = cycle / "cycle-meta.json"
        metadata = cycle_metadata()
        if meta_path.exists():
            if json.loads(meta_path.read_text()) != metadata:
                raise ValueError("benchmark profile, pricing, fixture, Codex version, or active instructions changed during cycle")
        else:
            meta_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
        failures = {arm: 0 for arm in ARMS}
        repeated_waits = 0
        for task, arm, repeat in schedule(selected, args.repeats, args.arm):
            skip_reason = (
                "repeated unresolved empty collaboration waits" if repeated_waits >= 2 and task["expected_route"] == "delegated"
                else "three consecutive runtime failures for arm" if failures[arm] >= 3 else None
            )
            if skip_reason:
                row = {"task_id": task["id"], "category": task["category"], "language": task["language"],
                       "arm": arm, "repeat": repeat, "calibration": task.get("calibration", False),
                       "status": "skipped", "accepted": False, "failure_reason": skip_reason,
                       "expected_route": task["expected_route"], "route_observed": "unknown",
                       "arm_config": ARMS[arm], "elapsed_seconds": 0, "telemetry": {"sessions": []}}
                with (cycle / "results.jsonl").open("a") as stream:
                    stream.write(json.dumps(row, sort_keys=True) + "\n")
                print(json.dumps({"task_id": task["id"], "arm": arm, "repeat": repeat,
                                  "status": "skipped", "reason": skip_reason}), flush=True)
                continue
            case_dir = cycle / f'{task["id"]}--{arm}--{repeat}'
            if case_dir.exists():
                print(f"existing case: {case_dir}", file=sys.stderr)
                return 2
            row = run_one(task, arm, repeat, cycle, args.timeout)
            with (cycle / "results.jsonl").open("a") as stream:
                stream.write(json.dumps(row, sort_keys=True) + "\n")
            failures[arm] = failures[arm] + 1 if row["status"] in {"timeout", "error", "model_mismatch"} else 0
            if row["runtime_issue"] == "unresolved_empty_collaboration_wait":
                repeated_waits += 1
            print(json.dumps({k: row[k] for k in ("task_id", "arm", "repeat", "status", "accepted", "route_observed")}), flush=True)
        return 0
    if not (cycle / "results.jsonl").exists():
        parser.error("cycle has no results.jsonl")
    rows = load_records(cycle / "results.jsonl")
    if args.action == "analyze":
        summary = report(rows)
        print(json.dumps(safe_json(summary), indent=2, sort_keys=True, allow_nan=False))
        return 0
    failed = []
    index = {task["id"]: task for task in selected}
    for row in rows:
        if row["task_id"] not in index or row["status"] == "skipped":
            continue
        task = index[row["task_id"]]
        workspace = Path(row["workspace"])
        result = run_check([sys.executable, "-B", str(HERE / task["acceptance"]), str(workspace), task["id"]], workspace, task["acceptance_timeout_seconds"], cycle / f'verify-{row["task_id"]}--{row["arm"]}--{row["repeat"]}.txt')
        if (result["exit_code"] == 0) != (row["acceptance"]["exit_code"] == 0):
            failed.append((row["task_id"], row["arm"], row["repeat"]))
    print(json.dumps({"rechecked": len(rows) - sum(row["status"] == "skipped" for row in rows), "mismatches": failed}))
    return bool(failed)


if __name__ == "__main__":
    raise SystemExit(main())
