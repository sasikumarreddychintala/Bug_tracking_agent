from src.discount import calculate_discount

def process_order(base_amount: float, tier: int = 0) -> float:
    discount = calculate_discount(base_amount, tier)
    return base_amount - discount
