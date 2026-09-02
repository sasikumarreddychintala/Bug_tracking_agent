def calculate_discount(order_amount: float, loyalty_tier: int) -> float:
    # BUG: Used <= 0 instead of < 0, erroneously zeroing valid tier-0 discounts
    if loyalty_tier <= 0:
        return 0.0
    elif loyalty_tier == 1:
        return order_amount * 0.10
    else:
        return order_amount * 0.20
