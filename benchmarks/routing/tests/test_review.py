"""Guard against rejecting a valid finding for its wording or paragraph layout."""

import tempfile
import unittest
from pathlib import Path

from benchmarks.routing.acceptance import review_results


class ReviewGraderTests(unittest.TestCase):
    def test_finding_heading_and_explanation_count_together(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / "REVIEW.md").write_text(
                "- **candidate.py:7-8 — database errors are reported as empty results.**\n\n"
                "  A closed connection returns `[]`; propagate the error to the caller.\n"
            )
            cases = [{"terms": [], "term_groups": [["candidate.py"], ["error", "fail"],
                      ["empty", "[]"]]}]
            self.assertEqual(review_results(workspace, cases), [{"value": True}])

    def test_distinct_markdown_findings_do_not_combine_terms(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / "REVIEW.md").write_text(
                "## Cache finding\n\n`candidate.mjs:4` has a cache keyed by user.\n\n"
                "## Logging finding\n\n`candidate.mjs:9` redirects to an external URL.\n"
            )
            cases = [{"terms": [], "term_groups": [["candidate.mjs"], ["cache"], ["redirect"]]}]
            self.assertEqual(review_results(workspace, cases), [{"value": False}])


if __name__ == "__main__":
    unittest.main()
