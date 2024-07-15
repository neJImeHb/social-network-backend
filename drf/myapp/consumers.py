from channels.generic.websocket import AsyncWebsocketConsumer
import json
from random import randint
import asyncio

class WSMessage(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.send_random_numbers_task = asyncio.create_task(self.send_random_numbers())

    async def disconnect(self, close_code):
        self.send_random_numbers_task.cancel()

    async def send_random_numbers(self):
        try:
            for i in range(1000):
                await self.send(json.dumps({'message': randint(1, 100)}))
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Логика обработки сообщения

        await self.send(text_data=json.dumps({
            'msg': message
        }))
