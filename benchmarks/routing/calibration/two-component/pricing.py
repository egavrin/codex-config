"""Price calculations used by checkout."""


def line_subtotal(unit_cents: int, quantity: int) -> int:
    if unit_cents < 0 or quantity < 0:
        raise ValueError("prices and quantities must be non-negative")
    return unit_cents * quantity
