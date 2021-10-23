import pandas as pd
from pandas.core.frame import DataFrame
from pygsheets import FormatType
from pygsheets.cell import Cell
from pygsheets.worksheet import Worksheet

from .base_model import BaseModel
from .summary_per_month import SummaryPerMonth, SummaryPerMonthList
from .transactions import TransactionsList, Transaction


class Account(BaseModel):

    def __init__(self, cpf=''):
        super().__init__(cpf)
        self.transactions_list: TransactionsList = []
        self.summary_per_month_list: SummaryPerMonthList = []

    def sync(self):
        self.__get_data()
        self.__generate_account_monthly_summary()
        # self.transactions_list.set_sheets_data()
        # self.summary_per_month_list.set_sheets_data()
        self.transactions_list.save_file()
        self.summary_per_month_list.save_file()

    def __get_data(self):
        raw_account_transactions = self.nu.get_account_statements()
        return self.__from_transactions_dict(raw_account_transactions)

    @staticmethod
    def __get_cell_header(cell_matrix: list[list[Cell]],
                          header_col_name: str):

        header_cells: list[Cell] = cell_matrix[0]

        result = [cell for cell in header_cells
                  if cell.value == header_col_name]

        return result[0]

    @staticmethod
    def __format_col(worksheet: Worksheet, col_header_name: str,
                     format_type: FormatType.CURRENCY):

        header_cells: list[Cell] = worksheet.get_values('A1', 'AZ1',
                                                        returnas='cell')[0]

        result = [cell for cell in header_cells
                  if cell.value == col_header_name]

        if len(result) > 0:
            rng = worksheet.get_col(result[0].col, returnas='range')

            model_cell = Cell('A1')
            model_cell.set_number_format(format_type, '')

            rng.apply_format(model_cell)

    def __generate_account_monthly_summary(self) -> dict:
        values = self.transactions_list

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

        self.summary_per_month_list = \
            SummaryPerMonthList(self.cpf, monthly_summary_list_obj)

        return self.summary_per_month_list

    def __from_transactions_dict(self, transactions: list[dict]):

        # transforming properties using dict and removing old properties
        raw_property_map: dict[str, str] = {
            '__typename': 'type_name',
            'postDate': 'post_date',
            'destinationAccount': 'destination_account',
            'originAccount': 'origin_account',
        }

        for transaction in transactions:
            for prop in raw_property_map:
                if prop in transaction:
                    transaction[raw_property_map[prop]] = transaction[prop]

                    transaction.pop(prop)

        transactions_dict_obj = [Transaction(self.cpf).from_dict(
            transaction) for transaction in transactions]

        self.transactions_list = TransactionsList(self.cpf,
                                                  transactions_dict_obj)

        return self
