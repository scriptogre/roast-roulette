# ruff: noqa: E501

from .base import *  # noqa: F403
from .base import INSTALLED_APPS

# WhiteNoise
# ------------------------------------------------------------------------------
# http://whitenoise.evans.io/en/latest/django.html#using-whitenoise-in-development
INSTALLED_APPS = ['whitenoise.runserver_nostatic', *INSTALLED_APPS]
