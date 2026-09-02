from app.tools.stacktrace import parse_stacktrace

def test_parse_standard_python_stacktrace():
    trace = """Traceback (most recent call last):
  File "src/cart.py", line 10, in add_item
    unit_price = calculate_unit_price(total_price, quantity)
  File "src/pricing.py", line 4, in calculate_unit_price
    return round(total_amount / quantity, 2)
ZeroDivisionError: division by zero"""

    res = parse_stacktrace(trace)
    assert res["exception_type"] == "ZeroDivisionError"
    assert "division by zero" in res["message"]
    assert len(res["frames"]) == 2
    assert res["frames"][0]["file"] == "src/cart.py"
    assert res["frames"][0]["line"] == 10
    assert res["frames"][0]["function"] == "add_item"
    assert res["frames"][1]["file"] == "src/pricing.py"
    assert res["frames"][1]["line"] == 4
    assert res["frames"][1]["function"] == "calculate_unit_price"

def test_parse_empty_stacktrace():
    res = parse_stacktrace("")
    assert res["exception_type"] == "Unknown"
    assert res["frames"] == []
