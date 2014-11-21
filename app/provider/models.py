from flask import current_app
from ..models import Gallery
from ..helpers import JSONSerializer, acceptable_url_string
from ..core import db
from ..indexer.indexer import index_one, update_doc

import requests
import datetime
import time

class ProviderSerializer(JSONSerializer):
    __json_hidden__ = [
            'gallery', 'avatar', 'products', 'banner',
            'hours', 'user', 'favorited_by',
            'reviews', 'fb_url', 'links', 'twitter_url', 'phone',
            '_business_url', 'email', 'bio', 'address', 'payment_methods',
            'business_name', 'endorses', 'endorsed_by']


endorsers_endorsees = db.Table('endorsers_endorsees',
            db.Column('endorser', db.Integer, db.ForeignKey('provider.id'), primary_key=True),
            db.Column('endorsee', db.Integer, db.ForeignKey('provider.id'), primary_key=True)
        )

providers_happy_customers = db.Table('providers_happy_customers',
        db.Column('provider', db.Integer, db.ForeignKey('provider.id'), primary_key=True),
        db.Column('happy_customer', db.Integer, db.ForeignKey('consumer.id'), primary_key=True)
        )

providers_unhappy_customers = db.Table('providers_unhappy_customers',
        db.Column('provider', db.Integer, db.ForeignKey('provider.id'), primary_key=True),
        db.Column('unhappy_customer', db.Integer, db.ForeignKey('consumer.id'), primary_key=True)
        )


class Provider(db.Model, ProviderSerializer):
    _db = db

    def __init__(self, user):
        self.user = user
        self.address = Address()
        self.location = Location(0, 0)
        self.hours = Hours()
        self.payment_methods = ''
        self.gallery = Gallery()

        for _type in ['barbershop', 'salon', 'product']:
            menu = Menu(menu_type=_type)
            self.menus.append(menu)

    def save(self):
        """
        Save an instance in the db
        """
        self._db.session.add(self)
        self._db.session.commit()

    @classmethod
    def get(cls, id):
        """
        Classmethod
        Get a model by it's id
        :param id:
        :type id: integer
        :rtype: Provider obj
        """
        return cls.query.get(id)

    @classmethod
    def find(cls, **kwargs):
        """
        Wrapper around query.filter_by(**kwargs).all()
        """
        return cls.query.filter_by(**kwargs).all()

    def index(self):
        """
        Save model as document in es index
        :rtype: the response returned by the es server
        """
        return index_one(self, self.id)

    def _get_clean_name(self, dirty_name):
        return acceptable_url_string(dirty_name.lower(),
                current_app.config['ACCEPTABLE_URL_CHARS'])

    #TODO update index method
    def update_index(self):
        return update_doc(self)

    id                  = db.Column(db.Integer, primary_key=True)
    user                = db.relationship('User', backref='provider',
                            uselist=False)

    avatar              = db.relationship('Photo', uselist=False)
    banner              = db.relationship('Banner', uselist=False)

    _business_name      = db.Column(db.String)
    _business_url       = db.Column(db.String)

    @property
    def business_name(self):
        return self._business_name

    @business_name.setter
    def business_name(self, value):
        # this assumes business name has  been set
        self._business_name = value
        clean_name = self._get_clean_name(value)
        provider_instance = ProviderInstance.query.get(clean_name)

        if provider_instance:
            self.business_url = '{}.{}'.format(clean_name, pi.count)
            pi.count += 1

        else:
            pi = ProviderInstance()
            pi.name = clean_name
            pi.count = 1
            self.business_url = clean_name

    @property
    def business_url(self):
        return self._business_url

    @business_url.setter
    def business_url(self, value):
        self._business_url = value

    phone               = db.Column(db.String)
    email               = db.Column(db.String)
    hours               = db.relationship('Hours', uselist=False)
    address             = db.relationship('Address', uselist=False,
                            backref=db.backref('provider'))
    payment_methods     = db.Column(db.String, default='')

    bio                 = db.Column(db.Text)
    external_site       = db.Column(db.Text)

    menus               = db.relationship('Menu',
                            backref=db.backref('provider'))
    gallery             = db.relationship('Gallery', uselist=False)
    products            = db.relationship('Product', backref='provider')
    location            = db.relationship('Location', uselist=False)
    comments            = db.relationship('Comment', backref='provider')

    # TODO different backref name
    shared              = db.relationship('Consumer', backref='shared')

    happy_customers     = db.relationship('Consumer',
                            secondary=providers_happy_customers,
                            backref='happy')

    unhappy_customers   = db.relationship('Consumer',
                            secondary=providers_unhappy_customers,
                            backref='unhappy')

    endorses            = db.relationship('Provider',
                            secondary=endorsers_endorsees,
                            primaryjoin=id==endorsers_endorsees.c.endorser,
                            secondaryjoin=id==endorsers_endorsees.c.endorsee,
                            backref="endorsed_by")


