import os
import argparse
from wrapper import NuBankWrapper, ConfigLoader

from getpass import getpass

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument('--reset_database', metavar='reset_database', type=bool, default=False)
parser.add_argument('--from_cache', metavar='from_cache', type=bool, default=False)
parser.add_argument('--mock', metavar='mock', type=bool, default=False)

args, remaining = parser.parse_known_args()

# Json .env file configuration
config_file = 'env.json'
os.environ['CONFIG_FILE'] = config_file
config = ConfigLoader.load(os.getenv("CONFIG_FILE"))

for user in config['users']:

    nu = NuBankWrapper(mock=args.mock, data_dir=config['cachedir'])

    if 'cpf' not in user:
        print('Please insert the CPF property on the user field')
        break
    else:
        nu.user = user['cpf']
        if 'nickname' in user:
            nu.nickname = user['nickname']

    if not os.path.exists(os.path.join(nu.data_dir, nu.user, f"{nu.user}_cert.p12")):
        print('Certificate not found')

        option = input("Do you want to generate a certificate? Y/N")

        if option == 'Y':
            nu.password = getpass(
                '[>] Enter your password (Used on the app/website): ')
            NuBankWrapper().generate_cert()
        else:
            print('Sorry! We need the certificate to proceed')
            break

    if 'token' not in user:
        print('Token not found!')
        option = input(
            'We need the token to proceed, do you want to generate the token? Y/N')

        if option == 'Y':
            refresh_token = nu.authenticate_with_certificate()
            user['token'] = refresh_token
            ConfigLoader.save(config_file, config)
        else:
            print('Sorry! We need the token to proceed')
            break

    if args.reset_database:
        nu.database_manager.reset()

    if not args.from_cache:
        nu.authenticate_with_token_string(user['token'])
        nu.get_account_feed()
        nu.get_account_statements()
        nu.get_card_statements()
        nu.get_card_feed()
        nu.get_card_bills(details=True, save_file=False)
        nu.generate_account_monthly_summary()

    nu.sync()
