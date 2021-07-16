import json
import os
import cert_generator
import pandas as pd

from datetime import datetime
from pandas.core.frame import DataFrame
from pynubank import MockHttpClient, Nubank
from wrapper.file_helper import FileHelper
from .database_manager import DatabaseManager


class NuBankWrapper:

    def __init__(self, cpf="", password="", mock: bool = True, data_dir: str = 'cache'):
        self.mock = mock
        self.user = cpf
        self.file_helper = FileHelper(self.user)
        self.database_manager = DatabaseManager
        self.password = password
        self.cached_data = {}
        self.refresh_token: str = ''
        self.data_dir = data_dir

        if mock:
            self.nu = Nubank(MockHttpClient())
        else:
            self.nu = Nubank()

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        self._user = value
        self.file_helper = FileHelper(self._user)

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

        self.save_to_file(self.file_helper.token.path,
                          self.refresh_token, file_format='')

        return self.refresh_token

    def authenticate_with_token(self):
        token_file_name = self.file_helper.token.path
        with open(token_file_name) as refresh_file:
            refresh_token = json.load(refresh_file)
            cert_path = self.file_helper.certificate.path

            return self.nu.authenticate_with_refresh_token(refresh_token, cert_path)

    def authenticate_with_token_string(self, token: str):
        cert_path = self.file_helper.certificate.path
        return self.nu.authenticate_with_refresh_token(token, cert_path)

    def get_account_balance(self):
        return self.nu.get_account_balance()

    def get_account_statements(self, save_file: bool = False):
        self.cached_data['account_statements'] = self.nu.get_account_statements()

        if save_file:
            current_date = datetime.now()
            file_path = self.file_helper.account_statement.get_custom_path(
                current_date.strftime("%Y-%m-%d_%H-%M-%S"))

            self.save_to_file(file_path, self.cached_data['account_statements'])

        return self.cached_data['account_statements']

    def get_card_bills(self, details: bool, save_file: bool = False):
        bills = self.nu.get_bills()
        for bill in bills:

            # Retrieving the bill details (transactions) from open and closed bills
            if details and bill['state'] != 'future':
                bill_detais = self.nu.get_bill_details(bill)['bill']
                bill['details'] = bill_detais['line_items']

                for transaction in bill['details']:
                    transaction['amount'] = transaction['amount'] / 100

            if 'summary' in bill:
                summary = bill['summary']

                # By default, nubank api provide the values as integers, so we need to convert and divide the value
                # by 100.
                summary['past_balance'] = summary['past_balance']/100
                summary['total_balance'] = summary['total_balance']/100
                summary['total_cumulative'] = summary['total_cumulative']/100
                summary['paid'] = summary['paid']/100
                summary['minimum_payment'] = summary['minimum_payment']/100

            # Storing the data in the class instance for future use
            self.cached_data['card_bills'] = bills

            if save_file:
                close_date = datetime.strptime(
                    bill['summary']['close_date'], "%Y-%m-%d")
                # folder_path =  self._get_base_path("card_bills")
                file_path = self.file_helper.card_bill.get_custom_path(
                    close_date.strftime("%Y-%m"))

                self.save_to_file(file_path, bill)

        return bills

    def retrieve_card_bill_from_cache(self) -> list[dict]:
        base_path = self.file_helper.card_bill.path
        files_list = self.file_helper.card_bill.files
        card_bills_list = []

        for file in files_list:
            with open(os.path.join(base_path, file), 'r', encoding='utf8') as f:
                file_content = json.load(f)
                card_bill = {
                    'nubank_id': file_content.get('id', None),
                    'cpf': self.user,
                    'state': file_content.get('state', None),
                    'due_date': file_content['summary'].get('due_date', None),
                    'close_date': file_content['summary'].get('close_date', None),
                    'past_balance': file_content['summary'].get('past_balance', None),
                    'effective_due_date': file_content['summary'].get('effective_due_date', None),
                    'total_balance': file_content['summary'].get('total_balance', None),
                    'interest_rate': file_content['summary'].get('interest_rate', None),
                    'interest': file_content['summary'].get('interest', None),
                    'total_cumulative': file_content['summary'].get('total_cumulative', None),
                    'paid': file_content['summary'].get('paid', None),
                    'minimum_payment': file_content['summary'].get('minimum_payment', None),
                    'open_date': file_content['summary'].get('open_date', None),
                }

                if '_links' in file_content \
                        and 'self' in file_content['_links'] and 'href' in file_content['_links']['self']:
                    card_bill['link_href'] = file_content['_links']['self']['href']

                if 'details' in file_content:

                    for t in file_content['details']:
                        transaction = {
                            'nubank_id': t['id'],
                            'category': t.get('category', None),
                            'amount': t.get('amount', None),
                            'transaction_id': t.get('transaction_id', None),
                            'index': t.get('index', None),
                            'charges': t.get('charges', None),
                            'type': t.get('type', None),
                            'title': t.get('title', None),
                            'href': t.get('href', None),
                            'post_date': t.get('post_date', None),
                        }

                        if 'transactions' not in card_bill:
                            card_bill['transactions'] = []
                        card_bill['transactions'].append(transaction)

                card_bills_list.append(card_bill)

        self.cached_data['card_bills'] = card_bills_list

        return self.cached_data['card_bills']

    def get_card_statements(self):
        card_statements = self.nu.get_card_statements()

        file_path = self.file_helper.card_statements.path
        self.save_to_file(file_path, card_statements)

        return card_statements

    def get_card_feed(self):
        card_feed = self.nu.get_card_feed()

        file_path = self.file_helper.card_feed.path

        self.save_to_file(file_path, card_feed)

        return card_feed

    def get_account_feed(self):
        self.cached_data['account_feed'] = self.nu.get_account_feed()
        self.save_to_file(self.file_helper.account_feed.path,
                          self.cached_data['account_feed'])

        return self.cached_data['account_feed']

    def generate_monthly_account_summary(self) -> dict:
        # It will retrieve new account statements if it wasn't retrieved before.
        if self.cached_data['account_statements'] is None:
            self.get_account_statements(save_file=True)

        values = self.cached_data['account_statements']

        # Still not sure why, but i cannot access __typename directly with pandas, so I'm changing it to type only
        for v in values:
            v['type'] = v['__typename']

        df = pd.DataFrame.from_dict(values)

        # Transforming string to datetime for easy grouping
        df['post_date'] = pd.to_datetime(df['postDate'], format='%Y-%m-%d')
        df.loc[df.type == 'TransferInEvent', "credito"] = df.amount
        df.loc[df.type != 'TransferInEvent', "debito"] = df.amount

        # Resampling data and grouping by post_date
        rdf: DataFrame = df.resample('MS', on='post_date').agg(
            {'credito': 'sum', 'debito': 'sum'})
        rdf['saldo'] = rdf.credito - rdf.debito

        # Rounding everything with 2 decimal places
        rdf = rdf.round(2)

        # Transforming the post_date index back to column and to the appropriate format
        rdf.reset_index(inplace=True)
        rdf['post_date'] = rdf["post_date"].dt.strftime("%Y-%m-%d")

        # Converting dataframe to dictionary
        account_statement_summary = rdf.to_dict(orient='records')

        file_path = self.file_helper.account_statement_summary.path
        self.save_to_file(file_path, account_statement_summary)

        return account_statement_summary

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

    def generate_cert(self, save_file=True):
        cert_generator.run(self.user, self.password, save_file=save_file)

    def sync(self):
        self.database_manager.sync(self.cached_data)
