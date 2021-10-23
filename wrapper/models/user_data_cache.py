from .user import User
from .account_model import Account
from .nubank_card_bill import NuBankCardBill
from .nubank_card_bill_amount_per_tag import CardBillAmountPerTag
from .nubank_card_transaction import NuBankCardBillTransactions


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
