from src.api_handler import handle_order_request

def test_api_order_lookup():
    payload = {"order_id": "101"}
    res = handle_order_request(payload)
    assert res["status"] == "shipped"
