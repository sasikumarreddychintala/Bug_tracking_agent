class UserCache:
    _cached_roles = ["guest", "viewer"]

    @classmethod
    def get_default_roles(cls):
        # BUG: Returns internal list reference directly instead of a copy (.copy())
        return cls._cached_roles
