from .base import *

DEBUG = False
DEVELOPMENT = False


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'z*lj!h50z8z71$2yc$pe$f$ucl57p)vi(ejd8om$#543ko+q0p'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

PDF_SERVER = 'http://printservice.jimbogo.com'
RKZBIOS_WEBSITE = 'http://rkzbios.nl'
MOLIE_API_KEY = ""

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'rkzbios',
    'USER': 'rkzbios',
    'PASSWORD': 'welcome',
    'HOST': 'db', # Or an IP Address that your DB is hosted on
    'PORT': '',
  }
}

CORS_ORIGIN_ALLOW_ALL = True

try:
    from .local import *
except ImportError:
    pass
