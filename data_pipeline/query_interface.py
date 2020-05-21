import sqlalchemy as sqla
import nltk
import gensim
import data_pipeline.db_orm as db_orm
import data_pipeline.utils as utils


engine = db_orm.init_database()
Session = sqla.orm.sessionmaker(bind=engine)


def insert_new_meta(item):
    sess = Session()
    item_id = None
    try:
        article_meta = db_orm.ArticlesMeta(**item)
        sess.add(article_meta)
        sess.commit()
        item_id = article_meta.id
    except Exception as e:
        utils.log(str(e))
    sess.close()
    return item_id


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
    return lemmatize(words)


def build_gensim_corpus(docs):
    """
    accept file-loading generator, which yields (article_id, article) in each
    iteration

    :param docs: iterable of tuples (id, text) of documents
    :type docs: generator
    :return: built gensim Dict, gensim corpus and ids of docs loaded
    :rtype: tuple(gensim.corpora.dictionary.Dictionary, list, list)
    """
    articles, loaded_idx = [], []
    for i, doc in docs:
        if not doc:
            continue
        loaded_idx.append(i)
        articles.append(basic_tokenize(doc))
    dictionary = gensim.corpora.dictionary.Dictionary(articles)
    corpus = [dictionary.doc2bow(article) for article in articles]
    return dictionary, corpus, loaded_idx


def build_tfidf_model(corpus):
    model = gensim.models.tfidfmodel.TfidfModel(corpus)
    return model


def get_tfidf():
    """
    Use existing data in corpora/ to generate top tfidf words for each doc

    :return: [description]
    :rtype: [type]
    """
    # TODO improve preprocessing refering to notebook
    sess = Session()
    idx = sess.query(db_orm.ArticlesMeta.id).all()
    idx = [*map(lambda e: e[0], idx)]
    sess.close()

    return idx
