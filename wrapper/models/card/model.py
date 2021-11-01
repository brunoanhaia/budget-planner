from ..base_model import BaseModel
from . import *


class Card(BaseModel):

    def __init__(self, cpf=''):
        super().__init__(cpf)

        self.feed: list[dict] = []
        self.statements: list[dict] = []
        self.bills: BillList = BillList(cpf)
        self.tag_summary: TagSummaryList = TagSummaryList(cpf)
        self.transaction_list: list[TransactionBill] = list()

    def sync(self):
        self.__get_data()
        self.bills.save_file()
        self.tag_summary.save_file()

    def __get_data(self):
        self.bills.get_data()
        self.tag_summary.get_data()

