Implement the `SAVE10` promotion across the pricing and checkout components.
Only edit `pricing.py` and `checkout.py`; do not change files under `tests/` or
this prompt. Add `apply_percent_discount(amount_cents, percent)` to `pricing.py`.
It must return the whole-cent result after a percentage discount, rounding down
any fractional cent. In `checkout_total`, a `promo_code` exactly equal to
`"SAVE10"` applies a 10% discount to merchandise only. Shipping is never
discounted, and free-shipping eligibility stays based on the pre-discount
merchandise subtotal. Unknown or absent codes keep current behavior. Run
`python3 tests/test_checkout.py` when finished.
