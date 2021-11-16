from __future__ import annotations

from datetime import date
from ..base_model import BaseModel, BaseList


class CategorySummaryList(BaseList):
    __sheet_name__ = 'card_category_summary'

    def __init__(self, cpf):
        super().__init__(cpf)
        self.__list: list[CategorySummary] = []

    def get_file_path(self):
        pass

    def get_list(self):
        return [item.to_dict() for item in self.__list]

    def __getitem__(self, index):
        return self.__list[index]

    def __len__(self):
        return len(self.__list)

    def get_data(self):
        if len(self.__list) == 0:
            amount_per_category_list: list[CategorySummary] = []

            transactions_list = self.cache_data.data.card.transaction_list

            for transaction_obj in transactions_list:

                # Get amount per category in each bill and  and to the list
                amount_per_category: list[CategorySummary] = transaction_obj.group_category_amount()
                if amount_per_category is not None:
                    amount_per_category_list.extend(amount_per_category)

            self.__list = amount_per_category_list

        return self.get_list()

    def save_file(self):
        # Save amount per category in a file
        self.file_helper.save_to_file(
            self.file_helper.card_bill_amount_per_category.path, self.__list)


class CategorySummary(BaseModel):

    def __init__(self, cpf='') -> None:
        BaseModel.__init__(self, cpf)

        self.ref_date: str = ''
        self.close_date: date = date.today()
        self.value: float = 0.00
        self.category: str = ''
