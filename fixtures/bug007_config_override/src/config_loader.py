import os

class ServerConfig:
    def __init__(self, custom_port: int = None):
        # BUG: os.getenv default overrides explicit custom_port argument when set
        env_port = int(os.getenv("SERVER_PORT", "8080"))
        self.port = env_port if env_port else custom_port
