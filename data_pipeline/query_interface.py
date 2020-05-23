import pandas as pd
from datetime import datetime
import sqlalchemy as sqla
import data_pipeline.db_orm as db_orm
import data_pipeline.utils as utils


engine = db_orm.init_database()
Session = sqla.orm.sessionmaker(bind=engine)


def query_all_articles():
    sess = Session()
    query = sess.query(db_orm.ArticlesMeta)
    df_articles = pd.read_sql(query.statement, sess.bind)
    sess.close()
    return df_articles


def insert_new_meta(item):
    sess = Session()
    item_id = None
    if item['url'] in query_all_articles().url.tolist():
        return item_id
    try:
        article_meta = db_orm.ArticlesMeta(**item)
        sess.add(article_meta)
        sess.commit()
        item_id = article_meta.id
    except Exception as e:
        utils.log(str(e))
    sess.close()
    return item_id


def clean_up_table(table):
    sess = Session()
    sess.query(table).delete()
    sess.close()


def insert_tfidf_metric(article_id, metrics, load_dt):
    sess = Session()
    objs = [db_orm.TfidfMetric(meta_id=article_id, word=m[0], tfidf=m[1],
                               load_dt=load_dt) for m in metrics]
    sess.add_all(objs)
    sess.commit()
    sess.close()


def get_tfidf(topk=5):
    """
    Use existing data in corpora/ to generate top tfidf words for each doc

    :return: [description]
    :rtype: [type]
    """
    df_articles = query_all_articles()
    idx = df_articles.id.tolist()
    idx_str = ', '.join(map(str, idx))
    print(f'updating tfidf metrics for articles: {idx_str}')
    dictionary, corpus, loaded_idx = utils.gensim_pipeline(idx)
    model = utils.build_tfidf_model(corpus)
    clean_up_table(db_orm.TfidfMetric)
    load_dt = datetime.now()
    for article_id, doc in zip(loaded_idx, corpus):
        weights = model[doc]
        sorted_weights = sorted(weights, key=lambda w: w[1], reverse=True)
        r = map(lambda w: (dictionary.get(w[0]), w[1]), sorted_weights[:topk])
        insert_tfidf_metric(article_id, r, load_dt)
    print('update tfidf finished.')


def insert_lda_topics(topic_id, topic_repr, topic_coherence, load_dt):
    sess = Session()
    objs = []
    for prob, word in topic_repr:
        lda_topic = db_orm.LDATopic(
            topic_id=topic_id, word=word, word_prob=prob,
            topic_coherence=topic_coherence, load_dt=load_dt)
        objs.append(lda_topic)
    sess.add_all(objs)
    sess.commit()
    sess.close()


def get_lda(num_topics=10, chunksize=2000, iterations=400, passes=20):
    df_articles = query_all_articles()
    idx = df_articles.id.tolist()
    idx_str = ', '.join(map(str, idx))
    print(f'updating LDA topics metrics for articles: {idx_str}')
    dictionary, corpus, loaded_idx = utils.gensim_pipeline(idx)
    model = utils.train_lda(dictionary, corpus, num_topics, chunksize,
                            iterations, passes)
    clean_up_table(db_orm.LDATopic)
    top_topics = model.top_topics(corpus)
    load_dt = datetime.now()
    for i, topic in enumerate(top_topics):
        topic_coherence = topic[1]
        topic_repr = topic[0]
        insert_lda_topics(i, topic_repr, topic_coherence, load_dt)
    print('update lda topics finished.')
