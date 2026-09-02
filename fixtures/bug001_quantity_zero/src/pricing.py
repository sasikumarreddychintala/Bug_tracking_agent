def calculate_unit_price(total_amount: float, quantity: int) -> float:
    # Downstream pricing calculation assumes positive integer quantity
    return round(total_amount / quantity, 2)
