import argparse

def parse_args():
    # Argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', metavar='user', type=str, default='')

    args, remaining = parser.parse_known_args()
    return args

def get_data(user: str):
    from src.nubank import NuBankWrapper
    nu = NuBankWrapper(user)
    nu.authenticate_with_token_string()
    nu.account_sync()
    nu.card_sync()

if __name__ == '__main__':
    args =  parse_args()
    get_data(args.user)