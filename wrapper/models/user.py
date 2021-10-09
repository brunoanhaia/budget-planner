from .base_model import BaseModel
from ..providers import DatabaseProvider


class User(BaseModel):

    def __init__(self, cpf: str = '', nickname: str = '') -> None:
        self.db_helper = DatabaseProvider.instance()
        self.cpf: str = cpf
        self.nickname: str = nickname

    def from_dict(self, values: dict):
        self.cpf = values.get('id', None)
        self.nickname = values.get('nickname', None)

        return self

    def sync(self, current_value: dict):
        # Todo: Refactor this method to update the current values in the worksheet with the new values.
        self.sync_base()
