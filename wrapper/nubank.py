import json
import os
import enum

from numpy import result_type
from wrapper.utils.config_loader import ConfigLoader
import cert_generator
import pandas as pd

from datetime import datetime
from pandas.core.frame import DataFrame
from pynubank import MockHttpClient, Nubank
from wrapper.file_helper import FileHelper
from .database_manager import DatabaseManager


class CachedDataEnum(enum.Enum):
    AccountStatements = "account_statements"
    User = 'user'
    CardBill = 'card_bills'
    AccountFeed = 'account_feed'
    AccountMonthlySummary = 'account_monthly_summary'
    CardFeed = 'card_feed'
    CardStatements = 'card_statements'


class NuBankWrapper:

    def __init__(self, cpf="", password="", mock: bool = True, data_dir: str = 'cache'):
        self.cached_data = {}
        self.mock = mock
        self.user = cpf
        self.file_helper = FileHelper(self.user)
        self.database_manager = DatabaseManager
        self.password = password
        self.refresh_token: str = ''
        self.data_dir = data_dir

        if mock:
            self.nu = Nubank(MockHttpClient())
        else:
            self.nu = Nubank()

    @property
    def user(self):
        if CachedDataEnum.User.value in self.cached_data and 'id' in self.cached_data[CachedDataEnum.User.value]:
            return self.cached_data[CachedDataEnum.User.value]['id']
        return ''

    @user.setter
    def user(self, value):
        if CachedDataEnum.User.value not in self.cached_data:
            self.cached_data[CachedDataEnum.User.value] = {}

        self.cached_data[CachedDataEnum.User.value]['id'] = value
        self.file_helper = FileHelper(value)

    @property
    def nickname(self):
        return self.cached_data[CachedDataEnum.User.value]['nickname']

    @nickname.setter
    def nickname(self, value):
        if CachedDataEnum.User.value not in self.cached_data:
            self.cached_data[CachedDataEnum.User.value] = {}

        self.cached_data[CachedDataEnum.User.value]['nickname'] = value

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
            'type': CachedDataEnum.User.value,
            'key': self.user,
            'update_values': {
                'token': self.refresh_token
            }
        })

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
        try:
            cert_path = self.file_helper.certificate.path
            return self.nu.authenticate_with_refresh_token(token, cert_path)
        except:
            return self.authenticate_with_certificate()

    def get_account_balance(self):
        return self.nu.get_account_balance()

    def get_account_statements(self, save_file: bool = True):
        self.cached_data[CachedDataEnum.AccountStatements.value] = self.nu.get_account_statements()

        if save_file:
            current_date = datetime.now()
            file_path = self.file_helper.account_statement.get_custom_path(
                current_date.strftime("%Y-%m-%d_%H-%M-%S"))

            self.save_to_file(
                file_path, self.cached_data[CachedDataEnum.AccountStatements.value])

        return self.cached_data[CachedDataEnum.AccountStatements.value]

    def get_card_bills(self, details: bool, save_file: bool = True):
        bills: list[dict] = self.nu.get_bills()
        for bill in bills:

            # Link bill to user
            bill['cpf'] = self.user

            # Retrieving the bill details (transactions) from open and closed bills
            if details and bill['state'] != 'future':
                bill_detais = self.nu.get_bill_details(bill)['bill']
                bill['details'] = bill_detais.get('line_items', None)
                bill['nubank_id'] = bill_detais.get('id', None)

                if '_links' in bill and 'self' in bill['_links'] and 'href' in bill['_links']['self']:
                    bill['link_href'] = bill['_links']['self']['href']

                for transaction in bill['details']:
                    transaction['amount'] = transaction['amount']/100
                    transaction['nubank_id'] = transaction['id']
                    transaction.pop('id')

                    if 'href' in transaction and 'transaction_id' not in transaction:
                        transaction['transaction_id'] = transaction['href'].split(
                            '/')[-1]

                    transaction = self.__transaction_add_details_from_card_statement(
                        transaction)

                self.__card_bill_add_details_from_card_statement(bill)
                self.__group_tags_and_get_amount_from_card_bill(bill)

            if 'summary' in bill:
                summary = bill['summary']

                # By default, nubank api provide the values as integers, so we need to convert and divide the value
                # by 100.
                summary['past_balance'] = summary['past_balance']/100
                summary['total_balance'] = summary['total_balance']/100
                summary['total_cumulative'] = summary['total_cumulative']/100
                summary['paid'] = summary['paid']/100
                summary['minimum_payment'] = summary['minimum_payment']/100

            self.__planify_summary(bill)

            if save_file:
                close_date = datetime.strptime(
                    bill['close_date'], "%Y-%m-%d")
                file_path = self.file_helper.card_bill.get_custom_path(
                    close_date.strftime("%Y-%m"))

                self.save_to_file(file_path, bill)

        # Storing the data in the class instance for future use
        self.cached_data[CachedDataEnum.CardBill.value] = bills

        return bills

    def retrive_from_cache(self, type: CachedDataEnum) -> list[dict]:
        file_path = getattr(self.file_helper, type.value).get_complete_path()

        with open(file_path, 'r', encoding='utf8') as f:
            file_content = json.load(f)

            self.cached_data[type.value] = file_content

            return file_content

    def retrieve_card_bill_from_cache(self) -> list[dict]:
        base_path = self.file_helper.card_bill.path
        files_list = self.file_helper.card_bill.files
        card_bills_list = []

        for file in files_list:
            with open(os.path.join(base_path, file), 'r', encoding='utf8') as f:
                file_content = json.load(f)

                card_bills_list.append(file_content)

        self.cached_data[CachedDataEnum.CardBill.value] = card_bills_list

        return self.cached_data[CachedDataEnum.CardBill.value]

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

        file_path = self.file_helper.card_statements.path
        self.save_to_file(file_path, card_statements)

        return card_statements

    def get_card_feed(self):
        card_feed = self.nu.get_card_feed()

        file_path = self.file_helper.card_feed.path

        self.save_to_file(file_path, card_feed)

        return card_feed

    def get_account_feed(self):
        self.cached_data[CachedDataEnum.AccountFeed.value] = self.nu.get_account_feed(
        )
        self.save_to_file(self.file_helper.account_feed.path,
                          self.cached_data[CachedDataEnum.AccountFeed.value])

        return self.cached_data[CachedDataEnum.AccountFeed.value]

    def generate_card_transactions_by_tag(self):
        card_bills = self.cached_data[CachedDataEnum.CardBill.value]
        card_bill_with_details = [
            bill for bill in card_bills if 'details' in bill]

        for card_bill in card_bill_with_details:
            card_bill = self.__group_tags_and_get_amount_from_card_bill(
                card_bill)

        self.cached_data[CachedDataEnum.CardBill.value] = card_bills

    def __group_tags_and_get_amount_from_card_bill(self, card_bill):
        transactions_with_tag = [
            transaction for transaction in card_bill['details'] if 'tags' in transaction]

        if len(transactions_with_tag) > 0:
            amount_per_tag = self.__get_amount_per_tag(
                transactions_with_tag)
            card_bill['amount_per_tag'] = amount_per_tag

        return card_bill

    def __get_amount_per_tag(self, transactions_list: list[dict]) -> dict:
        amount_per_tag_dict = {}

        for transaction in transactions_list:
            tags = self.__planify_array(transaction['tags'])
            amount = transaction['amount']

            for tag in tags:
                if tag in amount_per_tag_dict:
                    amount_per_tag_dict[tag] += amount
                else:
                    amount_per_tag_dict[tag] = amount

        return amount_per_tag_dict

    def __planify_array(self, array: list):
        result = []
        for elem in array:
            if type(elem) is list:
                self.__planify_array(elem)
            if type(elem) is str:
                result.append(elem)
            else:
                result.extend(elem)

        return result

    def __card_bill_add_details_from_card_statement(self, card_bill: dict):

        if 'details' in card_bill:
            for transaction in card_bill['details']:
                transaction = self.__transaction_add_details_from_card_statement(
                    transaction)

        return card_bill

    def __transaction_add_details_from_card_statement(self, transaction: dict):

        if CachedDataEnum.CardStatements.value not in self.cached_data:
            self.retrive_from_cache(CachedDataEnum.CardStatements)

        card_statements = self.cached_data[CachedDataEnum.CardStatements.value]

        statement = [statement for statement in card_statements if (
            'transaction_id' in transaction and statement['id'] == transaction['transaction_id'])]

        if statement != None and len(statement) > 0:
            detail_filter_list = ['tags', 'charges']

            for detail in detail_filter_list:
                st = statement[0]

                if detail in st:
                    transaction[detail] = st[detail]

        return transaction

    def generate_account_monthly_summary(self) -> dict:
        # It will retrieve new account statements if it wasn't retrieved before.
        if self.cached_data[CachedDataEnum.AccountStatements.value] is None:
            self.get_account_statements(save_file=True)

        values = self.cached_data[CachedDataEnum.AccountStatements.value]

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
        self.cached_data[CachedDataEnum.AccountMonthlySummary.value] = rdf.to_dict(
            orient='records')

        file_path = self.file_helper.account_monthly_summary.path
        self.save_to_file(
            file_path, self.cached_data[CachedDataEnum.AccountMonthlySummary.value])

        return self.cached_data[CachedDataEnum.AccountMonthlySummary.value]

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

    def __planify_summary(self, values: dict):

        # Iterate over each key in the summary dictionary
        for key in values['summary']:
            inner_value = values['summary'][key]
            values[key] = inner_value

        values.pop('summary')
