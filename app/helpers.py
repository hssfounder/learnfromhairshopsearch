from flask import current_app, g
import requests
import simplejson as json
from pyelasticsearch.client import _iso_datetime
from six import PY3

from PIL import Image

from boto.s3.connection import S3Connection
from boto.s3.key import Key

from werkzeug import secure_filename


import os

def info(msg):
    current_app.logger.info(msg)

def _get_bucket():
    # return bucket from app.g or make a new one
    if not g.get('bucket', False):
        g.bucket = S3Connection(
                current_app.config['AWS_KEY'],
                current_app.config['AWS_SECRET']
            ).get_bucket( current_app.config['BUCKET_NAME'])
    return g.bucket 


def delete_from_s3(url):
    k = Key(_get_bucket())
    k.key = '/'.join(url.rsplit('/', 2)[1:])
    current_app.logger.info(k.key)
    k.delete()

def put_s3(file_name):
    k = Key(_get_bucket())
    k.key = 'uploads/{}'.format(file_name)
    bytes_up = k.set_contents_from_file(open(os.path.join(
        current_app.config['UPLOAD_DIR'],
        file_name
        )))
    k.set_acl('public-read')
    info('~~~| Put {} bytes at key {}'.format(bytes_up, k.key))
    return k.key

def process_img(fh):
    filename = secure_filename(fh.filename)
    s3_put_names = dict(original=filename)
    path = os.path.join(current_app.config['UPLOAD_DIR'], filename)
    fh.save(path)

    for size_name, size in current_app.config['THUMB_SIZES'].items():
        image = Image.open(path)
        image.thumbnail(size, resample=Image.ANTIALIAS)
        save_name = '{}x{}_{}'.format(size[0], size[1], filename)
        save_path = os.path.join(current_app.config['UPLOAD_DIR'],
                save_name)
        image.save(save_path)
        s3_put_names[size_name] = save_name

    s3_keys = {}
    for size_name, put_name in s3_put_names.items():
        key = put_s3(put_name)
        s3_keys[size_name] = current_app.config['S3_URL'] + '/' + key

    # {'lg_thumb': 'uploads/image_name.jpg'}
    return s3_keys


def ellipsize(string, limit=50):
    """Jinja template filter
    Ellipsize that text! Craps out up to limit characters
    """
    return '{}{}'.format(string[0: limit], '...')

def acceptable_url_string(string, proto_string):
    """Clean a string of all it's unnacceptable chars.

    :param string: business name to be cleaned
    :param proto_string: acceptable charset
    """

    res = []
    test_string = string.strip().lower()
    for ch in (char for char in test_string):
        # replace as single whitespace with a single period
        if ch == ' ':
            ch = '.'
        if ch in proto_string:
            res.append(ch)

    res_string = u''.join(res)

    if res_string[-1] == '.':
        return res_string[0:-1]

    return res_string


class JSONSerializer():
    """Smart mixin that tags a SQLAlchemy model as serializable"""

    __json_public__     = None
    __json_hidden__     = None
    __json_modifiers__  = None

    def get_attrs(self):
        for name in self.__mapper__.iterate_properties:
            yield name.key

    def to_json(self):
        names = self.get_attrs()
        public = self.__json_public__ or names
        hidden = self.__json_hidden__ or []
        modifiers = self.__json_modifiers__ or dict()

        ret = dict()
        for key in public:
            ret[key] = getattr(self, key)
        for key, modifier in modifiers.items():
            val = modifier(getattr(self, key))
            ret[key] = val
        for key in hidden:
            ret.pop(key, None)
        return ret

class JSONEncoder(json.JSONEncoder):
    def default(self, value):
        """Convert more Python data types to ES-understandable JSON."""
        iso = _iso_datetime(value)
        if iso:
            return iso

        if not PY3 and isinstance(value, str):
            return unicode(value, errors='replace')  # TODO: Be stricter.

        if isinstance(value, set):
            return list(value)

        if isinstance(value, JSONSerializer):
            return value.to_json()

        return super(JSONEncoder, self).default(value)


class HSSError(Exception):
    def __init__(self, msg):
        self.msg = msg
