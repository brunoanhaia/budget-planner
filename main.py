import json
import os
import argparse
from helpers import Helper
from wrapper.nubank import NuBankWrapper
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from getpass import getpass
from models import Base

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument('--reset_database', metavar='reset_database', type=bool, default=False)
parser.add_argument('--from_cache', metavar='from_cache', type=bool, default=False)
parser.add_argument('--mock', metavar='mock', type=bool, default=False)

args, remaining = parser.parse_known_args()

# Json .env file configuration
config_file = 'env.json'
config = Helper.load_json_config(config_file)
mysql_config = config['mysqlConfig']

# MySQL Connection String
engine = create_engine(
    f"mysql+mysqlconnector://{mysql_config['user']}:{mysql_config['password']}@{mysql_config['host']}:{mysql_config['port']}/{mysql_config['database']}")

for user in config['users']:

    nu = NuBankWrapper(mock=args.mock, data_dir=config['cachedir'])
    Session = sessionmaker(bind=engine)
    global_session = Session()

    if 'cpf' not in user:
        print('Please insert the CPF property on the user field')
        break
    else:
        nu.user = user['cpf']

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
            Helper.save_json_config(config_file, config)
        else:
            print('Sorry! We need the token to proceed')
            break

    if not args.from_cache:
        nu.authenticate_with_token_string(user['token'])
        nu.get_account_feed()
        nu.get_account_statements()
        nu.get_card_statements()
        nu.get_card_feed()
        nu.get_card_bills(details = True, savefile = True)

    if args.reset_database:
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)


    nu.generate_monthly_account_summary()

    # card_bills = nu.retrieve_card_bill_from_cache()

    # Helper.update_database_card_bills(global_session, card_bills)
