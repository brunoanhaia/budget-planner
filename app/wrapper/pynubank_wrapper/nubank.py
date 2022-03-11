from pynubank.exception import NuException

from utils import FileHelper, Constants, init_config
from utils.user import get_user_password, set_user_token_value, get_user_token_value
from providers import NuBankApiProvider, CacheDataProvider
from decouple import config

class NuBankWrapper:

    def __init__(self, user: str, mock: bool = True, data_dir: str = 'cache'):
        init_config(user)

        self.cache = CacheDataProvider.instance()
        self.cache.set_data(user)

        self.mock = mock
        self.user: str = user
        self.file_helper = FileHelper()
        self.data_dir = data_dir

        self.nu = NuBankApiProvider.instance().nu

    @property
    def user(self):
        if self.cache.data.user is not None:
            return self.cache.data.user

    @user.setter
    def user(self, value: str):
        if self.cache.data.user is None:
            self.cache.data.user = value

    @property
    def nickname(self):
        return self.user.nickname

    def authenticate_with_qr_code(self):
        if self.mock:
            return self.nu.authenticate_with_qr_code(self.user, "", "qualquer-coisa")
        else:
            uuid, qr_code = self.nu.get_qr_code()
            qr_code.print_ascii(invert=True)
            input('Press enter to continue...')
            return self.nu.authenticate_with_qr_code(self.user, get_user_password(self.user), uuid)

    def __authenticate_with_certificate(self):
        cert_path = config(Constants.Wrapper.user_certificate_path)

        # Authenticate with certificate and store the refresh token for future use
        refresh_token = self.nu.authenticate_with_cert(self.user, get_user_password(self.user), cert_path)
        set_user_token_value(self.user, refresh_token)

        return refresh_token

    def authenticate_with_token_string(self):
        try:
            cert_path = config(Constants.Wrapper.user_certificate_path)
            token = get_user_token_value(self.user)

            return self.nu.authenticate_with_refresh_token(token, cert_path)
        except NuException:
            return self.__authenticate_with_certificate()

    def get_account_balance(self):
        return self.nu.get_account_balance()

    def account_sync(self):
        self.cache.data.account.sync()

    def card_sync(self):
        self.cache.data.card.sync()

    def get_cache_data(self):
        self.cache.data.account.load_cache()
        self.cache.data.card.load_cache()

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
        file_path = self.file_helper.card_statements._path
        FileHelper.save_to_file(file_path, card_statements)

        return card_statements

    def get_card_feed(self):
        card_feed = self.nu.get_card_feed()

        file_path = self.file_helper.card_feed._path
        FileHelper.save_to_file(file_path, card_feed)

        return card_feed
