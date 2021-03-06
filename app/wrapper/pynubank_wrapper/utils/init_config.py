import keyring
import logging
import os
from decouple import config, AutoConfig
from keyrings.cryptfile.cryptfile import CryptFileKeyring
from pathlib import Path
from .constants import Constants
from .user import init_user

def init_config(user: str):
    try:
        config_logging()
        config_keyring()
        config_cache_dir()
        init_user(user)
    except Exception as ex:
        raise Exception(f'init_config failed for user: {user}. Error: {ex}')

def config_keyring():
    # Keyring config
    kr = CryptFileKeyring()
    kr.keyring_key = config(Constants.Keyring.secret)
    keyring.set_keyring(kr)

def config_logging():
    # Config Logging
    try:
        config_logging_level = config(Constants.Log.level)

        if config_logging_level in logging._nameToLevel.keys():
            log_level = getattr(logging, config_logging_level)
        else:
            log_level = logging.DEBUG

        logging.basicConfig(encoding='utf-8', level=log_level)
    except Exception as ex:
        raise Exception(f'Could not configure logging. Error: {str(ex)}')
    
    logging.debug('Logging configured successfully')

def config_cache_dir():
    use_localappdata = config(Constants.Wrapper.use_localappdata, cast=bool)

    if use_localappdata:
        wrapper_root_dir = Path(os.getenv('LOCALAPPDATA')).joinpath('pynubank_wrapper')
    else:
        wrapper_root_dir = Path(__file__).resolve().parent.parent.parent.absolute()
    
    cache_dir_path = wrapper_root_dir.joinpath(config(Constants.Wrapper.cache_dir_name))
    os.environ[Constants.Wrapper.cache_dir_path] = str(cache_dir_path)

    if not cache_dir_path.exists():
        logging.debug('Creating Cache directory')

        cache_dir_path.mkdir(parents=True, exist_ok=True)
        logging.debug('Cache directory created successfully')

    logging.debug(f'Cache has been configured')
