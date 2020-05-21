import sqlalchemy as sqla
from config import __config
import db_orm


engine = db_orm.init_database()
Session = sqla.orm.sessionmaker(bind=engine)





