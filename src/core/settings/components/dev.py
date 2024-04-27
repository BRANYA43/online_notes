"""
Development settings
"""

from core.settings import env
from core.settings.components import BASE_DIR
from core.settings.components.base import INSTALLED_APPS, MIDDLEWARE

DEBUG = True

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: True,
}
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']

if env.get('DOCKER_RUN', '').lower() in ('true', '1'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'HOST': env.get('POSTGRES_HOST'),
            'PORT': env.get('POSTGRES_PORT', '5432'),
            'NAME': env.get('POSTGRES_DB'),
            'USER': env.get('POSTGRES_USER'),
            'PASSWORD': env.get('POSTGRES_PASSWORD'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(BASE_DIR / '../db.sqlite3'),
        }
    }
