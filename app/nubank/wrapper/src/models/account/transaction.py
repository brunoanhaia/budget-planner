from datetime import date

from utils.file_helper import FileHelper
from models.base_model import BaseList, BaseModel


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

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.id == other.id and self.type_name == other.type_name and self.title == other.title and self.detail == other.detail and self.post_date == other.post_date and self.amount == other.amount and self.origin_account == other.origin_account and self.destination_account == other.destination_account
        return False


class TransactionsList(BaseList):
    __sheet_name__ = 'account_statements'

    def __init__(self, cpf):
        super().__init__(cpf)
        self.__list: list[Transaction] = []

    def __getitem__(self, index):
        return self.__list[index]

    def __len__(self):
        return len(self.__list)

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.__list == other.__list
        return False

    def get_data(self):
        if len(self.__list) == 0:
            raw_account_transactions = self.nu.get_account_statements()
            self.__fill_from_transactions(raw_account_transactions)

        return [item.to_dict() for item in self.__list]
    
    def load_data(self):
        account_statement_path = self.file_helper.account_statement.get_complete_path()
        list_of_dicts = self.file_helper.read_from_file(account_statement_path)
        self.__list = [Transaction(self.cpf).from_dict(item) for item in list_of_dicts]

    def __parse_pix_transactions(self, transactions: list[Transaction]):
        pix_trasactions_type_list = {
            'PixTransferOutEvent': 'destination_account'}

        for t in transactions:
            if t.type_name in pix_trasactions_type_list.keys():
                details = t.detail.split('\n')
                t.detail = details[1]
                t.__setattr__(pix_trasactions_type_list[t.type_name], details[0])

    def __fill_from_transactions(self, transactions: list[dict]):
        # transforming properties using dict and removing old properties
        raw_property_map: dict[str, str] = {
            '__typename': 'type_name',
            'postDate': 'post_date',
            'destinationAccount': 'destination_account',
            'originAccount': 'origin_account',
        }

        for t in transactions:
            for prop in raw_property_map:
                if prop in t:
                    t[raw_property_map[prop]] = t[prop]

                    t.pop(prop)

        transactions_dict_obj = [Transaction(self.cpf).from_dict(
            t) for t in transactions]

        self.__parse_pix_transactions(transactions_dict_obj)

        self.__list = transactions_dict_obj

    def get_file_path(self):
        file_path = self.file_helper.account_statement._path

        return file_path

    def get_list(self) -> list[dict]:
        return [transaction.to_dict() for transaction
                in self.__list]
