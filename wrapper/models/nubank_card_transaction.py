from datetime import date
from wrapper.models.base_model import BaseModel
from wrapper.models.nubank_card_bill_amount_per_tag import CardBillAmountPerTag
from wrapper.utils import planify_array


class NuBankCardTransaction(BaseModel):

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

        if self.cache_data.card.statements is None and \
           len(self.cache_data.card.statements) > 0:
            self.cache_data.card.statements = self.nu.get_card_feed()

        card_statements = self.cache_data.card.statements

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


class NuBankCardBillTransactions(BaseModel):

    def __init__(self):
        super().__init__()
        self.ref_date: str = ''
        self.close_date: date = date.min
        self.transactions: list[NuBankCardTransaction] = {}

    def group_tags_amount(self) -> CardBillAmountPerTag:
        transactions_with_tag_obj = [
            transaction for transaction in self.transactions if
            len(transaction.tags) > 0]

        if len(transactions_with_tag_obj) > 0:
            amount_per_tag = self.__get_amount_per_tag(
                transactions_with_tag_obj)

            amount_per_tag_obj = CardBillAmountPerTag()
            amount_per_tag_obj.cpf = self.cpf
            amount_per_tag_obj.ref_date = self.ref_date
            amount_per_tag_obj.close_date = self.close_date
            amount_per_tag_obj.values = amount_per_tag

            return amount_per_tag_obj

    def __get_amount_per_tag(self, transactions_list:
                             list[NuBankCardTransaction]) -> dict[str, float]:

        amount_per_tag_dict = {}

        for transaction in transactions_list:
            tags = planify_array(transaction.tags)
            amount = self.round_to_two_decimal(transaction.amount)

            for tag in tags:
                if tag in amount_per_tag_dict:
                    amount_per_tag_dict[tag] += amount
                else:
                    amount_per_tag_dict[tag] = amount

                amount_per_tag_dict[tag] = self.round_to_two_decimal(
                                           amount_per_tag_dict[tag])

        return amount_per_tag_dict
