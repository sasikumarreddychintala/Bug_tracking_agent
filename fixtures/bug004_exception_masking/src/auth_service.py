def verify_token(token: str) -> dict:
    try:
        if token == "expired":
            raise ValueError("Token has expired")
        return {"user_id": 42, "role": "member"}
    except Exception:
        # BUG: Broad except swallows error and returns None instead of raising AuthError
        return None
