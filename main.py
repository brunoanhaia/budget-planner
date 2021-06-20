
import os
from helpers import Helper
from pynubank_wrapper import NuBankWrapper
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from getpass import getpass
from models import Base

## Create a .env config file
config_file = 'env.json'

# This script uses the token and certificate authentication
config = Helper.load_json_config(config_file)
mysql_config = config['mysqlConfig']

engine = create_engine(f"mysql+mysqlconnector://{mysql_config['user']}:{mysql_config['password']}@{mysql_config['host']}:{mysql_config['port']}/{mysql_config['database']}")

for user in config['users']:
    
    nu = NuBankWrapper(mock=False)
    Session = sessionmaker(bind=engine)
    global_session = Session()

    if 'cpf' not in user:
        print('Please insert the CPF property on the user field')
        break

    if not os.path.exists(f"{user['cpf']}_cert.p12"):
        print('Certificate not found')

        option = input("Do you want to generate a certificate? Y/N")

        if option == 'Y':
            nu.cpf = user['cpf']
            nu.password = getpass('[>] Enter your password (Used on the app/website): ')
            NuBankWrapper().generate_cert()
        else:
            print('Sorry! We need the certificate to proceed')
            break

    if 'token' not in user:
        print('Token not found!')
        option = input('We need the token to proceed, do you want to generate the token? Y/N')

        if option == 'Y':
            refresh_token = nu.authenticate_with_certificate()
            user['token'] = refresh_token
        else:
            print('Sorry! We need the token to proceed')
            break

    nu.authenticate_with_token()
    
    nu.get_card_bills(details = True, savefile = True)

    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    card_bills = nu.retrieve_card_bill_from_cache()

    Helper.update_database_card_bills(global_session, card_bills)
