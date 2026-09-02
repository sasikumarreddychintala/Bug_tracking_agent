from src.auth_service import verify_token

def get_user_role(token: str) -> str:
    auth_data = verify_token(token)
    # Downstream crash with AttributeError: 'NoneType' object has no attribute 'get'
    return auth_data.get("role", "unknown")
