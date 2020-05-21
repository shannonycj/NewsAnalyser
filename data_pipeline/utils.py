import logging
from config import __config


logging.basicConfig(
    filename=__config['logging_path'],
    level=logging.WARNING,
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p')


def log(msg):
    print(msg)
    logging.warning(msg)
