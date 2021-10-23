from datetime import datetime

from .base_model import BaseModel
from .nubank_card_transaction import NuBankCardBillTransactions, \
    NuBankCardTransaction


class NuBankCardBill(BaseModel):

    def __init__(self) -> None:
        super().__init__()
        self.nubank_id: str = ''
        self.state: str = ''
        self.due_date: str = ''
        self.close_date: str = ''
        self.effective_due_date: str = ''
        self.open_date: str = ''
        self.link_href: str = ''
        self.__past_balance: float = 0.0
        self.__total_balance: float = 0.0
        self.__interest_rate: float = 0.0
        self.__interest: float = 0.0
        self.__total_cumulative: float = 0.0
        self.__paid: float = 0.0
        self.__minimum_payment: float = 0.0

    # region Properties
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

    def get_transactions(self) -> NuBankCardBillTransactions:

        raw_details = self.nu._client.get(self.link_href)['bill']
        raw_transaction_list = raw_details.get('line_items', None)
        self.nubank_id = raw_details.get('id', None)

        transaction_list = [NuBankCardTransaction(self.cpf).from_dict(
            transaction) for transaction in raw_transaction_list]

        if self.cache_data.card.statements is None or \
           len(self.cache_data.card.statements) == 0:
            self.cache_data.card.statements = self.nu.get_card_statements()

        transaction_list = [transaction.add_details_from_card_statement()
                            for transaction in transaction_list]

        # self.details = transaction_list

        # Get the ref_date
        ref_date = datetime.strptime(
            self.close_date, "%Y-%m-%d").strftime("%Y-%m")
        file_path = self.file_helper.card_bill_transactions.get_custom_path(
            ref_date)

        # Create the transaction object
        transaction_obj = NuBankCardBillTransactions()
        transaction_obj.ref_date = ref_date
        transaction_obj.close_date = self.close_date
        transaction_obj.cpf = getattr(self, 'cpf')
        transaction_obj.transactions = transaction_list

        self.file_helper.save_to_file(file_path, transaction_obj)

        return transaction_obj
