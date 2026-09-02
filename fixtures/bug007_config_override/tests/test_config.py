from src.config_loader import ServerConfig

def test_custom_port_override():
    config = ServerConfig(custom_port=9000)
    assert config.port == 9000
