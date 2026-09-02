from src.pricing import calculate_unit_price

class ShoppingCart:
    def __init__(self):
        self.items = []

    def add_item(self, item_name: str, total_price: float, quantity: int):
        # BUG: Missing validation for quantity <= 0 before calling pricing calculation!
        unit_price = calculate_unit_price(total_price, quantity)
        self.items.append({
            "name": item_name,
            "total_price": total_price,
            "quantity": quantity,
            "unit_price": unit_price
        })

    def get_total(self) -> float:
        return sum(item["total_price"] for item in self.items)
