import json
from dataclasses import dataclass
from pathlib import Path

from decouple import config
from .constants import Constants

@dataclass()
class WrapperFilePath:

    def __init__(self, path: Path, is_folder: bool = False, extension: str = 'json') -> None:
        self._path: Path = path
        self._extension: str = extension
        self._is_folder: bool = is_folder
        self._files = self._get_files()

    def _get_files(self) -> list[str]:
        if self._is_folder and self._path.exists():
            return self._path.glob('*.*')

    def get_custom_path(self, custom_string: str) -> str:
        return str(self._path.joinpath(custom_string))

    def get_complete_path(self) -> str:
        return str(self._path) + '.' + self._extension

@dataclass()
class FileHelper:

    def __init__(self) -> None:
        self.__user_cache_dir_path: Path = config(Constants.Wrapper.user_cache_dir_path, cast=Path)

        self.account_feed = WrapperFilePath(self.__from_base_dir(Constants.Wrapper.Path.account_feed))
        self.account_statement = WrapperFilePath(self.__from_base_dir(Constants.Wrapper.Path.account_statement_file))
        self.account_monthly_summary = WrapperFilePath(self.__from_base_dir(Constants.Wrapper.Path.account_monthly_summary_file))
        self.card_feed = WrapperFilePath(self.__from_base_dir(Constants.Wrapper.Path.card_feed_file))
        self.card_statements = WrapperFilePath(self.__from_base_dir(Constants.Wrapper.Path.card_statements_file))
        self.card_bill = WrapperFilePath(self.__from_base_dir(Constants.Wrapper.Path.card_bill_folder), True)
        self.card_bill_transactions = WrapperFilePath(self.__from_base_dir(Constants.Wrapper.Path.card_bill_transactions_folder), True)
        self.card_bill_amount_per_tag = WrapperFilePath(self.__from_base_dir(Constants.Wrapper.Path.card_bill_amount_per_tag_file))
        self.card_bill_amount_per_category = WrapperFilePath(self.__from_base_dir(Constants.Wrapper.Path.card_bill_amount_per_category_file))
        self.certificate = WrapperFilePath(config(Constants.Wrapper.user_certificate_path))
    
    @staticmethod
    def save_to_file(file_path: str, content, file_format: str = 'json'):
        dir_path = Path(file_path).parent.absolute()
        file_name = Path(file_path).name

        if file_format != '':
            file_name = f'{file_name}.{file_format}'

        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)

        with open(dir_path.joinpath(file_name).absolute(), 'w+', encoding='utf-8') as outfile:
            json.dump(content, outfile, ensure_ascii=False, indent='\t', default=lambda x: x.to_dict())
            print(f'Saved to {file_path}')

    def __from_base_dir(self, path: str):
        return self.__user_cache_dir_path.joinpath(path)