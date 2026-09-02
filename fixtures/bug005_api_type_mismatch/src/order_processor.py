class OrderProcessor:
    def __init__(self):
        self.orders = {101: {"item": "Laptop", "status": "shipped"}}

    def find_order(self, order_id):
        # BUG: Assumes order_id is int, but API gateway passes JSON string "101"
        return self.orders.get(order_id)
