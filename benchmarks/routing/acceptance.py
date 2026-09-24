#!/usr/bin/env python3
"""External, data-driven acceptance kept outside each agent workspace."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def python_results(workspace: Path, cases: list[dict]) -> list[dict]:
    sys.path.insert(0, str(workspace))
    spec = importlib.util.spec_from_file_location("benchmark_solution", workspace / "solution.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    found = []
    for case in cases:
        try:
            args = deepcopy(case.get("args", []))
            original = deepcopy(args)
            value = getattr(module, case.get("function", "solve"))(*args)
            result = {"value": value}
            if case.get("input_unchanged"):
                result["input_unchanged"] = args == original
            found.append(result)
        except Exception as exc:
            found.append({"error": type(exc).__name__})
    return found


def node_results(workspace: Path, cases: list[dict]) -> list[dict]:
    code = """
import { pathToFileURL } from 'node:url';
let input=''; for await (const chunk of process.stdin) input += chunk;
const mod = await import(pathToFileURL(process.argv[1]).href);
const out=[];
for (const item of JSON.parse(input)) {
  try { out.push({value: await mod[item.function || 'solve'](...(item.args || []))}); }
  catch (e) { out.push({error: e.constructor.name}); }
}
process.stdout.write(JSON.stringify(out));
"""
    result = subprocess.run(
        ["node", "--input-type=module", "-e", code, str(workspace / "solution.mjs")],
        input=json.dumps(cases), text=True, capture_output=True, timeout=30,
    )
    if result.returncode:
        raise RuntimeError(result.stderr[:1000])
    return json.loads(result.stdout)


def cli_results(workspace: Path, cases: list[dict]) -> list[dict]:
    found = []
    for case in cases:
        result = subprocess.run(
            [sys.executable, "-B", str(workspace / "tool.py"), *case.get("argv", [])],
            input=json.dumps(case.get("stdin")), text=True, capture_output=True, timeout=15,
            env={**__import__("os").environ, **case.get("env", {})},
        )
        try:
            value = json.loads(result.stdout)
        except json.JSONDecodeError:
            value = result.stdout.strip()
        found.append({"value": value, "exit": result.returncode})
    return found


def review_results(workspace: Path, cases: list[dict]) -> list[dict]:
    path = workspace / "REVIEW.md"
    content = path.read_text() if path.is_file() else ""
    # A finding may contain a heading and several paragraphs. Keep those together
    # while preventing unrelated findings from satisfying one rubric item.
    findings = [part.lower() for part in re.split(
        r"(?m)^(?:\s*#{2,6}\s+|\s*(?:\d+[.)]|[-*])\s+)", content
    ) if part.strip()]
    found = []
    for case in cases:
        groups = case.get("term_groups", [[term] for term in case["terms"]])
        matched = any(
            all(any(term.lower() in part for term in group) for group in groups)
            and re.search(r"\b\d+\b", part)
            for part in findings
        )
        found.append({"value": bool(matched)})
    return found


def main() -> int:
    workspace = Path(sys.argv[1]).resolve()
    task_id = sys.argv[2]
    checks = json.loads((ROOT / "fixtures" / task_id / "checks.json").read_text())
    cases = checks["cases"]
    mode = checks["mode"]
    try:
        found = {"python": python_results, "node": node_results, "cli": cli_results, "review": review_results}[mode](workspace, cases)
        infrastructure_error = None
    except Exception as exc:
        found = []
        infrastructure_error = f"{type(exc).__name__}: {exc}"
    failures = []
    baseline_passed = 0
    for index, case in enumerate(cases):
        actual = found[index] if index < len(found) else None
        expected = case["expected"]
        if actual != expected:
            failures.append(case["name"])
        elif case.get("baseline"):
            baseline_passed += 1
    result = {
        "task_id": task_id, "passed": len(failures) == 0 and infrastructure_error is None,
        "failed_checks": failures, "baseline_passed": baseline_passed,
        "environment_ok": infrastructure_error is None,
        "infrastructure_error": infrastructure_error,
        "critical_defect": any(case.get("critical") and case["name"] in failures for case in cases),
    }
    print("BENCH_RESULT: " + json.dumps(result, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
