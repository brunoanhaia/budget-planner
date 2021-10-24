from wrapper.models import UserDataCache
from wrapper.providers import CacheDataProvider


class CacheDataManager:
    __cache_data_provider_instance = CacheDataProvider.instance().current

    @classmethod
    def get_data_cache_user(cls):
        cls.__cache_data_provider_instance = UserDataCache()
        return cls.__cache_data_provider_instance

