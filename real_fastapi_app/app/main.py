from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.order import OrderService

app = FastAPI(title="E-Commerce Order API")

class CheckoutRequest(BaseModel):
    user_id: str
    amount: float
    currency: Optional[str] = "USD"
    promo_code: Optional[str] = None

@app.post("/checkout")
def checkout(request: CheckoutRequest):
    try:
        result = OrderService.process_checkout(request.model_dump())
        return result
    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"Internal payment failure: missing {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
