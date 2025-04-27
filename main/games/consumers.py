import asyncio

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer


async def trigger_clients_refresh(game_code):
    """
    Sends a message to the game group to refresh the game state.
    """
    await get_channel_layer().group_send(game_code, {'type': 'refresh_game'})


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['cookies']['sessionid']
        self.game_code = self.scope['url_route']['kwargs']['game_code']

        # Join the group
        await self.channel_layer.group_add(self.game_code, self.channel_name)

        # Accept the connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(self.game_code, self.channel_name)

    async def refresh_game(self, event):
        """
        Method name must match "type" in group_send.
        """
        await self.send('refreshGame')
