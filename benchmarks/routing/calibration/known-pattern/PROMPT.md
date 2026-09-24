Fix the local slug helper. Only edit `slug.py`; do not change files under
`tests/` or this prompt. `slugify` must lowercase and trim its input, then turn
each run of one or more whitespace characters (spaces, tabs, newlines, etc.)
into exactly one `-`. Preserve non-whitespace characters unchanged. Run
`python3 tests/test_slug.py` when finished.
