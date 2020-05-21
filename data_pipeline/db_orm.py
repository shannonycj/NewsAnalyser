import os
import sqlalchemy as sqla
from sqlalchemy.ext.declarative import declarative_base
from config import __config


Base = declarative_base()


class ArticlesMeta(Base):
    __tablename__ = 'articles_meta'
    id = sqla.Column(sqla.Integer, autoincrement=1, primary_key=True)
    title = sqla.Column(sqla.String(255), nullable=False)
    publish_date = sqla.Column(sqla.DATE)
    url = sqla.Column(sqla.String(255), nullable=False)
    source = sqla.Column(sqla.String(255), nullable=False)
    original_key = sqla.Column(sqla.String(255), nullable=False)


class ModelOutput(Base):
    __tablename__ = 'model_output'
    id = sqla.Column(sqla.Integer, autoincrement=1, primary_key=True)
    meta_id = sqla.Column(sqla.Integer, sqla.ForeignKey('articles_meta.id'))
    tfidf = sqla.Column(sqla.String(255))
    lda_class = sqla.Column(sqla.Integer)
    lda_repr = sqla.Column(sqla.String(255))


def init_database():
    db_path = __config['database_path']
    is_existing = os.path.exists(db_path)
    engine = sqla.create_engine(f'sqlite:///{db_path}', echo=False)
    if not is_existing:
        Base.metadata.create_all(engine)
    return engine