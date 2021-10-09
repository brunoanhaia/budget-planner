import pandas as pd
from pygsheets.exceptions import WorksheetNotFound
from pygsheets.worksheet import Worksheet
import copy

from wrapper.utils.file_helper import FileHelper

from ..providers import DatabaseProvider, NuBankApiProvider, CacheDataProvider


class BaseModel:

    def __init__(self, cpf: str = '') -> None:
        self.cache_data = CacheDataProvider.instance().current
        self.file_helper = FileHelper(cpf)
        self.db_helper = DatabaseProvider.instance()
        self.nu = NuBankApiProvider.instance().nu
        self.cpf = cpf

    @property
    def cpf(self) -> str:
        return self._user_cpf

    @cpf.setter
    def cpf(self, value: str):
        self._user_cpf = value
        self.file_helper = FileHelper(value)

    @staticmethod
    def update_all_attributes(base_class, base, current, skip_fields=None):
        # Todo: Refactor this code to update the attributes of the worksheet
        pass

    def sync_base(self):
        current_worksheet_name = self.__class__.__name__

        current_worksheet: Worksheet = None

        try:
            current_worksheet = self.db_helper.default_sheet.worksheet(
                'title', current_worksheet_name)
        except WorksheetNotFound:
            current_worksheet = self.db_helper.default_sheet.add_worksheet(
                current_worksheet_name)

        df = pd.DataFrame.from_dict(self.__class__.__dict__)
        current_worksheet.set_dataframe(df, start='A1')

    def to_json(self) -> dict:
        obj_dict = copy.copy(self.__dict__)

        keys_with_underscore = [key for key in obj_dict if key.startswith(
            '_') or type(obj_dict[key]) not in [str, int, float, bool, list, dict]]
        [obj_dict.pop(key) for key in keys_with_underscore]

        return obj_dict

    def from_dict(self, values: dict):
        # Get keys from the class and remove private ones
        keys = [key for key in self.__dict__.keys() if not key.startswith('_')]

        for key in keys:
            dict_value = values.get(key, None)
            value_type = type(dict_value)

            if value_type not in [dict, list] and dict_value is not None:
                self.__setattr__(key, dict_value)

        return self

    @classmethod
    def round_to_two_decimal(self, value) -> float:
        return round(value, 2)
