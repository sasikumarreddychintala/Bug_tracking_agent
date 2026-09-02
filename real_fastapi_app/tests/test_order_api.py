import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from app.order import OrderService

def test_standard_checkout_succeeds():
    payload = {
        "user_id": "USR-101",
        "amount": 100.0,
        "currency": "USD"
    }
    res = OrderService.process_checkout(payload)
    assert res["final_amount"] == 100.0
    assert res["payment"]["status"] == "success"

def test_promo_code_checkout_fails():
    """
    When promo_code 'SUMMER50' is provided, checkout crashes with KeyError: 'currency'
    because order.py failed to forward the currency field to payment.py.
    """
    payload = {
        "user_id": "USR-102",
        "amount": 200.0,
        "currency": "USD",
        "promo_code": "SUMMER50"
    }
    # This test triggers the bug and fails with KeyError: 'currency'
    res = OrderService.process_checkout(payload)
    assert res["final_amount"] == 100.0
    assert res["payment"]["status"] == "success"
