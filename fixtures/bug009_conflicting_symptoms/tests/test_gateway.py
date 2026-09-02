import pytest
from src.gateway import ApiGateway

def test_invalid_auth_handling():
    gateway = ApiGateway()
    # Should report authentication failure, but currently raises TimeoutError
    res = gateway.forward_request("valid_key")
    assert res["status"] == "success"

    with pytest.raises(PermissionError):
        gateway.forward_request("invalid_key")
