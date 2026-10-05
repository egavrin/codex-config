"""Read local Codex rollout telemetry without copying prompt or tool content."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

TOKEN_FIELDS = (
    "input_tokens", "cached_input_tokens", "cache_write_input_tokens",
    "output_tokens", "reasoning_output_tokens", "total_tokens",
)


def _time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def read_rollout(path: Path) -> dict[str, Any]:
    """Use the last cumulative thread usage, never the sum of usage records."""
    meta: dict[str, Any] = {}
    contexts: list[dict[str, Any]] = []
    usage: dict[str, int] | None = None
    has_usage_record = False
    turn_ids: set[str] = set()
    malformed = 0
    with path.open(encoding="utf-8", errors="replace") as stream:
        lines = stream.readlines()
    for line in lines:
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            malformed += 1
            continue
        kind = item.get("type")
        payload = item.get("payload")
        if not isinstance(payload, dict):
            continue
        if kind == "session_meta":
            meta = payload
        elif kind == "turn_context":
            contexts.append(payload)
        elif kind == "token_usage_record":
            candidate = payload.get("thread_token_usage")
            if isinstance(candidate, dict):
                has_usage_record = True
                usage = {key: int(candidate.get(key, 0)) for key in TOKEN_FIELDS}
        elif kind == "event_msg":
            if payload.get("type") == "task_started" and payload.get("turn_id"):
                turn_ids.add(str(payload["turn_id"]))
            if not has_usage_record and payload.get("type") == "token_count":
                info = payload.get("info")
                candidate = info.get("total_token_usage") if isinstance(info, dict) else None
                if isinstance(candidate, dict):
                    usage = {key: int(candidate.get(key, 0)) for key in TOKEN_FIELDS}
    context = contexts[-1] if contexts else {}
    return {
        "session_id": meta.get("id") or meta.get("session_id"),
        "parent_session_id": meta.get("parent_thread_id"),
        "cwd": meta.get("cwd"),
        "started_at": meta.get("timestamp"),
        "model": context.get("model"),
        "effort": context.get("effort"),
        "observed_tier": None,
        "model_changed": len({ctx.get("model") for ctx in contexts}) > 1,
        "turn_count": len(turn_ids) or len({ctx.get("turn_id") for ctx in contexts}),
        "usage": usage,
        "malformed_lines": malformed,
    }


def collect_rollouts(
    sessions_root: Path, workspace: Path, started: datetime, ended: datetime,
) -> dict[str, Any]:
    """Match sessions by unique workspace and time, then retain one root tree."""
    lower = started - timedelta(seconds=10)
    upper = ended + timedelta(seconds=30)
    candidates: dict[str, dict[str, Any]] = {}
    if sessions_root.exists():
        for path in sessions_root.rglob("*.jsonl"):
            # Old sessions are numerous. Their file timestamp is a cheap first filter.
            modified = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
            if not lower <= modified <= upper + timedelta(minutes=2):
                continue
            try:
                record = read_rollout(path)
            except OSError:
                continue
            timestamp = _time(record["started_at"])
            if (
                record["cwd"] == str(workspace)
                and timestamp is not None
                and lower <= timestamp <= upper
                and record["session_id"]
            ):
                candidates[record["session_id"]] = record
    roots = [row for row in candidates.values() if not row["parent_session_id"]]
    roots.sort(key=lambda row: row["started_at"] or "")
    if len(roots) != 1:
        return {"root_session_id": None, "sessions": [], "issue": f"expected one root, found {len(roots)}"}
    root_id = roots[0]["session_id"]
    selected = {root_id}
    while True:
        additions = {sid for sid, row in candidates.items() if row["parent_session_id"] in selected}
        if additions <= selected:
            break
        selected |= additions
    sessions = [candidates[sid] for sid in selected]
    sessions.sort(key=lambda row: (row["started_at"] or "", row["session_id"]))
    return {"root_session_id": root_id, "sessions": sessions, "issue": None}
