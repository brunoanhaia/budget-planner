import json
import os
from datetime import datetime

from pynubank.exception import NuException

import cert_generator
from .models import User
from .providers import NuBankApiProvider, CacheDataProvider
from .utils import ConfigLoader, FileHelper


class NuBankWrapper:

    def __init__(self, user, password="", mock: bool = True,
                 data_dir: str = 'cache'):

        # CacheDataProvider.instance().current = UserDataCache()
        self.cache = CacheDataProvider.instance()
        self.cache.set_data(user)

        self.mock = mock
        self.user: str = user
        self.file_helper = FileHelper(self.user)
        self.password = password
        self.refresh_token: str = ''
        self.data_dir = data_dir

        self.nu = NuBankApiProvider.instance().nu

    @property
    def user(self):
        if self.cache.data.user is not None:
            return self.cache.data.user
        return User()

    @user.setter
    def user(self, value: str):
        if self.cache.data.user is None:
            self.cache.data.user = value

        self.file_helper = FileHelper(value)

    @property
    def nickname(self):
        return self.user.nickname

    def authenticate_with_qr_code(self):
        if self.mock:
            return self.nu.authenticate_with_qr_code(self.user, self.password,
                                                     "qualquer-coisa")
        else:
            uuid, qr_code = self.nu.get_qr_code()
            qr_code.print_ascii(invert=True)
            input('Apos escanear o QRCode pressione enter para continuar')
            return self.nu.authenticate_with_qr_code(self.user, self.password,
                                                     uuid)

    def authenticate_with_certificate(self):
        if self.password is None or self.password == '':
            self.password = input("Please insert your password: ")

        self.refresh_token = self.nu.authenticate_with_cert(
            self.user, self.password, self.file_helper.certificate.path)

        ConfigLoader.update(os.getenv("CONFIG_FILE"), {
            'type': 'user',
            'key': self.user,
            'update_values': {
                'token': self.refresh_token
            }
        })

        FileHelper.save_to_file(self.file_helper.token.path,
                                self.refresh_token, file_format='')

        return self.refresh_token

    def authenticate_with_token(self):
        token_file_name = self.file_helper.token.path
        with open(token_file_name) as refresh_file:
            refresh_token = json.load(refresh_file)
            cert_path = self.file_helper.certificate.path

            return self.nu.authenticate_with_refresh_token(refresh_token,
                                                           cert_path)

    def authenticate_with_token_string(self, token: str):
        try:
            cert_path = self.file_helper.certificate.path
            return self.nu.authenticate_with_refresh_token(token, cert_path)
        except NuException:
            return self.authenticate_with_certificate()

    def get_account_balance(self):
        return self.nu.get_account_balance()

    def account_sync(self):
        self.cache.data.account.sync()

    def card_sync(self):
        self.cache.data.card.sync()

    # Todo: Move to base class
    def retrieve_from_cache(self, type: None) -> list[dict]:
        file_path = getattr(self.file_helper, type.value).get_complete_path()

        with open(file_path, 'r', encoding='utf8') as f:
            file_content = json.load(f)

            self.cache[type.value] = file_content

            return file_content

    # Todo: Move to base class
    def retrieve_card_bill_from_cache(self) -> list[dict]:
        base_path = self.file_helper.card_bill.path
        files_list = self.file_helper.card_bill.files
        card_bills_list = []

        for file in files_list:
            with open(os.path.join(base_path, file), 'r',
                      encoding='utf8') as f:

                file_content = json.load(f)

                card_bills_list.append(file_content)

        self.cache.data.card.bills = card_bills_list

        return self.cache.data.card.bills

    def get_card_statements(self):
        card_statements = self.nu.get_card_statements()

        for statement in card_statements:
            if 'details' in statement:
                for key in statement['details'].keys():
                    statement[key] = statement['details'][key]

                    if type(statement[key]) is dict and key == 'charges':
                        statement[key]['charge_amount'] = \
                            statement[key]['amount']/100
                        statement[key]['total_amount'] = \
                            statement['amount']/100

                        statement[key].pop('amount')

                statement.pop('details')

        # Storing the data in the class instance for future use
        self.cache.data.card.statements = card_statements
        file_path = self.file_helper.card_statements.path
        FileHelper.save_to_file(file_path, card_statements)

        return card_statements

    def get_card_feed(self):
        card_feed = self.nu.get_card_feed()

        file_path = self.file_helper.card_feed.path
        FileHelper.save_to_file(file_path, card_feed)

        return card_feed

    def generate_cert(self, save_file=True):
        cert_generator.run(self.user, self.password, save_file=save_file)
