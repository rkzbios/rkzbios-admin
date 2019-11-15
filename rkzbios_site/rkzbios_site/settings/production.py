from .base import *

DEBUG = False

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


try:
    from .local import *
except ImportError:
    pass
