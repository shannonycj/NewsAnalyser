import pandas as pd
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


def get_tfidf(topk=5):
    """
    Use existing data in corpora/ to generate top tfidf words for each doc

    :return: [description]
    :rtype: [type]
    """
    # improve preprocessing refering to notebook
    df_articles = query_all_articles()
    idx = df_articles.id.tolist()
    dictionary, corpus, loaded_idx = utils.gensim_pipline(idx)
    model = utils.build_tfidf_model(corpus)
    report = {}
    for article_id, doc in zip(loaded_idx, corpus):
        weights = model[doc]
        sorted_weights = sorted(weights, key=lambda w: w[1], reverse=True)
        r = map(lambda w: (dictionary.get(w[0]), w[1]), sorted_weights[:topk])
        report[article_id] = [*r]
    return report
