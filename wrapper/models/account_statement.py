import pandas as pd
from datetime import date
from pandas.core.frame import DataFrame
from wrapper.models.base_model import BaseModel


class AccountStatement(BaseModel):

    def __init__(self, cpf = ''):
        super().__init__(cpf)
        self.transactions_list: list[self.Transaction] = []

    def generate_account_monthly_summary(self) -> dict:
        # It will retrieve new account statements if it wasn't retrieved before.
        if self.cache_data.account.statements is None or len(self.cache_data.account.statements.transactions_list) == 0:
            self.get_account_statements(save_file=True)

        values = self.cache_data.account.statements.transactions_list

        # Still not sure why, but i cannot access __typename directly with pandas, so I'm changing it to type only
        for v in values:
            v['type'] = v['__typename']

        df = pd.DataFrame.from_dict(values)

        # Transforming string to datetime for easy grouping
        df['ref_date'] = pd.to_datetime(df['postDate'], format='%Y-%m-%d')
        df.loc[df.type == 'TransferInEvent', "credit"] = df.amount
        df.loc[df.type != 'TransferInEvent', "debit"] = df.amount

        # Resampling data and grouping by ref_date
        rdf: DataFrame = df.resample('MS', on='ref_date').agg(
            {'credit': 'sum', 'debit': 'sum'})
        rdf['balance'] = rdf.credit - rdf.debit
        rdf['total'] = rdf['balance'].cumsum()
        rdf['cpf'] = self.user.cpf

        # Rounding everything with 2 decimal places
        rdf = rdf.round(2)

        # Transforming the ref_date index back to column and to the appropriate format
        rdf.reset_index(inplace=True)
        rdf['ref_date'] = rdf["ref_date"].dt.strftime("%Y-%m-%d")

        # Converting dataframe to dictionary
        self.cache_data.account.monthly_summary_list = rdf.to_dict(
            orient='records')

        file_path = self.file_helper.account_monthly_summary.path
        self.file_helper.save_to_file(
            file_path, self.cache_data.account.monthly_summary_list)

        return self.cache_data.account.monthly_summary_list

    def from_transactions_dict(self, transactions: list[dict]):

        raw_property_map = {
            '__typename': 'type_name',
            'postDate': 'post_date',
            'destinationAccount': 'destination_account',
            'originAccount': 'origin_account',
        }

        for transaction in transactions:
            for property in raw_property_map:
                if property in transaction:
                    transaction[raw_property_map[property]] = transaction[property]
                    del transaction[property]

        self.transactions_list = [self.Transaction(self.cpf).from_dict(transaction) for transaction in transactions]
        return self

    class Transaction(BaseModel):
        def __init__(self, cpf):
            super().__init__(cpf)
            self.id: str = ''
            self.type_name: str = ''
            self.title: str = ''
            self.detail: str = ''
            self.post_date: date = date.today()
            self.__amount: float = 0.0
            self.__origin_account: str = ''
            self.__destination_account: str = ''

        @property
        def amount(self):
            return self.__amount

        @amount.setter
        def amount(self, value):
            self.__amount = self.round_to_two_decimal(value)

        @property
        def origin_account(self):
            return self.__origin_account

        @origin_account.setter
        def origin_account(self, value):
            if value is not None and type(value) is dict and 'name' in value:
                value = value['name']

            self.__origin_account = value
        
        @property
        def destination_account(self):
            return self.__destination_account

        @destination_account.setter
        def destination_account(self, value):
            if value is not None and type(value) is dict and 'name' in value:
                value = value['name']

            self.__destination_account = value
