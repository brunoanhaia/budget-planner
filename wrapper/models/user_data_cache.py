
from .nubank_account_monthly_summary import NuBankAccountMonthlySummary
from .nubank_card_bill import NuBankCardBill
from .nubank_card_bill_amount_per_tag import CardBillAmountPerTag
from .nubank_card_transaction import NuBankCardBillTransactions
from .user import User


class UserDataCache:

    def __init__(self):
        self.user: User = None
        self.card_feed: list[dict] = []
        self.card_statements: list[dict] = []
        self.card_bill_list: list[NuBankCardBill] = list()
        self.card_bill_amount_per_tag_list: list[CardBillAmountPerTag] = list()
        self.card_transaction_list: list[NuBankCardBillTransactions] = list()
        self.account_monthly_summary_list: list[NuBankAccountMonthlySummary] = list()