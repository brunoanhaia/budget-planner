# PyNubank Export Script

The idea of this project is to provide an easy way to extract and store your Nubank Credit Card data and Nubank Account data. This script is based on the pynubank lib.


## Troubleshoting

This script is better to be run in a pyenv and virtualenv environment.

If you are using linux, don't forget to install lzma, liblzma-dev and libffi-dev.
If you already created installed a python version with pyenv and created a virtualenv, you will need to uninstall it and remove virtual environment to make it work.

```bat
python -m venv env # to create a virtual env called env in the current folder
source env/bin/activate
python -m pip install -r requirements.txt
python main.py
```

## Generating Wrapper exe
Go to the wrapper root folder and execute:
```bat
pyinstaller entrypoint.py --collect-all wrapper --collect-all pynubank
```
<b>Remarks</b>: Don't forget to add the cache folder to it. If you want to build the one file exe, please use `--onefile`.

