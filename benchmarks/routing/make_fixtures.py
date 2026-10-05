#!/usr/bin/env python3
"""Materialize the reviewed, public synthetic benchmark catalog."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from benchmarks.routing.runner import HERE, hash_file, prepare_workspace, tree_hash

SPECS: list[dict] = []


def add(identifier: str, category: str, language: str, objective: str, files: dict[str, str], cases: list[dict], *, mode: str | None = None) -> None:
    prompt = (
        f"# Task {identifier}\n\n{objective.strip()}\n\n"
        "Work only in this repository. Preserve existing behavior outside the request. "
        "You may inspect and edit production files, but do not modify PROMPT.md. "
        "Use the repository's normal Codex routing policy and run a focused check.\n"
    )
    if category in {"multi", "diagnosis", "security"}:
        prompt += (
            "For this routing benchmark, delegate the bounded implementation to exactly one "
            "senior_executor_standard (GPT-6 Sol Medium Standard). Independently inspect and "
            "accept the result. If native delegation is unavailable, finish the task directly "
            "and report the fallback.\n"
        )
    if category == "review":
        prompt = (
            f"# Task {identifier}\n\n{objective.strip()}\n\n"
            "This is a read-only review. Do not edit production code. Write actionable findings "
            "with file and line references in REVIEW.md; do not modify PROMPT.md. "
            "Delegate one bounded read-only review package to senior_executor_standard "
            "(GPT-6 Sol Medium Standard), then independently accept its findings. "
            "If native delegation is unavailable, finish the review directly and report the fallback.\n"
        )
    SPECS.append({"id": identifier, "category": category, "language": language, "prompt": prompt,
                  "files": files, "cases": cases, "mode": mode or {"Python": "python", "TypeScript": "node", "config/CLI": "cli"}[language]})


def value(name: str, args: list, expected, *, baseline: bool = False, critical: bool = False,
          unchanged: bool = False, function: str = "solve") -> dict:
    result = {"name": name, "function": function, "args": args, "expected": {"value": expected},
              "baseline": baseline, "critical": critical}
    if unchanged:
        result["input_unchanged"] = True
        result["expected"]["input_unchanged"] = True
    return result


def cli(name: str, expected, *, argv: list[str] | None = None, stdin=None, env: dict | None = None, baseline: bool = False) -> dict:
    return {"name": name, "argv": argv or [], "stdin": stdin, "env": env or {},
            "expected": {"value": expected, "exit": 0}, "baseline": baseline}


def finding(name: str, *terms: str | tuple[str, ...], critical: bool = False) -> dict:
    return {"name": name, "terms": [], "term_groups": [[term] if isinstance(term, str) else list(term)
            for term in terms], "expected": {"value": True}, "critical": critical}


# Four direct tasks: bounded, local changes that should not need delegation.
add("direct-size-parser", "direct", "Python",
    "Parse storage sizes. Accept plain nonnegative byte counts, and case-insensitive K/M/G suffixes with surrounding whitespace. Reject negative values.",
    {"solution.py": '''def solve(raw):
    units = {"K": 1024, "M": 1024 ** 2, "G": 1024 ** 3}
    return int(raw[:-1]) * units[raw[-1]]
'''}, [
        value("existing K", ["2K"], 2048, baseline=True),
        value("lowercase and spaces", [" 3m "], 3145728),
        value("plain bytes", ["512"], 512),
        {"name": "negative rejected", "args": ["-2K"], "expected": {"error": "ValueError"}},
    ])

add("direct-route-path", "direct", "TypeScript",
    "Normalize an HTTP path by collapsing repeated slashes and removing trailing slashes, except for root. Preserve the query string exactly.",
    {"solution.mjs": '''export function solve(path) {
  return path.replace(/\\/+$/, '') || '/';
}
'''}, [
        value("existing trailing slash", ["/api/"], "/api", baseline=True),
        value("duplicate separators", ["/api//v1///users/"], "/api/v1/users"),
        value("query preserved", ["/a//b/?q=x//y"], "/a/b?q=x//y"),
        value("root", ["////"], "/"),
    ])

add("direct-config-defaults", "direct", "Python",
    "Merge default configuration with explicit user values. Explicit values, including zero, false and empty strings, take precedence. Return a new dictionary.",
    {"solution.py": '''def solve(defaults, user):
    result = dict(user)
    result.update(defaults)
    return result
'''}, [
        value("no override", [{"threads": 4}, {}], {"threads": 4}, baseline=True),
        value("zero override", [{"threads": 4}, {"threads": 0}], {"threads": 0}),
        value("false and empty override", [{"enabled": True, "label": "x"}, {"enabled": False, "label": ""}], {"enabled": False, "label": ""}),
        value("defaults unchanged", [{"a": 1}, {"b": 2}], {"a": 1, "b": 2}),
    ])

add("direct-limit-flag", "direct", "config/CLI",
    "Read a JSON list from stdin and emit its first N items as JSON. --limit 0 must produce an empty list; negative limits must also produce an empty list.",
    {"tool.py": '''import argparse
import json
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--limit", type=int, default=None)
args = parser.parse_args()
items = json.load(sys.stdin)
print(json.dumps(items[:args.limit] if args.limit else items))
'''}, [
        cli("positive limit", [1, 2], argv=["--limit", "2"], stdin=[1, 2, 3], baseline=True),
        cli("zero limit", [], argv=["--limit", "0"], stdin=[1, 2, 3]),
        cli("negative limit", [], argv=["--limit", "-1"], stdin=[1, 2, 3]),
        cli("unlimited", [1, 2], stdin=[1, 2]),
    ])


# Four local implementation tasks.
add("local-intervals", "local", "Python",
    "Merge overlapping or touching closed integer intervals. Return sorted [start, end] pairs and do not mutate input.",
    {"solution.py": '''def solve(intervals):
    result = []
    for start, end in sorted(intervals):
        if result and start < result[-1][1]:
            result[-1][1] = max(result[-1][1], end)
        else:
            result.append([start, end])
    return result
'''}, [
        value("overlap", [[[1, 4], [3, 7]]], [[1, 7]], baseline=True),
        value("touching", [[[1, 3], [3, 5]]], [[1, 5]]),
        value("unsorted chain, input preserved", [[[5, 8], [1, 2], [2, 5]]], [[1, 8]], unchanged=True),
        value("empty", [[]], []),
    ])

add("local-utc-buckets", "local", "TypeScript",
    "Count ISO timestamp strings by UTC calendar day. Offset timestamps must be converted to UTC before grouping. Return an object sorted by day key.",
    {"solution.mjs": '''export function solve(timestamps) {
  const counts = {};
  for (const stamp of timestamps) {
    const day = stamp.slice(0, 10);
    counts[day] = (counts[day] || 0) + 1;
  }
  return Object.fromEntries(Object.entries(counts).sort());
}
'''}, [
        value("UTC baseline", [["2026-09-23T12:00:00Z"]], {"2026-09-23": 1}, baseline=True),
        value("offset crosses midnight", [["2026-09-23T23:30:00-02:00"]], {"2026-09-24": 1}),
        value("same UTC day", [["2026-09-23T23:30:00-02:00", "2026-09-24T01:30:00Z"]], {"2026-09-24": 2}),
    ])

add("local-csv-row", "local", "Python",
    "Parse one CSV row according to ordinary CSV quoting rules. Preserve empty fields and support commas and doubled quotes within quoted fields.",
    {"solution.py": '''def solve(row):
    return row.split(",")
'''}, [
        value("simple", ["a,b,c"], ["a", "b", "c"], baseline=True),
        value("quoted comma", ['a,"b,c",d'], ["a", "b,c", "d"]),
        value("escaped quote", ['"a""b",c'], ['a"b', "c"]),
        value("empty fields", [",x,"], ["", "x", ""]),
    ])

add("local-config-precedence", "local", "config/CLI",
    "Read JSON config from stdin with defaults and a file layer. Apply an optional THREADS environment value and --threads CLI value. CLI > environment > file > defaults; zero is valid.",
    {"tool.py": '''import argparse
import json
import os
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--threads', type=int)
args = parser.parse_args()
data = json.load(sys.stdin)
threads = data.get('file', {}).get('threads') or data['defaults']['threads']
threads = os.getenv('THREADS') or threads
threads = args.threads or threads
print(json.dumps({'threads': int(threads)}))
'''}, [
        cli("file layer", {"threads": 3}, stdin={"defaults": {"threads": 4}, "file": {"threads": 3}}, baseline=True),
        cli("file zero", {"threads": 0}, stdin={"defaults": {"threads": 4}, "file": {"threads": 0}}),
        cli("environment zero", {"threads": 0}, stdin={"defaults": {"threads": 4}}, env={"THREADS": "0"}),
        cli("CLI zero", {"threads": 0}, argv=["--threads", "0"], stdin={"defaults": {"threads": 4}}, env={"THREADS": "2"}),
    ])


# Four changes across connected modules.
add("multi-checkout-tax", "multi", "Python",
    "Apply a percentage discount to the subtotal before tax. The pricing and checkout modules form one contract; return the final integer cents after rounding half up.",
    {"pricing.py": '''from decimal import Decimal, ROUND_HALF_UP

def percent(value, rate):
    return int((Decimal(value) * Decimal(rate) / 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
''',
     "solution.py": '''from pricing import percent

def solve(subtotal_cents, discount_percent, tax_percent):
    tax = percent(subtotal_cents, tax_percent)
    discount = percent(subtotal_cents, discount_percent)
    return subtotal_cents + tax - discount
'''}, [
        value("no discount", [1000, 0, 10], 1100, baseline=True),
        value("discount before tax", [1000, 20, 10], 880),
        value("non-round subtotal", [999, 10, 10], 989),
    ])

add("multi-reservation-count", "multi", "TypeScript",
    "Compute remaining inventory from reservation records. Each reservation ID counts once using its latest state; cancelled reservations consume no stock. Reject over-reservation by returning null.",
    {"reservations.mjs": '''export function consumed(rows) {
  return rows.filter(r => r.state !== 'cancelled').reduce((n, r) => n + r.quantity, 0);
}
''',
     "solution.mjs": '''import { consumed } from './reservations.mjs';
export function solve(stock, reservations) {
  const left = stock - consumed(reservations);
  return left < 0 ? null : left;
}
'''}, [
        value("unique reservations", [10, [{"id": "a", "quantity": 3, "state": "active"}]], 7, baseline=True),
        value("latest state wins", [10, [{"id": "a", "quantity": 3, "state": "active"}, {"id": "a", "quantity": 3, "state": "cancelled"}]], 10),
        value("duplicate event", [10, [{"id": "a", "quantity": 3, "state": "active"}, {"id": "a", "quantity": 3, "state": "active"}]], 7),
        value("over reservation", [2, [{"id": "a", "quantity": 3, "state": "active"}]], None),
    ])

add("multi-markup-render", "multi", "Python",
    "Parse a title|body record and render both fields as escaped HTML text. A literal pipe belongs to the body after the first separator. Return one h1 and one p element.",
    {"parser.py": '''def parse(record):
    return record.split('|', 1)
''',
     "renderer.py": '''from html import escape

def render(title, body):
    return f'<h1>{escape(title)}</h1><p>{body}</p>'
''',
     "solution.py": '''from parser import parse
from renderer import render

def solve(record):
    return render(*parse(record))
'''}, [
        value("plain", ["Title|Body"], "<h1>Title</h1><p>Body</p>", baseline=True),
        value("escape body", ["T|<script>x</script>"], "<h1>T</h1><p>&lt;script&gt;x&lt;/script&gt;</p>", critical=True),
        value("pipe in body", ["A|B|C"], "<h1>A</h1><p>B|C</p>"),
    ])

add("multi-cache-expiry", "multi", "TypeScript",
    "Return active cache keys in insertion order. An entry expires when now >= createdAt + ttl, and a later write of the same key replaces its earlier record.",
    {"cache.mjs": '''export function active(entries, now) {
  return entries.filter(e => now - e.createdAt <= e.ttl).map(e => e.key);
}
''',
     "solution.mjs": '''import { active } from './cache.mjs';
export function solve(entries, now) {
  return active(entries, now);
}
'''}, [
        value("not expired", [[{"key": "a", "createdAt": 0, "ttl": 10}], 9], ["a"], baseline=True),
        value("boundary expired", [[{"key": "a", "createdAt": 0, "ttl": 10}], 10], []),
        value("new write replaces old", [[{"key": "a", "createdAt": 0, "ttl": 10}, {"key": "a", "createdAt": 5, "ttl": 10}], 6], ["a"]),
    ])


# Four diagnosis tasks with misleading surface symptoms and a connected cause.
add("diagnosis-retry-budget", "diagnosis", "Python",
    "Return [attempts, succeeded] for an operation that fails N times before succeeding. max_attempts is inclusive, and zero permits no calls. Inspect the retry helper and caller together.",
    {"retry.py": '''def attempt_numbers(max_attempts):
    return range(max_attempts - 1)
''',
     "solution.py": '''from retry import attempt_numbers

def solve(failures, max_attempts):
    count = 0
    for _ in attempt_numbers(max_attempts):
        count += 1
        if count > failures:
            return [count, True]
    return [count, False]
'''}, [
        value("early success", [0, 3], [1, True], baseline=True),
        value("last allowed success", [2, 3], [3, True]),
        value("exhausted", [4, 3], [3, False]),
        value("zero budget", [0, 0], [0, False]),
    ])

add("diagnosis-event-unsubscribe", "diagnosis", "TypeScript",
    "Process subscribe, emit and unsubscribe actions. An unsubscribe removes exactly the named listener; later emits must not call it. Return the sequence of delivered listener names.",
    {"emitter.mjs": '''export class Emitter {
  listeners = [];
  on(name) { this.listeners.push(name); }
  off(name) { this.listeners = this.listeners.filter(item => item === name); }
  emit() { return [...this.listeners]; }
}
''',
     "solution.mjs": '''import { Emitter } from './emitter.mjs';
export function solve(actions) {
  const emitter = new Emitter();
  const delivered = [];
  for (const [kind, name] of actions) {
    if (kind === 'on') emitter.on(name);
    if (kind === 'off') emitter.off(name);
    if (kind === 'emit') delivered.push(...emitter.emit());
  }
  return delivered;
}
'''}, [
        value("ordinary emit", [[['on', 'a'], ['emit', '']]], ["a"], baseline=True),
        value("unsubscribe one", [[['on', 'a'], ['on', 'b'], ['off', 'a'], ['emit', '']]], ["b"]),
        value("unsubscribe all", [[['on', 'a'], ['off', 'a'], ['emit', '']]], []),
    ])

add("diagnosis-version-cache", "diagnosis", "Python",
    "Apply set/get operations to a versioned key-value store and return get results. A set invalidates the cached value for that key without disturbing unrelated keys.",
    {"cache.py": '''class Cache:
    def __init__(self):
        self.values = {}

    def get(self, key, store):
        if key not in self.values:
            self.values[key] = store[key]
        return self.values[key]
''',
     "solution.py": '''from cache import Cache

def solve(initial, operations):
    store = dict(initial)
    cache = Cache()
    result = []
    for operation in operations:
        if operation[0] == 'set':
            store[operation[1]] = operation[2]
        else:
            result.append(cache.get(operation[1], store))
    return result
'''}, [
        value("initial read", [{"a": 1}, [["get", "a"]]], [1], baseline=True),
        value("updated value", [{"a": 1}, [["get", "a"], ["set", "a", 2], ["get", "a"]]], [1, 2]),
        value("unrelated key", [{"a": 1, "b": 5}, [["get", "a"], ["get", "b"], ["set", "a", 2], ["get", "b"]]], [1, 5, 5]),
    ])

add("diagnosis-mode-precedence", "diagnosis", "config/CLI",
    "Resolve mode from --mode, APP_MODE, and JSON stdin config in that order. The CLI option must win even when APP_MODE is set by the environment.",
    {"tool.py": '''import argparse
import json
import os
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--mode')
args = parser.parse_args()
config = json.load(sys.stdin)
print(json.dumps({'mode': os.getenv('APP_MODE') or args.mode or config.get('mode', 'safe')}))
'''}, [
        cli("environment only", {"mode": "fast"}, env={"APP_MODE": "fast"}, stdin={}, baseline=True),
        cli("CLI wins", {"mode": "safe"}, argv=["--mode", "safe"], env={"APP_MODE": "fast"}, stdin={}),
        cli("config fallback", {"mode": "audit"}, stdin={"mode": "audit"}),
    ])


# Four safety and rollback tasks. A known critical failure blocks promotion.
add("security-archive-member", "security", "Python",
    "Given an extraction root and a POSIX archive member name, return the destination path only when the member stays below root. Reject absolute paths, parent traversal, and backslash traversal by returning null.",
    {"solution.py": '''from pathlib import PurePosixPath

def solve(root, member):
    return str(PurePosixPath(root) / member)
'''}, [
        value("safe member", ["/out", "docs/readme.txt"], "/out/docs/readme.txt", baseline=True),
        value("parent traversal", ["/out", "../secret"], None, critical=True),
        value("absolute member", ["/out", "/etc/passwd"], None, critical=True),
        value("backslash traversal", ["/out", "..\\secret"], None, critical=True),
    ])

add("security-redirect-origin", "security", "TypeScript",
    "Accept a redirect URL only when its parsed origin exactly equals the trusted origin and its scheme is HTTPS. Return the accepted URL or null. Relative paths are allowed and resolve against the trusted origin.",
    {"solution.mjs": '''export function solve(trusted, candidate) {
  return candidate.startsWith(trusted) ? candidate : null;
}
'''}, [
        value("trusted absolute", ["https://example.test", "https://example.test/account"], "https://example.test/account", baseline=True),
        value("host prefix attack", ["https://example.test", "https://example.test.evil.invalid/"], None, critical=True),
        value("http rejected", ["https://example.test", "http://example.test/account"], None, critical=True),
        value("relative path", ["https://example.test", "/account"], "https://example.test/account"),
    ])

add("security-atomic-batch", "security", "Python",
    "Apply a sequence of key/value updates as one transaction. Return the resulting dictionary. If fail_at names a zero-based operation index, simulate failure there and return the original dictionary with no partial changes.",
    {"solution.py": '''def solve(initial, updates, fail_at):
    state = dict(initial)
    try:
        for index, (key, value) in enumerate(updates):
            state[key] = value
            if index == fail_at:
                raise RuntimeError('simulated failure')
    except RuntimeError:
        pass
    return state
'''}, [
        value("successful batch", [{"a": 1}, [["a", 2], ["b", 3]], None], {"a": 2, "b": 3}, baseline=True),
        value("failure after first", [{"a": 1}, [["a", 2], ["b", 3]], 0], {"a": 1}, critical=True, unchanged=True),
        value("failure after second", [{"a": 1}, [["a", 2], ["b", 3]], 1], {"a": 1}, critical=True),
        value("empty batch", [{"a": 1}, [], None], {"a": 1}),
    ])

add("security-nested-redaction", "security", "Python",
    "Return a deep copy of a JSON-like record with every value whose key is token, password or secret replaced by [REDACTED], including nested dictionaries and dictionaries inside lists. Do not alter unrelated values.",
    {"solution.py": '''def solve(record):
    return {key: ('[REDACTED]' if key in {'token', 'password', 'secret'} else value)
            for key, value in record.items()}
'''}, [
        value("top-level token", [{"token": "abc", "user": "a"}], {"token": "[REDACTED]", "user": "a"}, baseline=True),
        value("nested token", [{"auth": {"token": "abc"}}], {"auth": {"token": "[REDACTED]"}}, critical=True),
        value("list nested password", [{"users": [{"password": "x"}, {"name": "b"}]}], {"users": [{"password": "[REDACTED]"}, {"name": "b"}]}, critical=True, unchanged=True),
    ])


# Four read-only review tasks. Each seeded diff has distinct actionable findings.
add("review-python-query", "review", "Python",
    "Review candidate.py for correctness, security, and failure visibility. Report only actionable findings with file and line references.",
    {"candidate.py": '''import sqlite3

def list_invoices(db: sqlite3.Connection, user_id: str, sort: str):
    try:
        query = f"SELECT id, amount FROM invoices WHERE user_id = '{user_id}' ORDER BY {sort}"
        return db.execute(query).fetchall()
    except Exception:
        return []
'''}, [
        finding("SQL injection", "candidate.py", "sql", "parameter", critical=True),
        finding("sort allowlist", "candidate.py", "sort", ("allow", "fixed", "map"), critical=True),
        finding("suppressed error", "candidate.py", ("error", "fail", "exception"),
                ("empty", "[]", "suppress", "swallow", "hide")),
    ], mode="review")

add("review-typescript-session", "review", "TypeScript",
    "Review candidate.mjs for user isolation and redirect safety. Report only actionable findings with file and line references.",
    {"candidate.mjs": '''const cache = new Map();

export async function handler(req, store, logger) {
  const user = req.user.id;
  const key = req.params.documentId;
  if (cache.has(key)) return cache.get(key);
  const document = await store.get(key);
  logger.info({ token: req.headers.authorization, documentId: key });
  if (req.query.next) return { redirect: req.query.next };
  cache.set(key, document);
  return document;
}
'''}, [
        finding("cross-user cache", "candidate.mjs", "cache", "user", critical=True),
        finding("token log", "candidate.mjs", "token", "log", critical=True),
        finding("open redirect", "candidate.mjs", "redirect", ("valid", "allow", "trusted", "external"), critical=True),
    ], mode="review")

add("review-cli-cleanup", "review", "config/CLI",
    "Review candidate.sh for safe path handling and error reporting. Report only actionable findings with file and line references.",
    {"candidate.sh": '''#!/bin/sh
set -e
target=$1
root=$2
rm -rf $root/$target
echo cleanup complete
'''}, [
        finding("unquoted path", "candidate.sh", ("quote", "split", "glob"), ("path", "variable"), critical=True),
        finding("traversal", "candidate.sh", ("travers", "escape", "outside"), "root", critical=True),
        finding("missing arguments", "candidate.sh", ("argument", "missing", "empty"),
                ("root", "target", "delete", "rm")),
    ], mode="review")

add("review-typescript-fetch", "review", "TypeScript",
    "Review candidate.mjs for avoidable latency and resource growth. Report only actionable findings with file and line references.",
    {"candidate.mjs": '''export async function dashboard(ids, api) {
  const results = [];
  for (const id of ids) {
    const user = await api.getUser(id);
    const settings = await api.getSettings();
    results.push({ user, settings });
  }
  return results.sort((a, b) => a.user.name.localeCompare(b.user.name));
}
'''}, [
        finding("sequential calls", "candidate.mjs",
                ("sequential", "serial", "one at a time", "each iteration", "before"),
                ("getuser", "user")),
        finding("duplicate settings fetch", "candidate.mjs", "settings", ("once", "repeated", "each")),
    ], mode="review")


def build() -> None:
    root = HERE / "fixtures"
    rows = []
    for spec in SPECS:
        directory = root / spec["id"]
        start = directory / "start"
        start.mkdir(parents=True, exist_ok=True)
        (start / "PROMPT.md").write_text(spec["prompt"])
        for name, content in spec["files"].items():
            (start / name).write_text(content)
        checks = directory / "checks.json"
        checks.write_text(json.dumps({"mode": spec["mode"], "cases": spec["cases"]}, indent=2, sort_keys=True) + "\n")
        with tempfile.TemporaryDirectory(prefix="routing-seed-") as temporary:
            seed_commit = prepare_workspace({"source": str(start.relative_to(HERE))}, Path(temporary) / "workspace")
        rows.append({
            "id": spec["id"], "category": spec["category"], "language": spec["language"],
            "source": str(start.relative_to(HERE)), "checks": str(checks.relative_to(HERE)),
            "acceptance": "acceptance.py", "source_sha256": tree_hash(start),
            "base_commit": seed_commit,
            "checks_sha256": hash_file(checks), "acceptance_sha256": hash_file(HERE / "acceptance.py"),
            "protected": ["PROMPT.md"], "expected_route": "direct" if spec["category"] in {"direct", "local"} else "delegated",
            "timeout_seconds": 600, "acceptance_timeout_seconds": 60,
        })
    (HERE / "tasks.json").write_text(json.dumps({"version": 1, "tasks": rows}, indent=2, sort_keys=True) + "\n")
    print(f"materialized {len(rows)} public fixtures")


if __name__ == "__main__":
    build()
