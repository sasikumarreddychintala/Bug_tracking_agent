class AuthClient:
    def get_token(self, api_key: str) -> str:
        if api_key == "invalid_key":
            # Returns 401 Unauthorized
            return ""
        return "valid_token"
