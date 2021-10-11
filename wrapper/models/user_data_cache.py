
from .account_statement import AccountStatement
from .nubank_account_monthly_summary import NuBankAccountMonthlySummary
from .nubank_card_bill import NuBankCardBill
from .nubank_card_bill_amount_per_tag import CardBillAmountPerTag
from .nubank_card_transaction import NuBankCardBillTransactions
from .user import User


class UserDataCache:

    class CardData:
        
        def __init__(self) -> None:
            self.feed: list[dict] = []
            self.statements: list[dict] = []
            self.bill_list: list[NuBankCardBill] = list()
            self.bill_amount_per_tag_list: list[CardBillAmountPerTag] = list()
            self.transaction_list: list[NuBankCardBillTransactions] = list()

    class AccountData:
        
        def __init__(self) -> None:
            self.monthly_summary_list: list[NuBankAccountMonthlySummary] = list()
            self.feed: list[dict] = list()
            self.statements: AccountStatement = None

    def __init__(self):
        self.user: User = None
        self.card = self.CardData()
        self.account = self.AccountData()

