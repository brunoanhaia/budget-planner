from datetime import date

from pandas import DataFrame
import pandas as pd

from ...models import *
from ...models.base_model import Base, BaseList, BaseModel


class SummaryPerMonthList(BaseList):
    __sheet_name__ = 'account_summary_per_month'

    def __init__(self, cpf: str):
        Base.__init__(self, cpf)
        self.__list: list[SummaryPerMonth] = []

    def get_data(self):
        self.__generate()

        return self.get_list()

    def __generate(self) -> None:
        values = self.cache_data.data.account.transactions_list

        df = pd.DataFrame.from_dict([entry.to_dict() for entry in values])

        # Transforming string to datetime for easy grouping
        df['ref_date'] = pd.to_datetime(df['post_date'], format='%Y-%m-%d')
        df.loc[df.type_name == 'TransferInEvent', "credit"] = df.amount
        df.loc[df.type_name != 'TransferInEvent', "debit"] = df.amount

        # Resampling data and grouping by ref_date
        rdf: DataFrame = df.resample('MS', on='ref_date').agg(
            {'credit': 'sum', 'debit': 'sum'})
        rdf['balance'] = rdf.credit - rdf.debit
        rdf['total'] = rdf['balance'].cumsum()
        rdf['cpf'] = self.cpf

        # Rounding everything with 2 decimal places
        rdf = rdf.round(2)

        # Transforming the ref_date index back to column and to the
        # appropriate format
        rdf.reset_index(inplace=True)
        rdf['ref_date'] = rdf["ref_date"].dt.strftime("%Y-%m-%d")

        # Converting dataframe to dictionary
        df_dict = rdf.to_dict(
            orient='records')

        monthly_summary_list_obj = [
            SummaryPerMonth().from_dict(monthly_summary)
            for monthly_summary in df_dict]

        self.__list = monthly_summary_list_obj

    def __getitem__(self, index):
        return self.__list[index]

    def __len__(self):
        return len(self.__list)

    def get_list(self):
        return [item.to_dict() for item in self.__list]

    def get_file_path(self):
        return self.file_helper.account_monthly_summary.path


class SummaryPerMonth(BaseModel):
    def __init__(self, cpf=''):
        super().__init__(cpf)
        self.ref_date: date = date.today()
        self.__credit: float = 0.0
        self.__debit: float = 0.0
        self.__balance: float = 0.0
        self.__total: float = 0.0

    # region Properties

    @property
    def credit(self):
        return self.__credit

    @credit.setter
    def credit(self, value):
        self.__credit = self.round_to_two_decimal(value)

    @property
    def debit(self):
        return self.__debit

    @debit.setter
    def debit(self, value):
        self.__debit = self.round_to_two_decimal(value)

    @property
    def balance(self):
        return self.__balance

    @balance.setter
    def balance(self, value):
        self.__balance = self.round_to_two_decimal(value)

    @property
    def total(self):
        return self.__total

    @total.setter
    def total(self, value):
        self.__total = self.round_to_two_decimal(value)
