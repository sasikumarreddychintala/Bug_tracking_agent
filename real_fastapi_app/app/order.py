"""
Order Creation & Processing Service (Upstream Component).
"""
from app.payment import charge_payment

class OrderService:
    @staticmethod
    def process_checkout(order_payload: dict) -> dict:
        total = order_payload.get("amount", 0.0)
        promo_code = order_payload.get("promo_code")
        
        if promo_code == "SUMMER50":
            total = total * 0.5
            # BUG: When promo code is applied, the payment dictionary is constructed
            # without forwarding the 'currency' key from the user request!
            payment_info = {
                "user_id": order_payload.get("user_id"),
                "promo_applied": True
                # Missing: "currency": order_payload.get("currency", "USD")
            }
        else:
            payment_info = {
                "user_id": order_payload.get("user_id"),
                "currency": order_payload.get("currency", "USD")
            }
            
        # Forwards unvalidated payment_info dictionary downstream
        payment_result = charge_payment(total, payment_info)
        
        return {
            "order_id": "ORD-12345",
            "final_amount": total,
            "payment": payment_result
        }
