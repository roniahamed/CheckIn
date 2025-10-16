import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import QueueEntry
from asgiref.sync import sync_to_async


class QueueConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        self.room_group_name = 'queue_group'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def send_queue_update(self, event):
        await self.send(text_data=json.dumps(event))
