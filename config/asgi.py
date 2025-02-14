# ruff: noqa
"""
ASGI config for Expert Systems Platform project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/asgi/

"""

import os
import sys
from pathlib import Path

from django.core.asgi import get_asgi_application

from . import routing

# This allows easy placement of apps within the interior
# app directory.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
sys.path.append(str(BASE_DIR / 'main'))

# If DJANGO_SETTINGS_MODULE is unset, default to the local settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

# This application object is used by any ASGI server configured to use this file.
django_application = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

application = ProtocolTypeRouter(
    {
        'http': django_application,
        'websocket': AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns))
        ),
    }
)
