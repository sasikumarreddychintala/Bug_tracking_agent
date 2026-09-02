import pytest
from src.user_profile import get_user_role

def test_valid_token():
    assert get_user_role("valid") == "member"

def test_expired_token():
    # Should handle expired token or raise specific AuthError, not crash with AttributeError
    with pytest.raises(ValueError):
        get_user_role("expired")
