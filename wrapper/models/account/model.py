from pygsheets import FormatType
from pygsheets.cell import Cell
from pygsheets.worksheet import Worksheet

from . import *
from ..base_model import BaseModel


class Account(BaseModel):

    def __init__(self, cpf=''):
        super().__init__(cpf)
        self.transactions_list: TransactionsList = TransactionsList(self.cpf)
        self.summary_list: SummaryPerMonthList = SummaryPerMonthList(self.cpf)

    def sync(self):
        self.__get_data()
        # self.transactions_list.set_sheets_data()
        # self.summary_per_month_list.set_sheets_data()
        self.transactions_list.save_file()
        self.summary_list.save_file()

    def __get_data(self):
        self.transactions_list.get_data()
        self.summary_list.get_data()

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
