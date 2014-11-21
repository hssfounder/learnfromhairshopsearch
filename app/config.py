FILE_LOGGING = True

ELASTICSEARCH_SERVER = 'http://localhost:9200'

THUMB_SIZES = {
        'sm_thumb': (450, 450),
        'lg_thumb': (550, 550)
        }

FILE_LOG = '/tmp/info.hairshopsearch.log'
FILE_ERROR_LOG = '/tmp/error.hairshopsearch.log'
SECRET_KEY = 'dev key'
DEBUG = True
DEBUG_TB_ENABLED = False

ACCEPTABLE_URL_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789."

SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/hairshopsearch.db'
SQLALCHEMY_ECHO = False

WTF_CSRF_ENABLED = True

MAIL_SERVER = 'smtp.mailgun.org'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'timone'
MAIL_PASSWORD = 'pumba'

SECURITY_REGISTERABLE = True
SECURITY_SEND_REGISTER_EMAIL = True
SECURITY_EMAIL_SENDER = 'hairshopsearch-services@hairshopsearch.com'
SECURITY_CONFIRMABLE = True
SECURITY_TRACKABLE = True
SECURITY_PASSWORD_HASH = 'bcrypt'
SECURITY_PASSWORD_SALT = 'salty'
SECURITY_RECOVERABLE = True
SECURITY_CHANGEABLE = True
SECURITY_POST_LOGIN_VIEW = '/dashboard'
SECURITY_POST_REGISTER_VIEW = '/login'
SECURITY_POST_CONFIRM_VIEW = '/welcome'

MAIL_LOGGING = True
MAIL_LOG_FROM = ['HSS_APP_ERROR@hairshopsearch.com']
MAIL_LOG_ADMINS = ['oneofy@gmail.com']

DEBUG = True
GEOCODING_SERVICE_URI = 'http://www.mapquestapi.com/geocoding/v1/address'

LESS_BIN = 'lessc'
LESS_PREPROCESS = True
CSS_BUNDLES = {
        'css': (
            'css/jquery.nailthumb.1.1.min.css',
            'css/main.less'
            )
        }

JS_BUNDLES = {
        'js': (
            'js/main.js'
        ),

        'mod': ()
    }
