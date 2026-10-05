from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from benchmarks.routing.analysis import load_prices, route_credits, session_credits
from benchmarks.routing.rollouts import collect_rollouts, read_rollout


def write_rollout(path: Path, parent: str | None, workspace: Path, timestamp: datetime, usage: list[int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {"type": "session_meta", "payload": {"id": path.stem, "parent_thread_id": parent, "cwd": str(workspace), "timestamp": timestamp.isoformat()}},
        {"type": "turn_context", "payload": {"model": "gpt-6-sol" if parent else "gpt-6-luna", "effort": "medium", "turn_id": "one"}},
    ]
    for total in usage:
        rows.append({"type": "token_usage_record", "payload": {"thread_token_usage": {
            "input_tokens": total, "cached_input_tokens": total // 2, "output_tokens": 100,
            "total_tokens": total + 100, "cache_write_input_tokens": 0, "reasoning_output_tokens": 0,
        }}})
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n")


class RolloutTests(unittest.TestCase):
    def test_last_cumulative_record_and_child_link(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            workspace = root / "workspace"
            workspace.mkdir()
            now = datetime.now(timezone.utc)
            write_rollout(root / "sessions" / "root.jsonl", None, workspace, now, [100, 250])
            write_rollout(root / "sessions" / "child.jsonl", "root", workspace, now + timedelta(seconds=1), [80, 160])
            telemetry = collect_rollouts(root / "sessions", workspace, now, now + timedelta(seconds=2))
            self.assertEqual(telemetry["root_session_id"], "root")
            self.assertEqual(len(telemetry["sessions"]), 2)
            self.assertEqual(sum(row["usage"]["input_tokens"] for row in telemetry["sessions"]), 410)

    def test_truncated_and_missing_usage_are_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "broken.jsonl"
            path.write_text('{"type":"session_meta","payload":{"id":"root"}}\n{"broken"')
            result = read_rollout(path)
            self.assertEqual(result["malformed_lines"], 1)
            self.assertIsNone(result["usage"])


class PriceTests(unittest.TestCase):
    def test_cached_tokens_and_unknown_tier_range(self) -> None:
        prices = load_prices()
        session = {"session_id": "root", "model": "gpt-6-luna", "observed_tier": None, "usage": {
            "input_tokens": 1_000_000, "cached_input_tokens": 500_000,
            "output_tokens": 100_000,
        }}
        self.assertEqual(session_credits(session, prices), 2.625)
        record = {"telemetry": {"root_session_id": "root", "sessions": [session]}, "arm_config": {"tier": "default"}}
        result = route_credits(record, prices)
        self.assertEqual(result["estimate"], 2.625)
        self.assertEqual(result["minimum"], 2.625)
        self.assertEqual(result["maximum"], 6.5625)

    def test_missing_child_usage_prevents_full_route_price(self) -> None:
        prices = load_prices()
        record = {"telemetry": {"root_session_id": "root", "sessions": [
            {"session_id": "root", "model": "gpt-6-luna", "usage": {"input_tokens": 10, "cached_input_tokens": 0, "output_tokens": 1}},
            {"session_id": "child", "model": "gpt-6-sol", "usage": None},
        ]}, "arm_config": {"tier": "default"}}
        self.assertIsNone(route_credits(record, prices)["estimate"])


if __name__ == "__main__":
    unittest.main()
