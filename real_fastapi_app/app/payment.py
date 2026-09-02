"""
Payment Processing Service (Downstream Component).
"""

SUPPORTED_RATES = {
    "USD": 1.0,
    "EUR": 0.85,
    "GBP": 0.73,
    "INR": 83.0
}

def charge_payment(amount: float, payment_data: dict) -> dict:
    # Downstream assumes 'currency' is always present because upstream OrderService should validate it
    currency = payment_data["currency"]
    rate = SUPPORTED_RATES.get(currency, 1.0)
    converted_amount = round(amount * rate, 2)
    
    return {
        "status": "success",
        "charged_amount": converted_amount,
        "currency": currency,
        "transaction_id": "TXN-998811"
    }
