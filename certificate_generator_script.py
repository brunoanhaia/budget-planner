import os
import random
import string
from getpass import getpass

from pynubank import NuException
from pynubank.utils.certificate_generator import CertificateGenerator

def generate_random_id() -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))


def log(message):
    print(f'[*] {message}')


def save_cert(cert, name, passphrase = None):
    path = os.path.join(os.getcwd(), name)
    with open(path, 'wb') as cert_file:
        cert_file.write(cert.export())


def run(cpf: string, password: string, save_file):
    log(f'Starting PyNubank context creation.')

    device_id = generate_random_id()

    log(f'Generated random id: {device_id}')

    generator = CertificateGenerator(cpf, password, device_id)

    log('Requesting e-mail code')
    try:
        email = generator.request_code()
    except NuException:
        log(f'Failed to request code. Check your credentials!')
        return

    log(f'Email sent to {email}')
    code = input('[>] Type the code received by email: ')

    cert1, cert2 = generator.exchange_certs(code)

    if save_file:
        save_cert(cert1, f'{cpf}_cert.p12')

    print(f'Certificates generated successfully.')
    print(f'Warning, keep these certificates safe (Do not share or version in git)')
    return cert1