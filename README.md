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
        "host": "mysq.host",
        "port": "3306",
        "database": "database-name",
        "user": "user",
        "password": "password"
    }
}
```
