"""Acceptance tests. This file is not editable by the production model."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from window import rolling_average


assert rolling_average([3, 6, 9, 12], 2) == [4.5, 7.5, 10.5]
assert rolling_average(iter([3, 6, 9, 12]), 2) == [4.5, 7.5, 10.5]
assert rolling_average(iter([1, 2]), 3) == []
try:
    rolling_average(iter([1]), 0)
except ValueError:
    pass
else:
    raise AssertionError("non-positive widths must still raise ValueError")
print("window acceptance passed")
