from __future__ import annotations

import unittest

from benchmarks.routing.analysis import paired_scores, report
from benchmarks.routing.runner import schedule


def row(task: str, arm: str, accepted: bool, credits: float, seconds: float = 10) -> dict:
    return {
        "task_id": task, "category": "direct", "arm": arm, "accepted": accepted,
        "elapsed_seconds": seconds, "status": "complete", "route_observed": "direct",
        "critical_defect": False,
        "arm_config": {"tier": "default"},
        "telemetry": {"root_session_id": "root", "sessions": [{
            "session_id": "root", "model": "gpt-6-luna" if arm == "luna" else "gpt-5.6-terra",
            "observed_tier": "default", "usage": {"input_tokens": int(credits * 1000),
                "cached_input_tokens": 0, "output_tokens": 0},
        }]},
        "credits": {"estimate": credits, "minimum": credits, "maximum": credits},
    }


class AnalysisTests(unittest.TestCase):
    def test_failed_attempt_cost_counts_toward_success(self) -> None:
        rows = [row("one", "terra", True, 4), row("one", "luna", False, 2), row("one", "luna", True, 2)]
        scores = paired_scores(rows)["tasks"]["one"]
        self.assertEqual(scores["values"]["luna"][1], 4)
        self.assertEqual(scores["values"]["luna"][2], 20)
        self.assertLess(scores["scores"]["luna"], scores["scores"]["terra"])

    def test_no_success_has_zero_cost_and_time_components(self) -> None:
        scores = paired_scores([row("one", "terra", True, 4), row("one", "luna", False, 1)])["tasks"]["one"]
        self.assertEqual(scores["scores"]["luna"], 0)

    def test_partial_cycle_never_recommends_switch(self) -> None:
        summary = report([row("one", "terra", True, 4), row("one", "luna", True, 1)])
        self.assertEqual(summary["recommendation"], "retain_current_default")
        self.assertTrue(any("fewer than" in reason for reason in summary["recommendation_reasons"]))

    def test_arm_order_alternates(self) -> None:
        selected = [{"id": "a"}, {"id": "b"}]
        rows = schedule(selected, 2)
        self.assertEqual([arm for task, arm, repeat in rows[:2]], ["terra", "luna"])
        self.assertEqual([arm for task, arm, repeat in rows[2:4]], ["luna", "terra"])


if __name__ == "__main__":
    unittest.main()
