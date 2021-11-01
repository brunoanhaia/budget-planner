from __future__ import annotations

from datetime import date, datetime

from ..base_model import BaseModel, BaseList
from wrapper.utils import planify_array
from . import *


class TransactionBillList(BaseList):

    def get_data(self):
        bills = self.cache_data.data.card.bills

        bills_with_details = [b for b in bills if b.state != 'future']

        for b in bills_with_details:
            self.__get_transactions(b)
            # Todo: Parei aqui
            pass

    def __get_transactions(self, bill: NuBankCardBill):
        raw_details = self.nu._client.get(self.link_href)['bill']
        raw_transaction_list = raw_details.get('line_items', None)

        transaction_list = [Transaction(self.cpf).from_dict(
            t) for t in raw_transaction_list]

        if self.cache_data.data.card.statements is None or \
           len(self.cache_data.data.card.statements) == 0:
            self.cache_data.data.card.statements = self.nu.get_card_statements()

        transaction_list = [t.add_details_from_card_statement()
                            for t in transaction_list]

        # self.details = transaction_list

        # Get the ref_date
        ref_date = datetime.strptime(
            bill.close_date, "%Y-%m-%d").strftime("%Y-%m")
        file_path = self.file_helper.card_bill_transactions.get_custom_path(
            ref_date)

        # Create the transaction object
        transaction_obj = TransactionBill()
        transaction_obj.ref_date = ref_date
        transaction_obj.close_date = bill.close_date
        transaction_obj.cpf = getattr(self, 'cpf')
        transaction_obj.transactions = transaction_list

        self.file_helper.save_to_file(file_path, transaction_obj)

        return transaction_obj

    def get_file_path(self):
        pass

    def get_list(self):
        pass

    def __getitem__(self, index):
        pass

    def __len__(self):
        pass


class Transaction(BaseModel):

    def __init__(self, cpf=''):
        super().__init__(cpf)
        self.id: int = 0
        self.card_bill_id: int = 0
        self.state: str = ''
        self.category: str = ''
        self.transaction_id: str = ''
        self.index: int = 0
        self.charges: int = 0
        self.type: str = ''
        self.title: str = ''
        self.nubank_id: str = ''
        self.href: str = ''
        self.post_date: str = ''
        self.tags: list[str] = []
        self.__amount: float = 0.0

    @property
    def amount(self):
        return self.__amount

    @amount.setter
    def amount(self, value):
        self.__amount = self.round_to_two_decimal(value)

    def from_dict(self, value: dict):

        value['amount'] = value['amount']/100
        value['nubank_id'] = value['id']
        value.pop('id')

        if 'href' in value and 'transaction_id' not in value:
            value['transaction_id'] = value['href'].split('/')[-1]

        return BaseModel.from_dict(self, value)

    def add_details_from_card_statement(self):

        if self.cache_data.data.card.statements is None and \
           len(self.cache_data.data.card.statements) > 0:
            self.cache_data.data.card.statements = self.nu.get_card_feed()

        card_statements = self.cache_data.data.card.statements

        statement = [statement for statement in card_statements if (
            self.transaction_id is not None and
            statement['id'] == self.transaction_id)]

        if statement is not None and len(statement) > 0:
            detail_filter_list = ['tags', 'charges']

            for detail in detail_filter_list:
                found_key = statement[0]
                details_key = found_key.get('details', None)

                if details_key is not None and detail in details_key:
                    self.__setattr__(detail, details_key[detail])

        return self


class TransactionBill(BaseModel):

    def __init__(self):
        super().__init__()
        self.ref_date: str = ''
        self.close_date: date = date.min
        self.transactions: list[Transaction] = []

    def group_tags_amount(self) -> TagSummary:
        transactions_with_tag_obj = [
            t for t in self.transactions if
            len(t.tags) > 0]

        if len(transactions_with_tag_obj) > 0:
            amount_per_tag = self.__get_amount_per_tag(
                transactions_with_tag_obj)

            amount_per_tag_obj = TagSummary()
            amount_per_tag_obj.cpf = self.cpf
            amount_per_tag_obj.ref_date = self.ref_date
            amount_per_tag_obj.close_date = self.close_date
            amount_per_tag_obj.values = amount_per_tag

            return amount_per_tag_obj

    def __get_amount_per_tag(self, transactions_list:
                             list[Transaction]) -> dict[str, float]:

        amount_per_tag_dict = {}

        for t in transactions_list:
            tags = planify_array(t.tags)
            amount = self.round_to_two_decimal(t.amount)

            for tag in tags:
                if tag in amount_per_tag_dict:
                    amount_per_tag_dict[tag] += amount
                else:
                    amount_per_tag_dict[tag] = amount

                amount_per_tag_dict[tag] = self.round_to_two_decimal(
                                           amount_per_tag_dict[tag])

        return amount_per_tag_dict
