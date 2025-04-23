# ruff: noqa: E501

from .base import *  # noqa: F403
from .base import INSTALLED_APPS

# WhiteNoise
# ------------------------------------------------------------------------------
# http://whitenoise.evans.io/en/latest/django.html#using-whitenoise-in-development
INSTALLED_APPS = ['whitenoise.runserver_nostatic', *INSTALLED_APPS]


# django-debug-toolbar
# ------------------------------------------------------------------------------
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#prerequisites
# INSTALLED_APPS += ['debug_toolbar']

# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#middleware
# MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

# https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html#debug-toolbar-config
# DEBUG_TOOLBAR_CONFIG = {
#     'DISABLE_PANELS': [
#         'debug_toolbar.panels.redirects.RedirectsPanel',
#         # Disable profiling panel due to an issue with Python 3.12:
#         # https://github.com/jazzband/django-debug-toolbar/issues/1875
#         'debug_toolbar.panels.profiling.ProfilingPanel',
#     ],
#     'SHOW_TEMPLATE_CONTEXT': True,
# }

# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#internal-ips
# INTERNAL_IPS = ['127.0.0.1', '10.0.2.2']

# Add the Docker gateway to the list of internal IPs
# hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
# INTERNAL_IPS += ['.'.join(ip.split('.')[:-1] + ['1']) for ip in ips]


# django-extensions
# ------------------------------------------------------------------------------
# https://django-extensions.readthedocs.io/en/latest/installation_instructions.html#configuration
INSTALLED_APPS += ['django_extensions']
