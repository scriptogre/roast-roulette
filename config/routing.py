"""
Websocket URL patterns

Note: django-channels can't use URL namespaces; URLs must be hardcoded in templates.
"""

from channels.routing import URLRouter
from django.urls import path

from main.games.routing import websocket_urlpatterns as games_websocket_urlpatterns

websocket_urlpatterns = [
    path('', URLRouter(games_websocket_urlpatterns)),
]
