#!/home/no/.venvs/hairshopsearch/bin/python
from flask.ext.script import Manager, Server, Shell
from flask_security.utils import encrypt_password
from app import create_app
from app.core import db, ud
from app.models import (User, Role, Photo, Gallery)
from app.provider.models import Provider, Address, Menu, MenuItem, Location
from app.consumer.models import Consumer
from app.models import Gallery, Photo
from app.helpers import JSONEncoder, acceptable_url_string
from app.indexer import indexer

import app.config

import os
import csv
import random
import datetime
from pprint import pprint

m = Manager(create_app)

@m.command
def dump_url_map():
    print create_app().url_map

@m.command
def populate_db():
    # Provider
    password = encrypt_password('password')
    p = Provider(user=ud.create_user(email="provider@test.com", password=password))
    p.business_name = 'Sparky\'s'
    p.user.confirmed_at = datetime.date.today()

    p.address.street_1 = '403 South Second'
    p.address.city = 'Clarksville'
    p.address.state = 'TN'
    p.address.zip_code = 37040

    p.menus[0].menu_items.append(MenuItem(name="Haircut", price="25", description="We cut your hair"))
    p.menus[0].menu_items.append(MenuItem(name="Line out", price="10", description="A quick line out"))
    p.menus[0].menu_items.append(MenuItem(name="Shave", price="14", description="Shave your face"))

    p.menus[1].menu_items.append(MenuItem(name="Color", price="40", description="A lovely color for your hair"))
    p.menus[1].menu_items.append(MenuItem(name="Blowout", price="150", description="Blast it to the moon"))
    p.menus[1].menu_items.append(MenuItem(name="Trim", price="25", description="Keep things neat and tidy"))
    p.menus[1].menu_items.append(MenuItem(name="Cut and Style", price="60", description="The full package"))

    p.gallery = Gallery()

    for num in range(1, 40):
        p.gallery.photos.append(Photo(
            url="http://placehold.it/600x900&text={}".format(num),
            sm_thumb="http://placehold.it/450x450&text={}".format(num),
            lg_thumb="http://placehold.it/550x550&text={}".format(num))
            )
    p.save()
    p.index()

    # Consumer
    c = Consumer(user=ud.create_user(email='consumer@test.com', password=password,
            first_name='Bob', last_name='Johnson'))
    c.user.confirmed_at = datetime.date.today()
    c.consumer_url = 'bob.johnson'
    c.favorites.append(Provider.get(10))
    c.favorites.append(Provider.get(15))
    c.favorites.append(Provider.get(94))
    db.session.add(c)
    db.session.commit()

@m.command
def reset_db():
    db.drop_all()
    db.create_all()


@m.command
def create_index(doc_type):
    """Create new index and mapped doc_type
    """
    indexer.create_index(doc_type)

@m.command
def reset_index(doc_type):
    """Delete and recreate the index with doc_type
    """
    indexer.reset_index(doc_type)

def _build_menus():
    """Return a list of two menus, on barber and on salon
    composed of a random set of menu items
    """
    menus = []
    menus.append(Menu(menu_type="barbershop"))
    menus.append(Menu(menu_type="salon"))
    services = [
            'hair cut',
            'perm',
            'hair trim',
            'texturizer',
            'relaxer',
            'color',
            'color correction',
            'extensions',
            'weave',
            'wax',
            'blowout'
            ]
    prices = ['4', '15', '25', '17.99', '50.89', '55', '22']
    for i in range(5, random.randint(6, 15)):
        menus[0].menu_items.append(MenuItem(
            name=random.choice(services),
            price=random.choice(prices)
            )
            )
        menus[0].menu_items.append(MenuItem(
            name=random.choice(services),
            price=random.choice(prices)
            )
            )
        return menus


def _consume_csv(filename):
    entities = []
    first = True
    with open(filename, 'r') as f:
        for row in csv.reader(f):
            if first:
                keys = row
                first = False
            else:
                entity = dict()
                for key, col in zip(keys, row):
                    entity[key] = col
                entities.append(entity)
        for entity in entities:
            # clean and convert lat lon to decimal if DMS
            lat_string = entity['lat'].strip()
            lon_string = entity['lon'].strip()
            if '\xc2\xb0' in lat_string:
                deg, min = lat_string.split('\xc2\xb0')
                # bleah
                entity['lat'] = float(deg) + float(min[0:-1])/60

            if '\xc2\xb0' in lon_string:
                deg, min = lon_string.split('\xc2\xb0')
                # bleah
                entity['lon'] = float(deg) + float(min[0:-1])/60
    return entities

@m.command
def mock_from_csv(filename):
    """Pass a csv file
    Helps if the csv exhibits a schema like the Provider model
    """
    entities = _consume_csv(filename)
    for entity in entities:
        p = Provider(user=User())
        print entity['business_name']
        p.business_name = entity.pop('business_name')
        p.location = Location(entity.pop('lat'), entity.pop('lon'))
        p.address = Address(**entity)
        p.menus = _build_menus()
        p.save()
        # TODO indexing it here
        resp = indexer.index_one(p, id=p.id)
        print resp


def _make_context():
    return dict(
            app=create_app(),
            db=db,
            ud=ud,
            User=User,
            Role=Role,
            Provider=Provider,
            Consumer=Consumer,
            Address=Address,
            Gallery=Gallery,
            Photo=Photo,
            Location=Location,
            Menu=Menu,
            p=Provider.query.get(4),
            c=Consumer.query.first(),
            jsoner=JSONEncoder(),
            pprint=pprint,
            es=indexer.es
            )

port = os.environ.get('PORT', '3000')
host = os.environ.get('HOST', '127.0.0.1')
m.add_option('-c', '--config', dest='config', required=False)
m.add_option('-i', '--instance', dest='instance_path', required=False)
m.add_command('run', Server(port=port, host=host))
m.add_command('shell', Shell(make_context=_make_context))


if __name__ == '__main__':
    m.run()
