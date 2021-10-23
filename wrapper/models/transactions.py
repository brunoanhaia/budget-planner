from datetime import date

from wrapper.utils.file_helper import FileHelper
from .base_model import BaseList, BaseModel


class Transaction(BaseModel):
    def __init__(self, cpf):
        super().__init__(cpf)
        self.id: str = ''
        self.type_name: str = ''
        self.title: str = ''
        self.detail: str = ''
        self.post_date: date = date.today()
        self.__amount: float = 0.0
        self.__origin_account: str = ''
        self.__destination_account: str = ''

    # region Properties
    @property
    def amount(self):
        return self.__amount

    @amount.setter
    def amount(self, value):
        self.__amount = self.round_to_two_decimal(value)

    @property
    def origin_account(self):
        return self.__origin_account

    @origin_account.setter
    def origin_account(self, value):
        if value is not None and type(value) is dict and 'name' in value:
            value = value['name']

        self.__origin_account = value

    @property
    def destination_account(self):
        return self.__destination_account

    @destination_account.setter
    def destination_account(self, value):
        if value is not None and type(value) is dict and 'name' in value:
            value = value['name']

        self.__destination_account = value


class TransactionsList(BaseList):
    __sheet_name__ = 'account_statements'

    def __init__(self, cpf, transactions: list[Transaction]):
        super().__init__(cpf)
        self.__list = transactions
        self.__file_helper = FileHelper(cpf)

    def __getitem__(self, index):
        return self.__list[index]

    def __len__(self):
        return len(self.__list)

    def get_list(self):
        return self.__list

    def get_file_path(self):
        file_path = self.__file_helper.account_statement.path

        return file_path

    def get_transactions_dict(self) -> list[dict]:
        return [transaction.to_dict() for transaction
                in self.__list]
