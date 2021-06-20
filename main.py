import os
from helpers import Helper
from wrapper import NuBankWrapper
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from getpass import getpass
from models import Base

# Create a .env config file
config_file = 'env.json'

# This script uses the token and certificate authentication
config = Helper.load_json_config(config_file)
mysql_config = config['mysqlConfig']

engine = create_engine(
    f"mysql+mysqlconnector://{mysql_config['user']}:{mysql_config['password']}@{mysql_config['host']}:{mysql_config['port']}/{mysql_config['database']}")

for user in config['users']:

    nu = NuBankWrapper(mock=False, data_dir=config['cachedir'])
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

    nu.authenticate_with_token_string(user['token'])

    nu.get_card_bills(details = True, savefile = True)

    # Uncomment this line to drop the database
    # Base.metadata.drop_all(engine)
    # Uncomment this line to create the database
    # Base.metadata.create_all(engine)

    card_bills = nu.retrieve_card_bill_from_cache()

    Helper.update_database_card_bills(global_session, card_bills)
