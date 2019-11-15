from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'z_d-6+7j0a&bjzp^(w-6jcy8wa0t!+z0_n*2(guw$3!3@n1&ld'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*'] 

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'rkzbios',
    'USER': 'rkzbios',
    'PASSWORD': 'welcome',
    'HOST': '127.0.0.1', # Or an IP Address that your DB is hosted on
    'PORT': '3306',
  }
}

try:
    from .local import *
except ImportError:
    pass
