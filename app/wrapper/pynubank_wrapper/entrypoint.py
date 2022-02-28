import argparse
import pathlib
import sys
sys.path.append(str(pathlib.Path(__file__).parent.absolute()))

from nubank import NuBankWrapper


def parse_args():
    # Argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', metavar='user', type=str, default='')
    parser.add_argument('--cache', metavar='cache', type=bool, default=False)


    args, remaining = parser.parse_known_args()
    return args

def get_data(user: str):
    nu = NuBankWrapper(user)
    nu.authenticate_with_token_string()
    nu.account_sync()
    nu.card_sync()

    return nu.cache.data

def get_cache_data(user: str):
    nu = NuBankWrapper(user)
    nu.get_cache_data()

if __name__ == '__main__':
    args =  parse_args()
    
    if (args.cache):
        get_cache_data(args.user)
    else:
        get_data(args.user)