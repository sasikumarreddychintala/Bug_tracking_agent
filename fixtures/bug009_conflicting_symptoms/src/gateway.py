import time
from src.auth_client import AuthClient

class ApiGateway:
    def forward_request(self, api_key: str):
        client = AuthClient()
        token = client.get_token(api_key)
        
        # BUG: Retries in a tight loop indefinitely when token is empty instead of failing fast on 401
        retries = 0
        while not token:
            retries += 1
            if retries > 5:
                raise TimeoutError("Gateway timeout waiting for upstream service")
            token = client.get_token(api_key)
        return {"status": "success", "token": token}
