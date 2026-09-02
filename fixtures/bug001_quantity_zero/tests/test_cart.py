import pytest
from src.cart import ShoppingCart

def test_add_valid_item():
    cart = ShoppingCart()
    cart.add_item("Book", 50.0, 2)
    assert cart.get_total() == 50.0
    assert cart.items[0]["unit_price"] == 25.0

def test_add_zero_quantity_should_raise_or_prevent():
    cart = ShoppingCart()
    # When zero quantity is passed, it should either validate or handle safely, but crashes with ZeroDivisionError
    cart.add_item("Free Sample", 0.0, 0)
    assert len(cart.items) == 1
