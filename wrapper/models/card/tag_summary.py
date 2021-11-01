from __future__ import annotations

from datetime import date

from ..base_model import BaseModel, BaseList


class TagSummaryList(BaseList):

    def __init__(self, cpf):
        super().__init__(cpf)
        self.__list: list[TagSummary] = []

    def get_file_path(self):
        pass

    def get_list(self):
        self.__list

    def __getitem__(self, index):
        return self.__list[index]

    def __len__(self):
        return len(self.__list)

    def get_data(self):
        amount_per_tag_list: list[dict] = []

        transactions_list = self.cache_data.data.card.transaction_list

        # bill_list_with_details = [bill for bill in bill_list if bill.state != 'future']

        for transaction_obj in transactions_list:

            # Get amount per tag in each bill and  and to the list
            amount_per_tag: TagSummary = transaction_obj.group_tags_amount()
            if amount_per_tag is not None:
                amount_per_tag_list.append(amount_per_tag.to_dict())

        self.__list = amount_per_tag_list

    def save_file(self):
        # Save amount per tag in a file
        self.file_helper.save_to_file(
            self.file_helper.card_bill_amount_per_tag.path, self.__list)


class TagSummary(BaseModel):

    cpf: str
    ref_date: str
    close_date: date
    values: dict

    def __init__(self, cpf='') -> None:
        BaseModel.__init__(self, cpf)

        self.ref_date: str = ''
        self.close_date: date = date.today()
        self.values: dict = {}
