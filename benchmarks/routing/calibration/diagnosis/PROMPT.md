Diagnose and fix the reported production failure in `rolling_average`: a nightly
job passes a generator (for example `iter([3, 6, 9, 12])`) and gets a
`TypeError`, while list input works. Reproduce the failure, identify its cause,
and fix it. Only edit `window.py`; do not change files under `tests/` or this
prompt. Preserve list behavior, keep complete-window semantics, and preserve
the `ValueError` for a non-positive width. Run `python3 tests/test_window.py`
when finished.
