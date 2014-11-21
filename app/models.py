from flask import current_app
from flask.ext.security import UserMixin, RoleMixin
from sqlalchemy.ext.hybrid import hybrid_property
from .core import db
from .helpers import JSONSerializer, acceptable_url_string

# association object
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
        )


class Role(db.Model, RoleMixin):
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(), unique=True)
    description     = db.Column(db.String())


users_photos = db.Table('users_photos',
        db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
        db.Column('photo_id', db.Integer, db.ForeignKey('photo.id'))
        )

class User(db.Model, UserMixin):
    id                  = db.Column(db.Integer, primary_key=True)
    provider_id         = db.Column(db.Integer, db.ForeignKey('provider.id'))
    consumer_id         = db.Column(db.Integer, db.ForeignKey('consumer.id'))
    first_name          = db.Column(db.String)
    last_name           = db.Column(db.String)
    gender              = db.Column(db.String)
    birth_day           = db.Column(db.String)
    email               = db.Column(db.String(), unique=True)
    password            = db.Column(db.String())
    active              = db.Column(db.Boolean())
    confirmed_at        = db.Column(db.DateTime())
    current_login_at    = db.Column(db.DateTime())
    last_login_at       = db.Column(db.DateTime())
    current_login_ip    = db.Column(db.String())
    last_login_ip       = db.Column(db.String())
    login_count         = db.Column(db.Integer())
    roles               = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('user', lazy='dynamic'))
    favorite_photos     = db.relationship('Photo', secondary=users_photos,
                            backref=db.backref('users', lazy='dynamic'))


class Photo(db.Model):
    id                  = db.Column(db.Integer, primary_key=True)
    url                 = db.Column(db.Text)
    sm_thumb            = db.Column(db.Text)
    lg_thumb            = db.Column(db.Text)
    provider_id         = db.Column(db.Integer, db.ForeignKey('provider.id'))
    gallery_id          = db.Column(db.Integer, db.ForeignKey('gallery.id'))
    consumer_id         = db.Column(db.Integer, db.ForeignKey('consumer.id'))

    def __init__(self, **kwargs):
        self.url = kwargs.get('url', '')
        self.sm_thumb = kwargs.get('sm_thumb', '')
        self.lg_thumb = kwargs.get('lg_thumb', '')


class Banner(db.Model):
    id                  = db.Column(db.Integer, primary_key=True)
    url                 = db.Column(db.Text)
    sm_thumb            = db.Column(db.Text)
    lg_thumb            = db.Column(db.Text)
    provider_id         = db.Column(db.Integer, db.ForeignKey('provider.id'))

class Gallery(db.Model):
    id                  = db.Column(db.Integer, primary_key=True)
    provider_id         = db.Column(db.Integer, db.ForeignKey('provider.id'))
    consumer_id         = db.Column(db.Integer, db.ForeignKey('consumer.id'))
    photos              = db.relationship('Photo', backref='gallery', lazy="dynamic")


class ProductSerializer(JSONSerializer):
    __json_hidden__ = ['consumer', 'provider']


class Product(db.Model, JSONSerializer):
    id                  = db.Column(db.Integer, primary_key=True)
    name                = db.Column(db.String)
    description         = db.Column(db.String)
    provider_id         = db.Column(db.Integer, db.ForeignKey('provider.id'))
    consumer_id         = db.Column(db.Integer, db.ForeignKey('consumer.id'))
    hair_routine_id     = db.Column(db.Integer, db.ForeignKey('hairroutine.id'))
