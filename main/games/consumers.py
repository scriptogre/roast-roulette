from channels.generic.websocket import AsyncWebsocketConsumer


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

    async def update_game(self, event):
        """
        Method name must match "type" in group_send.
        """
        # Send the data to the client
        await self.send('updateGame')
