from pricing import percent

def solve(subtotal_cents, discount_percent, tax_percent):
    tax = percent(subtotal_cents, tax_percent)
    discount = percent(subtotal_cents, discount_percent)
    return subtotal_cents + tax - discount
