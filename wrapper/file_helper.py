from dataclasses import dataclass
import json
import os

ACCOUNT_FEED = 'account_feed'
ACCOUNT_STATEMENT_FILE = 'account_statement'
ACCOUNT_MONTHLY_SUMMARY_FILE = 'account_statement_summary'
CARD_FEED_FILE = 'card_feed'
CARD_STATEMENTS_FILE = 'card_statements'
CARD_BILL_FOLDER = 'card_bill'
CERTIFICATE_SUFFIX = '_cert.p12'
TOKEN_SUFFIX = '.token'


@dataclass()
class FilePath:

    def __init__(self, path: str, is_folder: bool = False, extension: str = 'json') -> None:
        self.path: str = path
        self.extension: str = extension
        self.__is_folder: bool = is_folder
        self.files = self._get_files()

    def _get_files(self) -> list[str]:
        if self.__is_folder and os.path.exists(self.path):
            return os.listdir(self.path)

    def get_custom_path(self, custom_string: str) -> str:
        return os.path.join(self.path, custom_string)

    def get_complete_path(self) -> str:
        return self.path + '.' + self.extension

@dataclass()
class FileHelper:

    def __init__(self, user: str, cache_dir: str = 'cache') -> None:
        self.user = user
        self.cache_dir = cache_dir
        self.account_feed = FilePath(self.from_base_dir(ACCOUNT_FEED))
        self.account_statement = FilePath(self.from_base_dir(ACCOUNT_STATEMENT_FILE))
        self.account_monthly_summary = FilePath(self.from_base_dir(ACCOUNT_MONTHLY_SUMMARY_FILE))
        self.card_feed = FilePath(self.from_base_dir(CARD_FEED_FILE))
        self.card_statements = FilePath(self.from_base_dir(CARD_STATEMENTS_FILE))
        self.card_bill = FilePath(self.from_base_dir(CARD_BILL_FOLDER), True)
        self.certificate = FilePath(self.from_base_dir(os.path.join(self.user + CERTIFICATE_SUFFIX)))
        self.token = FilePath(self.from_base_dir(os.path.join(self.user + TOKEN_SUFFIX)))

    def from_base_dir(self, path: str):
        return os.path.join(self.cache_dir, self.user, path)
    
    @staticmethod
    def save_to_file(file_name, content, file_format: str = 'json'):
        dirname = os.path.dirname(file_name)
        name = os.path.basename(file_name)

        if file_format != '':
            name = f'{name}.{file_format}'

        if not os.path.exists(dirname):
            os.makedirs(dirname)

        with open(os.path.join(dirname, name), 'w+', encoding='utf-8') as outfile:
            json.dump(content, outfile, ensure_ascii=False, indent='\t')
