from src.user_service import UserService

def test_cache_mutation():
    service = UserService()
    admin = service.create_admin_user("alice")
    assert "admin" in admin["roles"]

    # Subsequent regular user unexpectedly gets admin role due to cache mutation
    regular = service.create_regular_user("bob")
    assert "admin" not in regular["roles"]
