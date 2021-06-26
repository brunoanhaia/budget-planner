import os
import json
from wrapper.file_helper import FileHelper
import cert_generator
import pandas as pd
from pynubank import Nubank, MockHttpClient
from datetime import datetime
from dataclasses import dataclass

from sqlalchemy.sql.sqltypes import Boolean, String


class NuBankWrapper:

    def __init__(self, cpf="", password="", mock: bool = True, data_dir: String = 'cache'):
        self.mock = mock
        self.user = cpf
        self.file_helper = FileHelper(self.user)
        self.password = password
        self.bills: any
        self.account_statements: any
        self.refresh_token: any
        self.data_dir = data_dir

        if (mock):
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
        if (self.mock):
            return self.nu.authenticate_with_qr_code(self.user, self.password, "qualquer-coisa")
        else:
            uuid, qr_code = self.nu.get_qr_code()
            qr_code.print_ascii(invert=True)
            input('Apos escanear o QRCode pressione enter para continuar')
            return self.nu.authenticate_with_qr_code(self.user, self.password, uuid)

    def authenticate_with_certificate(self):
        self.refresh_token = self.nu.authenticate_with_cert(
            self.user, self.password, self.file_helper.certificate.path)

        self.save_to_file(self.file_helper.token.path,
                          self.refresh_token, format=None)

        return self.refresh_token

    def authenticate_with_token(self):
        token_file_name = self.file_helper.token.path
        with open(token_file_name) as refresh_file:
            refresh_token = json.load(refresh_file)
            cert_path = self.file_helper.certificate.path

            return self.nu.authenticate_with_refresh_token(refresh_token, cert_path)

    def authenticate_with_token_string(self, token: String):
        cert_path = self.file_helper.certificate.path
        return self.nu.authenticate_with_refresh_token(token, cert_path)

    def get_account_balance(self):
        return self.nu.get_account_balance()

    def get_account_statements(self, savefile: bool = False):
        self.account_statements = self.nu.get_account_statements()

        if savefile:
            current_date = datetime.now()
            # folder_path = self._get_base_path("account_statements")
            file_path = self.file_helper.account_statement.get_custom_path(
                current_date.strftime("%Y-%m-%d_%H-%M-%S"))

            self.save_to_file(file_path, self.account_statements)

        return self.account_statements

    def get_card_bills(self, details: bool, savefile: bool = False):
        self.bills = self.nu.get_bills()
        for bill in self.bills:

            # This will get the bill datails (transactions) from open and closed bills
            if (details and bill['state'] != 'future'):
                bill_detais = self.nu.get_bill_details(bill)['bill']
                bill['details'] = bill_detais['line_items']

                for transaction in bill['details']:
                    transaction['amount'] = transaction['amount'] / 100

            if 'summary' in bill:
                summary = bill['summary']
                # By default, nubank api provide the values as integers, so we need to convert to divide by 100.
                summary['past_balance'] = summary['past_balance']/100
                summary['total_balance'] = summary['total_balance']/100
                summary['total_cumulative'] = summary['total_cumulative']/100
                summary['paid'] = summary['paid']/100
                summary['minimum_payment'] = summary['minimum_payment']/100

            if savefile:
                close_date = datetime.strptime(
                    bill['summary']['close_date'], "%Y-%m-%d")
                # folder_path =  self._get_base_path("card_bills")
                file_path = self.file_helper.card_bill.get_custom_path(
                    close_date.strftime("%Y-%m"))

                self.save_to_file(file_path, bill)

        return self.bills

    def retrieve_card_bill_from_cache(self) -> list[dict]:
        base_path = self.file_helper.card_bill.path
        files_list = self.file_helper.card_bill._get_files()
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

                if '_links' in file_content and 'self' in file_content['_links'] and 'href' in file_content['_links']['self']:
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

        return card_bills_list

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
        account_feed = self.nu.get_account_feed()
        self.save_to_file(self.file_helper.account_feed.path, account_feed)

        return account_feed

    def generate_monthly_account_summary(self) -> dict:
        if self.account_statements == None:
            self.get_account_statements()
        
        values = self.account_statements

        for v in values:
            v['type'] = v['__typename']

        df = pd.DataFrame.from_dict(values)
        df['postDate'] = pd.to_datetime(df['postDate'], format='%Y-%m-%d')
        df.loc[df.type == 'TransferInEvent', "credito"] = df.amount
        df.loc[df.type != 'TransferInEvent', "debito"] = df.amount

        resampled_data = df.resample('MS', on='postDate').agg(
            {'credito': 'sum', 'debito': 'sum'})
        resampled_data['saldo'] = resampled_data.credito - \
            resampled_data.debito

        print(resampled_data)
        resampled_data = resampled_data.reset_index()

        print(resampled_data)

        account_statement_summary = resampled_data.to_json(
            date_format='iso', orient='records')

        file_path = self.file_helper.account_statement_summary.path
        self.save_to_file(file_path, account_statement_summary)

        return account_statement_summary

    def save_to_file(self, file_name, content, format='json'):
        dirname = os.path.dirname(file_name)
        name = f'{os.path.basename(file_name)}'

        if format != None:
            name = f'{name}.{format}'

        if os.path.exists(dirname) == False:
            os.makedirs(dirname)

        with open(os.path.join(dirname, name), 'w+', encoding='utf-8') as outfile:
            json.dump(content, outfile, ensure_ascii=False, indent='\t')

    def generate_cert(self, save_file=True):
        cert_generator.run(self.cpf, self.password, save_file=save_file)
