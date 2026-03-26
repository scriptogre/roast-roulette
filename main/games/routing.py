from django.urls import path

from main.games.consumers import GameConsumer

websocket_urlpatterns = urlpatterns = [
    path('<str:game_code>/', GameConsumer.as_asgi()),
]
