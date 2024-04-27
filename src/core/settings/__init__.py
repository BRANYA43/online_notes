"""
Combining settings for django project
"""

from split_settings.tools import include

from core.settings.components import env

_settings = (
    'components/base.py',
    'components/{}.py'.format(env.get('DJANGO_SETTINGS_ENV', 'prod').lower()),
)

include(*_settings)
