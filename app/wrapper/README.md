# .env config and example

## Keyring config

- <b>KEYRING-SECRET</b>: A string containing the passcode to your keyring.
- <b>KEYRING-MASK</b>: A string that will be used as a template to store the user password.
- <b>KEYRING-TKMASK</b>: A string that will be used as a template to store the user token.

## Logging config

- <b>LOG_LEVEL</b>: The log level for the nubank wrapper.

## Wrapper config
- <b>CACHE_DIR_NAME</b>: A string that stores the name of the dir that will be used for caching user info.
- <b>CERTIFICATE_MASK</b>: A string that will be used as a template to store the name of the user certificate. The certificate is saved inside the cache folder
- <b>STANDALONE_RUN</b>: A boolean signalizing if the script should run in standalone mode or not.

</br>

## Example config


```markdown
# KEYRING CONFIG
KEYRING-SECRET='SOMEKEY'
KEYRING-MASK='${user}-user@your_appn_ame'
KEYRING-TKMASK='${user}-token@your_appn_ame'

# LOGGING
LOG_LEVEL=DEBUG

# WRAPPER CONFIG
CACHE_DIR_NAME='cache'
CERTIFICATE_MASK="${user}_cert.p12"
STANDALONE_RUN=False
```
