# PyNubank Export Script

The idea of this project is to provide an easy way to extract and store your Nubank Credit Card data and Nubank Account data. This script is based on the pynubank lib.

This is a sample config that need to be created on the root folder.
```json
{
    "users": [
        {
            "cpf": "11144477789",
            "token": "Your generated token"
        }
    ],
    "cachedir": "Path to the dir where your temp data will be stored",
    "mysqlConfig": {
        "host": "mysql.host",
        "port": "3306",
        "database": "database-name",
        "user": "user",
        "password": "password"
    }
}
```

## Troubleshoting

This script is better to be run in a pyenv and virtualenv environment.

If you are using linux, don't forget to install lzma, liblzma-dev and libffi-dev.
If you already created installed a python version with pyenv and created a virtualenv, you will need to uninstall it and remove virtual environment to make it work.


python -m venv env # to create a virtual env called env in the current folder
source env/bin/activate
python -m pip install -r requirements.txt
python main.py