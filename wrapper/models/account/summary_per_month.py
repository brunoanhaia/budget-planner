from datetime import date

from wrapper.models import *
from wrapper.models.base_model import Base, BaseList, BaseModel


class SummaryPerMonthList(BaseList):
    __sheet_name__ = 'account_summary_per_month'

    def __init__(self, cpf: str, summary_list: list[object]):
        Base.__init__(self, cpf)
        self.__list: TransactionsList = summary_list

    def __getitem__(self, index):
        return self.__list[index]

    def __len__(self):
        return len(self.__list)

    def get_list(self):
        return self.__list

    def get_file_path(self):
        return self.file_helper.account_monthly_summary.path


class SummaryPerMonth(BaseModel):
    def __init__(self, cpf=''):
        super().__init__(cpf)
        self.ref_date: date = date.today()
        self.__credit: float = 0.0
        self.__debit: float = 0.0
        self.__balance: float = 0.0
        self.__total: float = 0.0

    # region Properties

    @property
    def credit(self):
        return self.__credit

    @credit.setter
    def credit(self, value):
        self.__credit = self.round_to_two_decimal(value)

    @property
    def debit(self):
        return self.__debit

    @debit.setter
    def debit(self, value):
        self.__debit = self.round_to_two_decimal(value)

    @property
    def balance(self):
        return self.__balance

    @balance.setter
    def balance(self, value):
        self.__balance = self.round_to_two_decimal(value)

    @property
    def total(self):
        return self.__total

    @total.setter
    def total(self, value):
        self.__total = self.round_to_two_decimal(value)
