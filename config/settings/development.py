import os

from .base import *

DEBUG = True
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-development-only-westminster')

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
