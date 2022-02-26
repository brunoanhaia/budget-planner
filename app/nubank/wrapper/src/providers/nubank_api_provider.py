from pynubank import Nubank


class NuBankApiProvider:
    _instance = None

    def __init__(self) -> None:
        self.nu = Nubank()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
