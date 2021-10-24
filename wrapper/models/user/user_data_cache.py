from wrapper.models.account import *
from wrapper.models.card import *
from . import *


class UserDataCache:
    class CardData:

        def __init__(self) -> None:
            self.feed: list[dict] = []
            self.statements: list[dict] = []
            self.bill_list: list[NuBankCardBill] = list()
            self.bill_amount_per_tag_list: list[CardBillAmountPerTag] = list()
            self.transaction_list: list[NuBankCardBillTransactions] = list()

    def __init__(self):
        self.user: User = None
        self.card = self.CardData()
        self.account = Account()
