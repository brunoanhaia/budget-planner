from __future__ import annotations

from datetime import date

from ..base_model import BaseModel, BaseList


class TagSummaryList(BaseList):
    __sheet_name__ = 'card_tag_summary'

    def __init__(self, cpf):
        super().__init__(cpf)
        self.__list: list[TagSummary] = []

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
            amount_per_tag_list: list[TagSummary] = []

            transactions_list = self.cache_data.data.card.transaction_list

            for transaction_obj in transactions_list:

                # Get amount per tag in each bill and  and to the list
                amount_per_tag: list[TagSummary] = transaction_obj.group_tags_amount()
                if amount_per_tag is not None:
                    amount_per_tag_list.extend(amount_per_tag)

            self.__list = amount_per_tag_list

        return self.get_list()

    def save_file(self):
        # Save amount per tag in a file
        self.file_helper.save_to_file(
            self.file_helper.card_bill_amount_per_tag._path, self.__list)


class TagSummary(BaseModel):

    def __init__(self, cpf='') -> None:
        BaseModel.__init__(self, cpf)

        self.ref_date: str = ''
        self.close_date: date = date.today()
        self.value: float = 0.00
        self.tag: str = ''
