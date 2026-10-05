from decimal import Decimal, ROUND_HALF_UP

def percent(value, rate):
    return int((Decimal(value) * Decimal(rate) / 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
