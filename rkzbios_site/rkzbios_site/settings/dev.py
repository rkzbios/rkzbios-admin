from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
DEVELOPMENT = True
TEST_MAIL_ADDRESS = "robert.hofstra@gmail.com"

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'z_d-6+7j0a&bjzp^(w-6jcy8wa0t!+z0_n*2(guw$3!3@n1&ld'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*'] 

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
PDF_SERVER = 'http://printservice.jimbogo.com'
RKZBIOS_WEBSITE = 'http://localhost:4000'
MOLIE_API_KEY = "test_wAbEvcUCtfjRRpVbVD4GWHMWvCFa7C"
MOLLIE_CALLBACK_HOST = "http://localhost"
MAIL_SENDER_NAME = "rkzbios"
MAIL_FROM = "Tickets <info@sandbox61f33e3f23e243a68558ea6e52171ba7.mailgun.org>"

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

CORS_ORIGIN_ALLOW_ALL = True

try:
    from .local import *
except ImportError:
    pass



LOG_DIR = "/home/roho/local-dev-data/rkz-media/log"
LOG_LEVEL = 'DEBUG'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': LOG_LEVEL,
            'class': 'logging.FileHandler',
            'filename': LOG_DIR + '/base.log'
        },
        'tickets-log-file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOG_DIR + '/ticketing.log'
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
        },
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'tickets': {
            'handlers': ['tickets-log-file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}