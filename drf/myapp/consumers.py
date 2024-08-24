import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from django.utils import timezone
from .DataBase import GetLastActivity
from django.core.cache import cache

from .models import Messages, CustomUser, Chat
User = get_user_model()

class OnlineStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.current_user = self.scope['url_route']['kwargs']['userID']
        self.group_name = f'group_{self.current_user}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        await self.ChangeOnlineStatus(self.current_user, True)

    async def disconnect(self, close_code):
        await self.ChangeOnlineStatus(self.current_user, False)

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    @database_sync_to_async
    def ChangeOnlineStatus(self, current_user, status):
        user = CustomUser.objects.get(id=current_user)
        user.online_status = status
        if not status:
            user.last_activity = timezone.now()
        user.save()

class UserStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user_ids_str = self.scope['url_route']['kwargs'].get('user_ids')
        
        # Разделяем строку с идентификаторами пользователей и формируем имена групп
        self.user_ids = user_ids_str.split(',')
        self.group_names = [f"user_{user_id}_status" for user_id in self.user_ids]
        
        for group_name in self.group_names:
            await self.channel_layer.group_add(group_name, self.channel_name)
        
        await self.accept()

        for user_id in self.user_ids:
            last_activity, online_status = await GetLastActivity(user_id)
            await self.send(text_data=json.dumps({
                'user_id': user_id,
                'new_status': online_status,
                'last_activity': last_activity,
            }))

    async def disconnect(self, close_code):
        for group_name in self.group_names:
            await self.channel_layer.group_discard(group_name, self.channel_name)

    async def receive(self, text_data):
        pass

    async def send_status_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))



class ChatConsumer(AsyncWebsocketConsumer):
    # Хранение подключенных пользователей
    connected_users = []

    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_name = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_name}'

        # Добавление пользователя в список
        if self.user_id not in self.connected_users:
            self.connected_users.append(int(self.user_id))

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        
        await self.accept()
        print(self.room_name, self.room_group_name, self.user_id)
        print(f"Connected users: {self.connected_users}")

    async def disconnect(self, close_code):
        # Удаление пользователя из списка при отключении
        if self.user_id in self.connected_users:
            self.connected_users.remove(self.user_id)

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )
        
        print(f"Disconnected user {self.user_id} from room {self.room_group_name}")
        print(f"Remaining users: {self.connected_users}")

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json['action']
        if action == 'save_message':
            message = text_data_json['message']
            userID = text_data_json['userID']
            recipient = text_data_json['recipient']

            await self.save_message(self.room_name, userID, message, recipient)  # Save message here

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'userID': userID,
                    'action': action,
                }
            )
        elif action == 'edit_message':
            message = text_data_json['message']
            userID = text_data_json['userID']
            message_id = text_data_json['message_id']

            await self.edit_message(message_id, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'userID': userID,
                    'action': action,
                }
            )
        elif action == 'delete_message':
            message_id = text_data_json['message_id']

            await self.delete_message(message_id)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message_id': message_id,
                    'action': action,
                }
            )

    async def chat_message(self, event):
        action = event['action']
        if action in ['save_message', 'edit_message']:
            message = event['message']
            userID = event['userID']
            print(f"Chat message called with message: {message} and userID: {userID}")

            await self.send(text_data=json.dumps({
                'message': message,
                'sender_id': userID,
                'action': action,
            }))
        elif action == 'delete_message':
            message_id = event['message_id']
            print(f"Chat message called with deleted message_id: {message_id}")

            await self.send(text_data=json.dumps({
                'message_id': message_id,
                'action': action,
            }))

    @database_sync_to_async
    def save_message(self, chat_id, sender_id, message, recipient):
        msgs = Messages(chat_id=chat_id, sender_id=sender_id, text=message)
        chat = Chat.objects.get(id=chat_id)
        chat.reader = recipient
        chat.read = recipient in self.connected_users
        print(recipient in self.connected_users)
        print(recipient)
        print(self.connected_users)
        msgs.save()
        chat.save()

    @database_sync_to_async
    def edit_message(self, message_id, message):
        msgs = Messages.objects.get(id=message_id)
        msgs.text = message
        msgs.date_change = timezone.now()
        msgs.save()

    @database_sync_to_async
    def delete_message(self, message_id):
        msgs = Messages.objects.get(id=message_id)
        msgs.delete()
