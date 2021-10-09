import json
import os
import enum
from wrapper.models import User, UserDataCache
from wrapper.models.nubank_card_bill import NuBankCardBill
from wrapper.providers import NuBankApiProvider
from wrapper.providers.cache_data_provider import CacheDataProvider
from wrapper.utils.utils import card_bill_add_details_from_card_statement, transaction_add_details_from_card_statement

import cert_generator
import pandas as pd

from .utils import ConfigLoader, planify_array
from datetime import datetime
from pandas.core.frame import DataFrame
from pynubank import MockHttpClient, Nubank
from wrapper.utils import FileHelper
from .database_manager import DatabaseManager


class NuBankWrapper:

    def __init__(self, user: User, password="", mock: bool = True, data_dir: str = 'cache'):
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
        if self.cache_data.user != None:
            return self.cache_data.user
        return User()

    @user.setter
    def user(self, value: User):
        if self.cache_data.user == None:
            self.cache_data.user = User(value.cpf, value.nickname)

        self.file_helper = FileHelper(value.cpf)

    @property
    def nickname(self):
        return self.user.nickname

    def authenticate_with_qr_code(self):
        if self.mock:
            return self.nu.authenticate_with_qr_code(self.user, self.password, "qualquer-coisa")
        else:
            uuid, qr_code = self.nu.get_qr_code()
            qr_code.print_ascii(invert=True)
            input('Apos escanear o QRCode pressione enter para continuar')
            return self.nu.authenticate_with_qr_code(self.user, self.password, uuid)

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

            return self.nu.authenticate_with_refresh_token(refresh_token, cert_path)

    def authenticate_with_token_string(self, token: str):
        try:
            cert_path = self.file_helper.certificate.path
            return self.nu.authenticate_with_refresh_token(token, cert_path)
        except:
            return self.authenticate_with_certificate()

    def get_account_balance(self):
        return self.nu.get_account_balance()

    def get_account_statements(self, save_file: bool = True):
        self.cache_data.account.statements = self.nu.get_account_statements()

        if save_file:
            current_date = datetime.now()
            file_path = self.file_helper.account_statement.get_custom_path(
                current_date.strftime("%Y-%m-%d_%H-%M-%S"))

            FileHelper.save_to_file(
                file_path, self.cache_data.account.statements)

        return self.cache_data.account.statements

    def get_card_bills(self, details: bool, save_file: bool = True):
        raw_data = self.nu.get_bills()

        bills: list[NuBankCardBill] = [NuBankCardBill().from_dict(card_bill) for card_bill in raw_data]

        amount_per_tag_list: list[dict] = []

        for bill in bills:
            
            # Link bill to user
            bill.cpf = self.user.cpf

            # Retrieving the bill details (transactions) from open and closed bills
            if details and bill.state != 'future':

                transactions_list = bill.get_transactions()

                # Get amount per tag in each bill and  and to the list
                amount_per_tag = transactions_list.group_tags_and_get_amount_from_transactions()
                if amount_per_tag is not None:
                    amount_per_tag_list.append(amount_per_tag.to_json())

            if save_file:
                close_date = datetime.strptime(
                    bill.close_date, "%Y-%m-%d")
                file_path = self.file_helper.card_bill.get_custom_path(
                    close_date.strftime("%Y-%m"))

                FileHelper.save_to_file(file_path, bill.to_json())

        # Storing the data in the class instance for future use
        self.cache_data.card.bill_list = bills

        # Save amount per tag in a file
        self.file_helper.save_to_file(
            self.file_helper.card_bill_amount_per_tag.path, amount_per_tag_list)

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
            with open(os.path.join(base_path, file), 'r', encoding='utf8') as f:
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
                        statement[key]['charge_amount'] = statement[key]['amount']/100
                        statement[key]['total_amount'] = statement['amount']/100

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

    def generate_account_monthly_summary(self) -> dict:
        # It will retrieve new account statements if it wasn't retrieved before.
        if self.cache_data.account.statements is None:
            self.get_account_statements(save_file=True)

        values = self.cache_data.account.statements

        # Still not sure why, but i cannot access __typename directly with pandas, so I'm changing it to type only
        for v in values:
            v['type'] = v['__typename']

        df = pd.DataFrame.from_dict(values)

        # Transforming string to datetime for easy grouping
        df['ref_date'] = pd.to_datetime(df['postDate'], format='%Y-%m-%d')
        df.loc[df.type == 'TransferInEvent', "credit"] = df.amount
        df.loc[df.type != 'TransferInEvent', "debit"] = df.amount

        # Resampling data and grouping by ref_date
        rdf: DataFrame = df.resample('MS', on='ref_date').agg(
            {'credit': 'sum', 'debit': 'sum'})
        rdf['balance'] = rdf.credit - rdf.debit
        rdf['total'] = rdf['balance'].cumsum()
        rdf['cpf'] = self.user

        # Rounding everything with 2 decimal places
        rdf = rdf.round(2)

        # Transforming the ref_date index back to column and to the appropriate format
        rdf.reset_index(inplace=True)
        rdf['ref_date'] = rdf["ref_date"].dt.strftime("%Y-%m-%d")

        # Converting dataframe to dictionary
        self.cache_data.account.monthly_summary_list = rdf.to_dict(
            orient='records')

        file_path = self.file_helper.account_monthly_summary.path
        FileHelper.save_to_file(
            file_path, self.cache_data.account.monthly_summary_list)

        return self.cache_data.account.monthly_summary_list

    def generate_cert(self, save_file=True):
        cert_generator.run(self.user, self.password, save_file=save_file)

    def sync(self):
        self.database_manager.sync(self.cache_data)
