from __future__ import annotations
import copy
from abc import abstractmethod
from datetime import date, datetime
import inspect
from typing import Any

import pandas as pd
from pygsheets.exceptions import PyGsheetsException, WorksheetNotFound
from pygsheets.worksheet import Worksheet

from ..providers import *
from ..utils import FileHelper


class Base:

    def __init__(self, cpf: str) -> None:

        self.cache_data = CacheDataProvider.instance()
        self.file_helper = FileHelper()
        self.db_helper = DatabaseProvider.instance()
        self.nu = NuBankApiProvider.instance().nu
        self.__cpf = ''
        self.cpf = cpf

    @property
    def cpf(self) -> str:
        return self.__cpf

    @cpf.setter
    def cpf(self, value: str):
        self.__cpf = value


class BaseList(Base):
    __sheet_name__: str

    def __init__(self, cpf: str) -> None:
        super().__init__(cpf)

    @abstractmethod
    def get_list(self):
        pass

    @abstractmethod
    def __getitem__(self, index):
        pass

    @abstractmethod
    def __len__(self):
        pass

    def save_file(self):
        file_path = self.get_file_path()

        self.file_helper.save_to_file(file_path, self.get_list())

    def set_sheets_data(self, get_data_method='get_data'):

        try:
            worksheet: Worksheet = self.db_helper \
                                .get_worksheet(self.__sheet_name__)

            list_obj = getattr(self, get_data_method)()
            df = pd.DataFrame.from_dict(list_obj)

            current_sheets_data = self.__get_sheets_data(current_cpf=False)

            # Workaround to prevent corrupted tables
            if '' not  in current_sheets_data.columns:
                current_sheets_data = current_sheets_data.append(df, ignore_index=True)
            else:
                current_sheets_data = df


            worksheet.clear()
            worksheet.set_dataframe(current_sheets_data, start='A1', fit=True)

            return True

        except PyGsheetsException:
            return False

    def __get_sheets_data(self, current_cpf: bool = True):
        worksheet: Worksheet = self.db_helper.get_worksheet(self.__sheet_name__)

        df = worksheet.get_as_df(include_tailing_empty=False)

        if 'cpf' not in df:
            return df

        if current_cpf:
            result_df = df[df['cpf'].astype(str) == self.cpf]
        else:
            result_df = df[df['cpf'].astype(str) != self.cpf]

        return result_df


class BaseModel(Base):

    def __init__(self, cpf: str = '') -> None:
        Base.__init__(self, cpf)

    @staticmethod
    def update_all_attributes(base_class, base, current, skip_fields=None):
        # Todo: Refactor this code to update the attributes of the worksheet
        pass

    def sync_base(self):
        current_worksheet_name = self.__class__.__name__

        try:
            current_worksheet = self.db_helper.default_sheet.worksheet(
                'title', current_worksheet_name)
        except WorksheetNotFound:
            current_worksheet = self.db_helper.default_sheet.add_worksheet(
                current_worksheet_name)

        df = pd.DataFrame.from_dict(self.__class__.__dict__)
        current_worksheet.set_dataframe(df, start='A1')

    @classmethod
    def get_base_class_list(cls, T):
        return [c.__name__ for c in inspect.getmro(T)]

    def to_dict(self) -> dict:
        obj_dict = copy.copy(self.__dict__)
        base_class_list = self.get_base_class_list(self.__class__)
        # cls_name = self.__class__.__name__
        # cls_parent_name = self.__class__.__base__.__name__

        forbidden_keys = [key for key in obj_dict if
                          type(obj_dict[key]) not in
                          [str, int, float, bool, list, dict, date, datetime]]
        [obj_dict.pop(key) for key in forbidden_keys]

        property_keys = [key for key in obj_dict if [cls_name for cls_name in base_class_list if key.startswith(f'_{cls_name}_')]]
        for key in property_keys:
            new_key = key.split('__')[-1]
            obj_dict[new_key] = obj_dict[key]
            obj_dict.pop(key)

        return obj_dict

    def from_dict(self, values: dict):
        obj_dict = self.to_dict()

        for key in obj_dict:
            dict_value = values.get(key, None)
            value_type = type(dict_value)

            if value_type not in [list] and dict_value is not None:
                self.__setattr__(key, dict_value)

        return self

    @classmethod
    def round_to_two_decimal(cls, value) -> float:
        if type(value) == str:
            value = float(value)

        return round(value, 2)
