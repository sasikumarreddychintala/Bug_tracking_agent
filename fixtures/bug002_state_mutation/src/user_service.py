from src.cache_manager import UserCache

class UserService:
    def create_admin_user(self, username: str):
        roles = UserCache.get_default_roles()
        roles.append("admin")  # In-place mutation corrupts global cache!
        return {"username": username, "roles": roles}

    def create_regular_user(self, username: str):
        roles = UserCache.get_default_roles()
        return {"username": username, "roles": list(roles)}
