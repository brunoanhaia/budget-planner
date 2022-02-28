from ..card import Card
from ..account import Account


class UserDataCache:
    def __init__(self, cpf):
        self.user: str = None
        self.card = Card(cpf)
        self.account = Account(cpf)
