import json
import os
import cert_generator
from datetime import datetime
from .models import AccountStatement, NuBankCardBill, User
from .providers import NuBankApiProvider, CacheDataProvider
from .utils import ConfigLoader, FileHelper
from .database_manager import DatabaseManager


class NuBankWrapper:

    def __init__(self, user: User, password="", mock: bool = True,
                 data_dir: str = 'cache'):
        self.cache_data = CacheDataProvider.instance().current
        self.mock = mock
        self.user: User = user
        self.file_helper = FileHelper(self.user.cpf)
        self.database_manager = DatabaseManager
        self.password = password
        self.refresh_token: str = ''
        self.data_dir = data_dir

        self.nu = NuBankApiProvider.instance().nu

    @property
    def user(self):
        if self.cache_data.user is not None:
            return self.cache_data.user
        return User()

    @user.setter
    def user(self, value: User):
        if self.cache_data.user is None:
            self.cache_data.user = User(value.cpf, value.nickname)

        self.file_helper = FileHelper(value.cpf)

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
        except:
            return self.authenticate_with_certificate()

    def get_account_balance(self):
        return self.nu.get_account_balance()

    def get_account_statements(self, save_file: bool = True):
        return AccountStatement(self.user.cpf).get_data()

    def get_card_bills(self, details: bool, save_file: bool = True):
        raw_data = self.nu.get_bills()

        bills: list[NuBankCardBill] = [NuBankCardBill().from_dict(card_bill)
                                       for card_bill in raw_data]

        amount_per_tag_list: list[dict] = []

        for bill in bills:

            # Link bill to user
            bill.cpf = self.user.cpf

            # Retrieving the bill details (transactions) from open and closed
            # bills
            if details and bill.state != 'future':

                transactions_list = bill.get_transactions()

                # Get amount per tag in each bill and  and to the list
                amount_per_tag = transactions_list.group_tags_amount()
                if amount_per_tag is not None:
                    amount_per_tag_list.append(amount_per_tag.to_dict())

            if save_file:
                close_date = datetime.strptime(
                    bill.close_date, "%Y-%m-%d")
                file_path = self.file_helper.card_bill.get_custom_path(
                    close_date.strftime("%Y-%m"))

                FileHelper.save_to_file(file_path, bill.to_dict())

        # Storing the data in the class instance for future use
        self.cache_data.card.bill_list = bills

        # Save amount per tag in a file
        self.file_helper.save_to_file(
            self.file_helper.card_bill_amount_per_tag.path,
            amount_per_tag_list)

        return bills

    # Todo: Move to base class
    def retrive_from_cache(self, type: None) -> list[dict]:
        file_path = getattr(self.file_helper, type.value).get_complete_path()

        with open(file_path, 'r', encoding='utf8') as f:
            file_content = json.load(f)

            self.cache_data[type.value] = file_content

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

        self.cache_data.card.bill_list = card_bills_list

        return self.cache_data.card.bill_list

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
        self.cache_data.card.statements = card_statements
        file_path = self.file_helper.card_statements.path
        FileHelper.save_to_file(file_path, card_statements)

        return card_statements

    def get_card_feed(self):
        card_feed = self.nu.get_card_feed()

        file_path = self.file_helper.card_feed.path

        FileHelper.save_to_file(file_path, card_feed)

        return card_feed

    def get_account_feed(self):
        self.cache_data.account.feed = self.nu.get_account_feed(
        )
        FileHelper.save_to_file(self.file_helper.account_feed.path,
                                self.cache_data.account.feed)

        return self.cache_data.account.feed

    def generate_cert(self, save_file=True):
        cert_generator.run(self.user, self.password, save_file=save_file)

    def sync(self):
        self.database_manager.sync(self.cache_data)
