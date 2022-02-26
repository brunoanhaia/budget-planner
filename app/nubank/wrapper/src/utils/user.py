import logging
import os
import keyring
from getpass import getpass
from pathlib import Path
from string import Template
from decouple import config
from .cert_generator import run as generate_cert
from .constants import Constants

def init_user(user: str):
    try:
        __config_current_user_path(user)
        __config_user(user)
        __config_certificate(user)
    except Exception as err:
        raise Exception(f'Could not init the config for the user {user}. Error: {err}')

def get_user_password(user: str):
    return keyring.get_password(__get_user_key(user), 'id')

def __get_user_key(user: str):
    return Template(config(Constants.Keyring.user_mask)).substitute(user=user)

def __get_token_key(user: str):
    return Template(config(Constants.Keyring.user_token_mask)).substitute(user=user)

def get_user_token_value(user: str):
    token_key = __get_token_key(user)
    return keyring.get_password(token_key, 'token')

def set_user_token_value(user: str, token: str):
    token_key = __get_token_key(user)
    keyring.set_password(token_key, 'token', token)

def __config_user(user: str):

    # Config user
    user_key  = __get_user_key(user)
    credential_exists = keyring.get_credential(user_key, 'id') != None
    is_standalone_run = config(Constants.Wrapper.standalone_run, cast=bool)

    if  is_standalone_run and not credential_exists:
        raise Exception(f'Please run the script without the standalone flag and config the user : {user}')

    option = 'N'
    if credential_exists: 
        option = input(f'The user {user} in key {user_key} already exist, do you want to replace? [Y/N]: ')

    if option == 'Y' or not credential_exists:
        user_id = user
        user_password = getpass(f'[>] Enter your password for {user_id} (Used on the app/website): ')

        keyring.set_password(user_key, 'id', user_password)

def __config_current_user_path(user: str):
    cache_dir_path: Path = config(Constants.Wrapper.cache_dir_path, cast=Path)
    user_cache_dir_path = cache_dir_path.joinpath(user)

    if not user_cache_dir_path.exists():
        logging.debug('Creating User Data directory')

        user_cache_dir_path.mkdir(parents=True, exist_ok=True)
        logging.debug('User data directory created')

    os.environ[Constants.Wrapper.user_cache_dir_path] = str(user_cache_dir_path)


def __config_certificate(user: str):
    user_data_cache: Path = config(Constants.Wrapper.user_cache_dir_path, cast=Path)
    certificate_file_name = Template(config(Constants.Wrapper.user_certificate_mask)).substitute(user=user)
    certificate_file_path = user_data_cache.joinpath(certificate_file_name).absolute()
    certificate_exists = certificate_file_path.exists()
    os.environ[Constants.Wrapper.user_certificate_path] = str(certificate_file_path)

    logging.debug(f'Cerfificate file name: {certificate_file_name}')
    logging.debug(f'Cerfificate file path: {certificate_file_path}')
    logging.debug(f'Cerfificate file exists: {certificate_exists}')

    
    if not certificate_exists:
        logging.debug(f'Generating Certificate {get_user_password(user)}')
        generate_cert(user, get_user_password(user))
    
    logging.debug(f'Certificate config finished')
