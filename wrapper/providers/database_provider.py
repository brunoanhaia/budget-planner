import os
import pygsheets
from pygsheets import Spreadsheet


class DatabaseProvider:
    _instance = None

    def __init__(self) -> None:
        # Todo: move credentials to environment variables
        current_dir = os.getcwd()
        self.client = pygsheets.authorize(client_secret='cache/client_secret.json', credentials_directory='cache')
        self.__init_default_sheet()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init_default_sheet(self):
        # Todo: check if sheet exists and move sheet name to constant
        self.__default_sheet = self.client.create('expense-manager/expense_manager')

    @property
    def default_sheet(self) -> Spreadsheet:
        return self.__default_sheet
