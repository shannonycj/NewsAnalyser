import os
import logging
import hashlib
from datetime import datetime
import nltk
import gensim
import joblib
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
        file_name = str(i) + '.txt'
        if file_name in files:
            try:
                with open(os.path.join(corpora_path, file_name), 'r') as fs:
                    article = fs.read()
                yield i, article
            except Exception as e:
                msg = f'Loading file "{file_name}" failed.\n' + str(e)
                log(msg)
                yield i, None
        else:
            yield i, None


def get_stopwords():
    stopwords = nltk.corpus.stopwords.words('english')
    return stopwords


def lemmatize(words):
    lemmatizer = nltk.stem.WordNetLemmatizer()
    return [*map(lemmatizer.lemmatize, words)]


def basic_tokenize(text):
    text = text.lower()
    words = nltk.tokenize.regexp_tokenize(text, r'\w+')
    stopwords = get_stopwords()
    words = filter(lambda w: w not in stopwords, words)
    # remove numbers
    words = filter(lambda w: len(w) > 1 and not w.isnumeric(), words)
    return lemmatize(words)


def add_multigrams(docs, min_count=5):
    """
    min_count: only include phrases with occurance more than that
    """
    phrases = gensim.models.Phrases(docs, min_count=min_count)
    for i in range(len(docs)):
        multigrams = [*filter(lambda s: '_' in s, phrases[docs[i]])]
        docs[i].extend(multigrams)
    return docs


def build_gensim_dictionary(docs, no_below, no_above):
    dictionary = gensim.corpora.dictionary.Dictionary(docs)
    dictionary.filter_extremes(no_below=no_below, no_above=no_above)
    return dictionary


def build_gensim_corpus(docs, dictionary):
    return [dictionary.doc2bow(doc) for doc in docs]


def gensim_pipeline(article_ids, min_count=5, no_below=1, no_above=1.):
    articles = load_articles(article_ids)
    docs, loaded_idx = [], []
    for i, article in articles:
        if not article:
            continue
        loaded_idx.append(i)
        docs.append(basic_tokenize(article))
    docs = add_multigrams(docs, min_count)
    dictionary = build_gensim_dictionary(docs, no_below, no_above)
    corpus = build_gensim_corpus(docs, dictionary)
    print('Number of unique tokens: %d' % len(dictionary))
    print('Number of documents: %d' % len(corpus))
    return dictionary, corpus, loaded_idx


def build_tfidf_model(corpus):
    model = gensim.models.tfidfmodel.TfidfModel(corpus)
    return model


def create_hash_path(path):
    s = str(datetime.now().timestamp()).encode('utf-8')
    folder = hashlib.sha256(s).hexdigest()[:10]
    save_path = os.path.join(path, folder)
    os.mkdir(save_path)
    return save_path


def train_lda(dictionary, corpus, num_topics=10, chunksize=2000,
              iterations=400, passes=20):
    # Make a index to word dictionary.
    _ = dictionary[0]  # This is only to "load" the dictionary.
    id2word = dictionary.id2token
    print('Training LDA model...')
    model = gensim.models.LdaModel(
        corpus=corpus,
        id2word=id2word,
        chunksize=chunksize,
        alpha='auto',
        eta='auto',
        iterations=iterations,
        num_topics=num_topics,
        passes=passes,
        eval_every=None
    )
    path = os.path.join(create_hash_path(__config['lda_model_path']),
                        'model.pkl')
    joblib.dump(model, path)
    print('LDA model has been saved.')
    return model
