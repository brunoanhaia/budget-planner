class CacheDataProvider:
    _instance = None

    def __init__(self) -> None:
        from ..models import UserDataCache
        self.current = UserDataCache()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance