import asyncio

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer


async def arefresh_game(game_code):
    """
    Sends a message to the game group to refresh the game state.
    """
    await get_channel_layer().group_send(game_code, {'type': 'refresh_game'})


def refresh_game(game_code):
    """
    Sends a message to the game group to refresh the game state.
    """
    async_to_sync(arefresh_game)(game_code)


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

    async def start_timer_for_round(self):
        """Async task to wait 60 seconds and update the round state."""
        from main.games.models import Game

        # Wait for 60 seconds
        await asyncio.sleep(60)

        # Retrieve game and current round
        game = await Game.objects.aget(code=self.game_code)
        round = game.current_round

        # Timer expired, transition to next state
        if round.seconds_left <= 0:
            round.transition_to_next_state()
            refresh_game(self.game_code)
