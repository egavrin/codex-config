"""Acceptance tests. These files are not editable by the production model."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from checkout import checkout_total
from pricing import apply_percent_discount


def check(actual, expected):
    assert actual == expected, f"expected {expected}, got {actual}"


check(apply_percent_discount(999, 10), 899)
check(checkout_total([(1200, 2)]), 2899)
check(checkout_total([(1200, 2)], "SAVE10"), 2659)
check(checkout_total([(5555, 1)], "SAVE10"), 4999)
check(checkout_total([(1200, 2)], "NOT-A-CODE"), 2899)
print("checkout acceptance passed")
