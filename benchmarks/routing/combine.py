#!/usr/bin/env python3
"""Combine pinned non-review and review cycles after a review-rubric correction."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from benchmarks.routing.analysis import load_records, report
from benchmarks.routing.runner import HERE, hash_file, run_check, safe_json, tasks


def combine(non_review: Path, review: Path, output: Path) -> dict:
    first_meta = json.loads((non_review / "cycle-meta.json").read_text())
    second_meta = json.loads((review / "cycle-meta.json").read_text())
    stable = ("profile_sha256", "price_sha256", "runner_sha256", "rollout_importer_sha256",
              "active_agents_sha256", "codex_version")
    differences = [field for field in stable if first_meta.get(field) != second_meta.get(field)]
    if differences:
        raise ValueError(f"cycles differ in pinned execution settings: {differences}")
    if first_meta["manifest_sha256"] == second_meta["manifest_sha256"]:
        raise ValueError("expected a documented review-rubric amendment")
    first = [row for row in load_records(non_review / "results.jsonl") if row["category"] != "review"]
    second = [row for row in load_records(review / "results.jsonl") if row["category"] == "review"]
    selected = first + second
    manifest = {task["id"]: task for task in tasks()}
    expected = {(task_id, arm, repeat) for task_id in manifest for arm in ("terra", "luna")
                for repeat in range(1, 4)}
    observed = [(row["task_id"], row["arm"], row["repeat"]) for row in selected]
    if len(selected) != 144 or len(set(observed)) != 144 or set(observed) != expected:
        raise ValueError(f"incomplete or duplicate matrix: {len(selected)} rows, {len(set(observed))} unique")
    output.mkdir(parents=True, exist_ok=False)
    verified = []
    changed_grades = []
    for row in selected:
        task = manifest[row["task_id"]]
        prompt = HERE / task["source"] / "PROMPT.md"
        if row["source_sha256"] != task["source_sha256"] or row["prompt_sha256"] != hash_file(prompt):
            raise ValueError(f"source or prompt drift for {row['task_id']}")
        if row["profile_sha256"] != first_meta["profile_sha256"]:
            raise ValueError(f"profile drift for {row['task_id']}")
        workspace = Path(row["workspace"])
        if not workspace.is_dir():
            raise ValueError(f"missing local workspace for {row['task_id']}")
        check = run_check(
            [__import__("sys").executable, "-B", str(HERE / task["acceptance"]),
             str(workspace), task["id"]],
            workspace, task["acceptance_timeout_seconds"],
            output / f"verify-{row['task_id']}--{row['arm']}--{row['repeat']}.txt",
        )
        old_passed = row["acceptance"]["exit_code"] == 0
        new_passed = check["exit_code"] == 0
        if row["category"] != "review" and new_passed != old_passed:
            raise ValueError(f"non-review acceptance changed for {row['task_id']} {row['arm']} {row['repeat']}")
        if row["category"] == "review":
            row["original_acceptance"] = row["acceptance"]
            row["original_accepted"] = row["accepted"]
            row["acceptance"] = check
            row["critical_defect"] = check["critical_defect"]
            row["accepted"] = (row["status"] == "complete" and row["protected_unchanged"]
                               and new_passed and not check["critical_defect"])
            if old_passed != new_passed or row["original_accepted"] != row["accepted"]:
                changed_grades.append({"run": [row["task_id"], row["arm"], row["repeat"]],
                                       "original_accepted": row["original_accepted"],
                                       "final_accepted": row["accepted"]})
        verified.append([row["task_id"], row["arm"], row["repeat"]])
    selected.sort(key=lambda row: (row["task_id"], row["repeat"], row["arm"]))
    with (output / "results.jsonl").open("w") as stream:
        for row in selected:
            stream.write(json.dumps(row, sort_keys=True) + "\n")
    provenance = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "non_review_cycle": str(non_review.resolve()),
        "review_cycle": str(review.resolve()),
        "non_review_count": len(first), "review_count": len(second),
        "rechecked": len(verified),
        "reason": "The initial review rubric rejected valid database-error wording. Review tasks were rerun with amended wording. Final grading also accepts two valid paraphrases in the CLI and fetch reviews, and splits Markdown findings to avoid cross-finding matches. The final checker was applied uniformly to all 144 saved workspaces. Original review grades remain in each composite record; raw cycle records were not altered.",
        "changed_grades": changed_grades,
        "active_config_drift": first_meta.get("active_config_sha256") != second_meta.get("active_config_sha256"),
        "active_config_drift_limit": "The global config hash changed between cycles. Pinned experiment profile, runner, agent guidance, pricing and Codex version match, and the runner explicitly overrides route models, efforts and tiers. Other inherited global settings cannot be reconstructed from hashes alone.",
        "first_cycle_meta": first_meta,
        "second_cycle_meta": second_meta,
        "current_manifest_sha256": hash_file(HERE / "tasks.json"),
    }
    (output / "provenance.json").write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n")
    summary = safe_json(report(selected))
    (output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n")
    return {"combined": len(selected), "rechecked": len(verified),
            "changed_grades": len(changed_grades),
            "recommendation": summary["recommendation"], "output": str(output)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--non-review", required=True, type=Path)
    parser.add_argument("--review", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(combine(args.non_review, args.review, args.output), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
