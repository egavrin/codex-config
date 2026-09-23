"""Acceptance tests. This file is not editable by the production model."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from slug import slugify


def check(actual, expected):
    assert actual == expected, f"expected {expected!r}, got {actual!r}"


check(slugify("Hello World"), "hello-world")
check(slugify("  Hello   World  "), "hello-world")
check(slugify("One\tTwo\nThree"), "one-two-three")
check(slugify("Already--Punctuated!"), "already--punctuated!")
print("slug acceptance passed")
