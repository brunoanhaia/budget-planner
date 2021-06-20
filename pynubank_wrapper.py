import os
import json
from pynubank import Nubank, MockHttpClient
from datetime import datetime
from certificate_generator_script import CertificateGenerator


class NuBankWrapper:
    data_dir = 'data'

    def __init__(self, cpf="", password="", mock: bool = True):
        self.mock = mock
        self.user = cpf
        self.password = password
        self.bills: any
        self.refresh_token: any

        if (mock):
            self.nu = Nubank(MockHttpClient())
        else:
            self.nu = Nubank()

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
            self.user, self.password, self._get_cert_path())

        self.save_to_file(f'{self._get_prefix_user()}', self.refresh_token, format='token')

        return self.refresh_token

    def authenticate_with_token(self):
        token_file_name = "{prefix}_refresh_token.txt".format(
            prefix=self._get_prefix_user())
        with open(token_file_name) as refresh_file:
            refresh_token = json.load(refresh_file)
            cert_path = self._get_cert_path()
            return self.nu.authenticate_with_refresh_token(refresh_token, cert_path)

    def get_account_balance(self):
        return self.nu.get_account_balance()

    def get_account_statements(self, savefile: bool = False):
        account_statements = self.nu.get_account_statements()

        if savefile:
            current_date = datetime.now()
            folder_path = os.path.join(
                self._get_prefix_user(), "account_statements")
            file_path = os.path.join(
                folder_path, current_date.strftime("%Y-%m-%d_%H-%M-%S"))

            self.save_to_file(file_path, account_statements)
        return account_statements

    def save_to_file(self, file_name, content, format='json'):
        dirname = os.path.dirname(file_name)

        if os.path.exists(dirname) == False:
            os.makedirs(dirname)

        with open('{name}.{format}'.format(name=file_name, format=format), 'w+', encoding='utf-8') as outfile:
            json.dump(content, outfile, ensure_ascii=False, indent='\t')

    def get_card_bills(self, details: bool, savefile: bool = False):
        self.bills = self.nu.get_bills()
        if details:
            for bill in self.bills:

                if (bill['state'] != 'future'):
                    bill_detais = self.nu.get_bill_details(bill)['bill']
                    bill['details'] = bill_detais['line_items']

                if savefile:
                    close_date = datetime.strptime(
                        bill['summary']['close_date'], "%Y-%m-%d")
                    folder_path = os.path.join(
                        self._get_prefix_user(), "card_bills")
                    file_path = os.path.join(
                        folder_path, close_date.strftime("%Y-%m"))

                    self.save_to_file(file_path, bill)

        return self.bills

    def retrieve_card_bill_from_cache(self) -> list[dict]:
        base_path = f'{self.user}/card_bills'
        files_list = os.listdir(base_path)
        card_bills_list = []

        for file in files_list:
            with open(os.path.join(base_path, file), 'r', encoding='utf8') as f:
                file_content = json.load(f)
                card_bill = {
                    'nubank_id' : file_content.get('id', None),
                    'cpf' : self.user,
                    'due_date' : file_content['summary'].get('due_date', None),
                    'close_date' : file_content['summary'].get('close_date', None),
                    'past_balance' : file_content['summary'].get('past_balance', None),
                    'effective_due_date' : file_content['summary'].get('effective_due_date', None),
                    'total_balance' : file_content['summary'].get('total_balance', None),
                    'interest_rate' : file_content['summary'].get('interest_rate', None),
                    'interest' : file_content['summary'].get('interest', None),
                    'total_cumulative' : file_content['summary'].get('total_cumulative', None),
                    'paid' : file_content['summary'].get('paid', None),
                    'minimum_payment' : file_content['summary'].get('minimum_payment', None),
                    'open_date' : file_content['summary'].get('open_date', None),
                }

                if '_links' in file_content and 'self' in file_content['_links'] and 'href' in file_content['_links']['self']:
                    card_bill['link_href'] = file_content['_links']['self']['href']

                if 'details' in file_content:

                    for t in file_content['details']:
                        transaction = {
                            'nubank_id' : t['id'],
                            'category' : t.get('category', None),
                            'amount' : t.get('amount', None),
                            'transaction_id' : t.get('transaction_id', None),
                            'index' : t.get('index', None),
                            'charges' : t.get('charges', None),
                            'type' : t.get('type', None),
                            'title' : t.get('title', None),
                            'href' : t.get('href', None),
                            'post_date' : t.get('post_date', None),
                        }

                        if 'transactions' not in card_bill:
                            card_bill['transactions'] = []
                        card_bill['transactions'].append(transaction)

                card_bills_list.append(card_bill)

        return card_bills_list

    def _get_cert_path(self):
        return "./{}_cert.p12".format(self.user)

    def _get_prefix_user(self):
        return "{}".format(self.user)

    def generate_cert(self, save_file = True):
        CertificateGenerator.run(self.cpf, self.password, save_file=save_file)
