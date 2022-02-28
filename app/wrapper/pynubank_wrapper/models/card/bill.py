from __future__ import annotations

from datetime import datetime
import os

from . import *
from ..base_model import BaseModel, BaseList


class BillList(BaseList):
    __sheet_name__ = 'card_bill'

    def __init__(self, cpf):
        super().__init__(cpf)
        self.__list: list[NuBankCardBill] = []

    def save_file(self):
        for item in self.__list:

            close_date = datetime.strptime(
                item.close_date, "%Y-%m-%d")
            file_path = self.file_helper.card_bill.get_custom_path(
                close_date.strftime("%Y-%m"))

            self.file_helper.save_to_file(file_path, item.to_dict())

    def get_list(self):
        return [item.to_dict() for item in self.__list]

    def get_data(self):
        if len(self.__list) == 0:
            raw_data = self.nu.get_bills()
            bills: list[NuBankCardBill] = [
                NuBankCardBill().from_dict(card_bill)
                for card_bill in raw_data]

            for b in bills:
                # Link bill to user
                b.cpf = self.cpf

            # Storing the data in the class instance for future use
            self.__list = bills

        return self.get_list()

    def load_data(self):
        files_list = self.file_helper.card_bill.files
        card_bills_list = []

        for file in files_list:
            file_content = self.file_helper.read_from_file(file)
            card_bills_list.append(file_content)

        self.__list = card_bills_list

    def __getitem__(self, index):
        return self.__list[index]

    def __len__(self):
        return len(self.__list)


class NuBankCardBill(BaseModel):

    def __init__(self) -> None:
        super().__init__()
        self.nubank_id: str = ''
        self.state: str = ''
        self.due_date: str = ''
        self.effective_due_date: str = ''
        self.open_date: str = ''
        self.link_href: str = ''
        self.__ref_date: str = ''
        self.__close_date: str = ''
        self.__past_balance: float = 0.0
        self.__total_balance: float = 0.0
        self.__interest_rate: float = 0.0
        self.__interest: float = 0.0
        self.__total_cumulative: float = 0.0
        self.__paid: float = 0.0
        self.__minimum_payment: float = 0.0

    # region Properties
    @property
    def close_date(self):
        return self.__close_date

    @close_date.setter
    def close_date(self, value):
        self.__close_date = value
        self.__ref_date = datetime.strptime(
            value, "%Y-%m-%d").strftime("%Y-%m")

    @property
    def ref_date(self):
        return self.__ref_date
    
    def ref_date(self, value):
        self.__ref_date = value

    @property
    def past_balance(self):
        return self.__past_balance

    @past_balance.setter
    def past_balance(self, value):
        self.__past_balance = self.round_to_two_decimal(value)

    @property
    def total_balance(self):
        return self.__total_balance

    @total_balance.setter
    def total_balance(self, value):
        self.__total_balance = self.round_to_two_decimal(value)

    @property
    def interest_rate(self):
        return self.__interest_rate

    @interest_rate.setter
    def interest_rate(self, value):
        self.__interest_rate = self.round_to_two_decimal(value)

    @property
    def interest(self):
        return self.__interest

    @interest.setter
    def interest(self, value):
        self.__interest = self.round_to_two_decimal(value)

    @property
    def total_cumulative(self):
        return self.__total_cumulative

    @total_cumulative.setter
    def total_cumulative(self, value):
        self.__total_cumulative = self.round_to_two_decimal(value)

    @property
    def paid(self):
        return self.__paid

    @paid.setter
    def paid(self, value):
        self.__paid = self.round_to_two_decimal(value)

    @property
    def minimum_payment(self):
        return self.__minimum_payment

    @minimum_payment.setter
    def minimum_payment(self, value):
        self.__minimum_payment = self.round_to_two_decimal(value)

    # endregion

    def from_dict(self, values: dict):
        if values is not None and 'summary' in values:
            summary = values['summary']

            # By default, nubank api provide the values as integers, so we
            # need to convert and divide the value by 100.
            summary['past_balance'] = summary.get('past_balance', 0)/100
            summary['total_balance'] = summary.get('total_balance', 0)/100
            summary['total_cumulative'] = summary.get(
                'total_cumulative', 0)/100
            summary['paid'] = summary.get('paid', 0)/100
            summary['minimum_payment'] = summary.get('minimum_payment', 0)/100

            self.__planify_summary_section(values)

        # Simplifying the link_ref from card_bill
        if '_links' in values and 'self' in values['_links'] and \
                'href' in values['_links']['self']:
            values['link_href'] = values['_links']['self']['href']
            values.pop('_links')

        return BaseModel.from_dict(self, values)

    def sync(self, values: list[dict]):
        # Todo: Refactor this method to update the current values in the
        # worksheet with the new values.
        pass

    @staticmethod
    def __planify_summary_section(values: dict):

        # Iterate over each key in the summary dictionary
        for key in values['summary']:
            inner_value = values['summary'][key]
            values[key] = inner_value

        values.pop('summary')
