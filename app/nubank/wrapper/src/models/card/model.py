from ..base_model import BaseModel
from . import *


class Card(BaseModel):

    def __init__(self, cpf=''):
        super().__init__(cpf)

        self.feed: list[dict] = []
        self.statements: StatementList = StatementList(cpf)
        self.bills: BillList = BillList(cpf)
        self.tag_summary: TagSummaryList = TagSummaryList(cpf)
        self.transaction_list: TransactionBillList = TransactionBillList(cpf)
        self.category_summary: CategorySummaryList = CategorySummaryList(cpf)

    def sync(self):
        self.__get_data()
        self.__save_file()
        self.__set_sheets_data()

    def __get_data(self):
        self.statements.get_data()
        self.bills.get_data()
        self.transaction_list.get_data()
        self.tag_summary.get_data()
        self.category_summary.get_data()

    def __save_file(self):
        self.statements.save_file()
        self.bills.save_file()
        self.transaction_list.save_file()
        self.tag_summary.save_file()
        self.category_summary.save_file()

    def __set_sheets_data(self):
        self.statements.set_sheets_data()
        self.tag_summary.set_sheets_data()
        self.category_summary.set_sheets_data()
        self.bills.set_sheets_data()
        self.transaction_list.set_sheets_data()