class ProviderInstance(db.Model):
    __tablename__      = 'provider_instance'

    name                = db.Column(db.String, primary_key=True)
    count               = db.Column(db.Integer)


class AddressSerializer(JSONSerializer):
    __json_hidden__ = ['provider', 'id']


class Address(db.Model, AddressSerializer):
    """ Class rep'ing a street address

    :param street_1: Street address
    :param street_2: Street address 2
    :param apartment: Apt number
    :param city: City
    :param state: State (as abbrev "TN")
    :param zip_code: Five digit zip

    """

    id                  = db.Column(db.Integer, primary_key=True)
    provider_id         = db.Column(db.Integer, db.ForeignKey('provider.id'))
    street_1            = db.Column(db.String)
    street_2            = db.Column(db.String)
    apartment           = db.Column(db.String)
    city                = db.Column(db.String)
    state               = db.Column(db.String)
    zip_code            = db.Column(db.Integer)

    def __init__(self, **kwargs):
        self.street_1       = kwargs.get('street_1', '')
        self.street_2       = kwargs.get('street_2', '')
        self.apartment      = kwargs.get('apartment', '')
        self.city           = kwargs.get('city', '')
        self.state          = kwargs.get('state', '')
        self.zip_code       = kwargs.get('zip_code', 0)

    def geocode(self):
        """Access the Mapquest Geocoding API to return lat and lon given
        an address.

        :rtype: array of tuples of the format (lat, lon)
        """

        params = {}
        params['key']           = current_app.config['GEOCODING_SERVICE_KEY']
        params['outFormat']     = 'json'
        params['inFormat']      = 'kvp'
        params['street']        = '{}{}{}'.format(
                                    self.street_1 or '',
                                    self.street_2 or '',
                                    self.apartment or ''
                                    )
        params['city']          = self.city
        params['state']         = self.state
        params['postalCode']    = self.zip_code
        params['thumbMaps']     = 'false'

        geo_uri = current_app.config['GEOCODING_SERVICE_URI']

        resp = requests.get(geo_uri, params=params)

        decoded_resp = resp.json()

        if not decoded_resp['info']['statuscode'] == 0:
            for msg in  decoded_resp['info']['messages']:
                print msg
                raise Exception(msg)

        res_arr = []

        for res in decoded_resp['results']:
            for loc in res['locations']:
                res_arr.append((loc['latLng']['lat'], loc['latLng']['lng']))

        return res_arr


    def __repr__(self):
        return '%s %s %s, %s, %s %s' %(
               self.street_1,
               self.street_2,
               self.apartment,
               self.city,
               self.state,
               self.zip_code
                )


class MenuSerializer(JSONSerializer):
    __json_hidden__ = ['provider', 'provider_id', 'id']


class Menu(db.Model, MenuSerializer):
    id                  = db.Column(db.Integer, primary_key=True)
    provider_id         = db.Column(db.Integer, db.ForeignKey('provider.id'))
    menu_type           = db.Column(db.String)
    menu_items          = db.relationship('MenuItem', backref='menu')


class MenuItemSerializer(JSONSerializer):
    __json_hidden__ = ['menu', 'menu_id', 'id']


