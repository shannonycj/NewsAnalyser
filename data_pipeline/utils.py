import os
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


def save_article(article_id, article):
    corpora_path = __config['corpora_path']
    try:
        file_path = os.path.join(corpora_path, f'{article_id}.txt')
        with open(file_path, 'w') as f:
            f.write(article)
    except Exception as e:
        log(str(e))


def load_articles(article_ids):
    corpora_path = __config['corpora_path']
    files = os.listdir(corpora_path)
    for i in article_ids:
        file_name = i + '.txt'
        if file_name in files:
            try:
                with open(os.path.join(corpora_path, file_name), 'r') as fs:
                    article = fs.read()
                yield i, article
            except Exception as e:
                msg = f'Loading file "{file_name}" failed.\n' + str(e)
                log(msg)
        yield i, None
