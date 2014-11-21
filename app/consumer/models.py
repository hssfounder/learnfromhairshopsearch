from flask import current_app
from sqlalchemy.ext.hybrid import hybrid_property
from ..core import db
from ..helpers import JSONSerializer, acceptable_url_string

consumers_providers = db.Table('consumers_providers',
        db.Column('consumer_id', db.Integer, db.ForeignKey('consumer.id')),
        db.Column('provider_id', db.Integer, db.ForeignKey('provider.id'))
        )

class ConsumerSerializer(JSONSerializer):
    __json_hideen__ = [
           'user',
           'favorites',
           '_consumer_url',
           'avatar',
           'bio',
           'hair_status',
           'hair_journey',
           'hair_routine',
           'gallery',
           'consumer_url'
            ]

class Consumer(db.Model, ConsumerSerializer):
    _db = db

    def __init__(self, **kwargs):
        self.user               = kwargs.get('user', '')
        self.hair_routine       = HairRoutine()
        self.hair_journey       = kwargs.get('hair_journey', '')
        self.hair_status        = kwargs.get('hair_status', '')

    def __repr__(self):
        return ('{} {} {} {}'.format(
            self.id,
            self.user.email,
            self._consumer_url,
            self.hair_status
            ))

    def save(self):
        self._db.session.add(self)
        self._db.session.commit()

    # ready to be serialized, for great search
    id                  = db.Column(db.Integer, primary_key=True)
    provider_id         = db.Column(db.Integer, db.ForeignKey('provider.id'))
    user                = db.relationship('User', backref='consumer',
                            uselist=False)
    _consumer_url       = db.Column(db.String)
    favorites           = db.relationship('Provider',
                            backref=db.backref('favorited_by', lazy='dynamic'),
                            secondary=consumers_providers)
    avatar              = db.relationship('Photo', uselist=False)
    hair_status         = db.Column(db.Text)
    hair_journey        = db.Column(db.Text)
    comments            = db.relationship('Comment', backref='consumer')
    hair_routine        = db.relationship('HairRoutine', backref= 'consumer',
                            uselist=False)

    @hybrid_property
    def consumer_url(self):
        return self._consumer_url

    @consumer_url.setter
    def consumer_url(self, value):
        self._consumer_url = value


class ConsumerInstance(db.Model):
    __tablename__      = 'consumer_instance'

    name                = db.Column(db.String, primary_key=True)
    count               = db.Column(db.Integer)


class HairRoutineSerializer(JSONSerializer):
    __json_hidden__ = [
            'hair_condition',
            'chemical_treat',
            'last_treatment',
            'fav_style',
            'shampoo_type',
            'shampoo_frequency',
            'conditioner_type',
            'scalp_condition',
            'last_trim',
            'fav_products'
            ]


class HairRoutine(db.Model, HairRoutineSerializer):
    # Ready to be serialized for search purposes
    __tablename__       = 'hairroutine'

    def __init__(self, **kwargs):
        self.hair_condition      = kwargs.get('hair_condition', '')
        self.chemical_treat      = kwargs.get('chemical_treat', False)
        self.last_treatment      = kwargs.get('last_treatment', '')
        self.fav_style           = kwargs.get('fav_style', '')
        self.shampoo_type        = kwargs.get('shampoo_type', '')
        self.shampoo_frequency   = kwargs.get('shampoo_frequency', '')
        self.conditioner_type    = kwargs.get('conditioner_type', '')
        self.condition_frequency = kwargs.get('condition_frequency', '')
        self.scalp_condition     = kwargs.get('scalp_condition', '')
        self.last_trim           = kwargs.get('last_trim', '')


    id                  = db.Column(db.Integer, primary_key=True)
    consumer_id         = db.Column(db.Integer, db.ForeignKey('consumer.id'))
    hair_condition      = db.Column(db.Text()) # text
    chemical_treat      = db.Column(db.Boolean()) # bool
    last_treatment      = db.Column(db.Text()) # text
    fav_style           = db.Column(db.Text()) # text
    shampoo_type        = db.Column(db.Text()) # text
    shampoo_frequency   = db.Column(db.String()) # string
    conditioner_type    = db.Column(db.String()) # string
    condition_frequency = db.Column(db.String()) # string
    scalp_condition     = db.Column(db.String())
    last_trim           = db.Column(db.String())
    favorite_products   = db.relationship('Product')