class MenuItem(db.Model, MenuItemSerializer):
    id                  = db.Column(db.Integer, primary_key=True)
    menu_id             = db.Column(db.Integer, db.ForeignKey('menu.id'))
    name                = db.Column(db.String)
    price               = db.Column(db.Float(precision=2))
    description         = db.Column(db.Text())


class HoursSerializer(JSONSerializer):
    __json_hidden__ = ['provider']


class Hours(db.Model, HoursSerializer):
    id                      = db.Column(db.Integer, primary_key=True)
    provider_id             = db.Column(db.Integer,
                                db.ForeignKey('provider.id'))
    monday_open             = db.Column(db.String, default="Closed")
    monday_close            = db.Column(db.String, default="Closed")
    tuesday_open            = db.Column(db.String, default="Closed")
    tuesday_close           = db.Column(db.String, default="Closed")
    wednesday_open          = db.Column(db.String, default="Closed")
    wednesday_close         = db.Column(db.String, default="Closed")
    thursday_open           = db.Column(db.String, default="Closed")
    thursday_close          = db.Column(db.String, default="Closed")
    friday_open             = db.Column(db.String, default="Closed")
    friday_close            = db.Column(db.String, default="Closed")
    saturday_open           = db.Column(db.String, default="Closed")
    saturday_close          = db.Column(db.String, default="Closed")
    sunday_open             = db.Column(db.String, default="Closed")
    sunday_close            = db.Column(db.String, default="Closed")

    def __init__(self, **kwargs):
        self.monday_open             = kwargs.get("monday_open","Closed")
        self.monday_close            = kwargs.get("monday_close", "Closed")
        self.tuesday_open            = kwargs.get("tuesday_open", "Closed")
        self.tuesday_close           = kwargs.get("tuesday_close", "Closed")
        self.wednesday_open          = kwargs.get("wednesday_open", "Closed")
        self.wednesday_close         = kwargs.get("wednesday_close", "Closed")
        self.thursday_open           = kwargs.get("thursday_open", "Closed")
        self.thursday_close          = kwargs.get("thursday_close", "Closed")
        self.friday_open             = kwargs.get("friday_open", "Closed")
        self.friday_close            = kwargs.get("friday_close", "Closed")
        self.saturday_open           = kwargs.get("saturday_open", "Closed")
        self.saturday_close          = kwargs.get("saturday_close", "Closed")
        self.sunday_open             = kwargs.get("sunday_open", "Closed")
        self.sunday_close            = kwargs.get("sunday_close", "Closed")


    def todays_hours(self):
        self.daily_hours = dict()
        self.daily_hours[1] = (self.monday_open, self.monday_close)
        self.daily_hours[2] = (self.tuesday_open, self.tuesday_close)
        self.daily_hours[3] = (self.wednesday_open, self.wednesday_close)
        self.daily_hours[4] = (self.thursday_open, self.thursday_close)
        self.daily_hours[5] = (self.friday_open, self.friday_close)
        self.daily_hours[6] = (self.saturday_open, self.saturday_close)
        self.daily_hours[7] = (self.sunday_open, self.sunday_close)
        return self.daily_hours[datetime.date.today().isoweekday()]


class LocationSerializer(JSONSerializer):
    __json_hidden__ = ['provider_id', 'id']

class Location(db.Model, LocationSerializer):
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    id              = db.Column(db.Integer, primary_key=True)
    provider_id     = db.Column(db.Integer, db.ForeignKey('provider.id'))
    lat             = db.Column(db.Float)
    lon             = db.Column(db.Float)


class Comment(db.Model):
    def __init__(self, body):
        self.body = body
        self.timestamp = time.time()
        self.date = datetime.datetime.fromtimestamp(self.timestamp)


    id              = db.Column(db.Integer, primary_key=True)
    provider_id     = db.Column(db.Integer, db.ForeignKey('provider.id'))
    consumer_id     = db.Column(db.Integer, db.ForeignKey('consumer.id'))
    body            = db.Column(db.Text)
    date            = db.Column(db.Date)
    happy           = db.Column(db.Boolean)
