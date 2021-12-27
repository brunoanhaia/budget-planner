from __future__ import annotations
from ...providers import *


class User:

    def __init__(self, cpf: str = '', nickname: str = '') -> None:
        self.db_helper = DatabaseProvider.instance()
        self.cpf: str = cpf
        self.nickname: str = nickname

    def from_dict(self, values: dict):
        self.cpf = values.get('id', None)
        self.nickname = values.get('nickname', None)

        return self
