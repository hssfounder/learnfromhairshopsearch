import config

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask.ext.security import SQLAlchemyUserDatastore
from .models import User, Role
ud = SQLAlchemyUserDatastore(db, User, Role)

from flask.ext.mail import Mail
mail = Mail()

from pyelasticsearch import ElasticSearch
es = ElasticSearch(config.ELASTICSEARCH_SERVER)

from flask_security import Security
sec = Security()
sec.datastore = ud

class HSSError(Exception):
    def __init__(self, msg):
        self.msg = msg
