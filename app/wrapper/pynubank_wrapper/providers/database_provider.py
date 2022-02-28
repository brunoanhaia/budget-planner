import pygsheets
from pygsheets import Spreadsheet
from pygsheets.exceptions import SpreadsheetNotFound, WorksheetNotFound
from pygsheets.worksheet import Worksheet
from decouple import config
from pathlib import Path

from utils.constants import Constants


class DatabaseProvider:
    _instance = None

    def __init__(self) -> None:
        cache_dir_path: Path = config(Constants.Wrapper.cache_dir_path, cast=Path)
        service_account_file = cache_dir_path.joinpath('service_secret.json')

        self.client = pygsheets.authorize(service_account_file=service_account_file, credentials_directory=cache_dir_path)
        self.__init_default_sheet()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init_default_sheet(self):
        # Todo: check if sheet exists and move sheet name to constant
        try:
            self.__default_sheet = self.client.open_by_key('1AIj61NNfIjpnhUodnR0QMdCih7En6o5KZwirsxgN30c')
        except SpreadsheetNotFound:
            self.__default_sheet = self.client.create('expense-manager', None, None, 'expense-manager')

    @property
    def default_sheet(self) -> Spreadsheet:
        return self.__default_sheet

    def get_worksheet(self, name, property='title') -> Worksheet:
        try:
            return self.default_sheet.worksheet(property, name)
        except WorksheetNotFound:
            return self.default_sheet.add_worksheet(name)
