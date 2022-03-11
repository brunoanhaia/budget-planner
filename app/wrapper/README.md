# .env config and example

## Keyring config

- **KEYRING-SECRET**: A string containing the passcode to your keyring.
- **KEYRING-MASK**: A string that will be used as a template to store the user password.
- **KEYRING-TKMASK**: A string that will be used as a template to store the user token.

## Logging config

- **LOG_LEVEL**: The log level for the nubank wrapper.

## Wrapper config
- **CACHE_DIR_NAME**: A string that stores the name of the dir that will be used for caching user info.
- **CERTIFICATE_MASK**: A string that will be used as a template to store the name of the user certificate. The certificate is saved inside the cache folder
- **STANDALONE_RUN**: A boolean signalizing if the script should run in standalone mode or not.
- **USE_LOCALAPPDATA**: A boolean signalizing if the cache folder should be created in the Local App Data folder.

</br>

## Example config


```bash
# KEYRING CONFIG
KEYRING-SECRET='SOMEKEY'
KEYRING-MASK='${user}-user@your_appn_ame'
KEYRING-TKMASK='${user}-token@your_appn_ame'

# LOGGING
LOG_LEVEL=DEBUG

# WRAPPER CONFIG
USE_LOCALAPPDATA=True
CACHE_DIR_NAME='cache'
CERTIFICATE_MASK="${user}_cert.p12"
STANDALONE_RUN=False
```
