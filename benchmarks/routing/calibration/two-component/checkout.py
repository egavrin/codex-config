"""Checkout total calculation."""
from __future__ import annotations

from pricing import line_subtotal

SHIPPING_CENTS = 499
FREE_SHIPPING_SUBTOTAL_CENTS = 5000


def checkout_total(lines: list[tuple[int, int]], promo_code: str | None = None) -> int:
    """Return the payable total for (unit_cents, quantity) lines."""
    merchandise = sum(line_subtotal(unit_cents, quantity) for unit_cents, quantity in lines)
    shipping = 0 if merchandise >= FREE_SHIPPING_SUBTOTAL_CENTS else SHIPPING_CENTS
    return merchandise + shipping
