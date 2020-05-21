import sqlalchemy as sqla
import data_pipeline.db_orm as db_orm
import data_pipeline.utils as utils


engine = db_orm.init_database()
Session = sqla.orm.sessionmaker(bind=engine)


def insert_new_meta(item):
    sess = Session()
    try:
        sess.add(db_orm.ArticlesMeta(**item))
    except Exception as e:
        utils.log(str(e))
    sess.close()
