import sqlalchemy as sqla
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
