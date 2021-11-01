from ..base_model import BaseModel
from . import *


class Card(BaseModel):

    def __init__(self, cpf=''):
        super().__init__(cpf)

        self.feed: list[dict] = []
        self.statements: list[dict] = []
        self.bills: BillList = BillList(cpf)
        self.tag_summary: TagSummaryList = TagSummaryList(cpf)
        self.transaction_list: TransactionBillList = TransactionBillList(cpf)

    def sync(self):
        self.__get_data()
        self.__save_file()

    def __get_data(self):
        self.bills.get_data()
        self.transaction_list.get_data()
        self.tag_summary.get_data()

    def __save_file(self):
        self.bills.save_file()
        self.transaction_list.save_file()
        self.tag_summary.save_file()
