from src.order_processor import OrderProcessor

def handle_order_request(request_payload: dict) -> dict:
    processor = OrderProcessor()
    # request_payload["order_id"] is passed as string '101'
    order = processor.find_order(request_payload["order_id"])
    if not order:
        raise KeyError(f"Order {request_payload['order_id']} not found")
    return order
