from rest_framework import serializers
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q

from .models import Chat, Messages
from .DataBase import GetCurrentlyUserChats
from .serializers import UserSerilizerForChats, UserSerializerForFriendRequest

User = get_user_model()

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ('id', 'first_user', 'second_user', 'date_created')

class MessagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = ('id', 'chat_id', 'sender_id', 'text', 'date_send', 'date_change', 'date_look')

class CreateChat(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        current_user = request.user
        companion = request.data['user_id']

        chatIsExist = Chat.objects.filter(Q(first_user=current_user.id, second_user=companion) | Q(first_user=companion, second_user=current_user.id)).first()

        if companion:
            if not chatIsExist:
                creating_chat = Chat(first_user=current_user.id, second_user=companion)
                creating_chat.save()
                return Response('Chat is successful created')
            else: return Response('Chat is already exist')
        else: return Response('User is not found')

class GetChats(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        current_user = request.user
        chats = GetCurrentlyUserChats(current_user=current_user)

        users = []
        messages = []
        if chats: 
            for el in chats:
                messages.append(Messages.objects.filter(chat_id=el.id).order_by('-date_send').first())
                if el.first_user != current_user.id:
                    user = User.objects.filter(id=el.first_user).first()
                    users.append(user)
                if el.second_user != current_user.id:
                    user = User.objects.filter(id=el.second_user).first()
                    users.append(user)
        serialized_users = UserSerilizerForChats(users, many=True)
        serialized_chats = ChatSerializer(chats, many=True)
        serialized_messages = MessagesSerializer(messages, many=True)
        return Response({'chats': serialized_chats.data, 'users': serialized_users.data, 'messages': serialized_messages.data, 'current_user_id': current_user.id})
    
class GetCompanion(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        companion_id = request.data['id']
        user = User.objects.filter(id=companion_id).first()
        companion = UserSerializerForFriendRequest(user).data
        return Response(companion)
    
class SendMessage(APIView):
    permission_classes = [IsAuthenticated]
        
    def post(self, request):
        current_user = request.user
        current_chat = request.data['current_chat']
        message = request.data['message']

        create_message = Messages(chat_id=current_chat, sender_id=current_user.id, text=message)
        create_message.save()

        return Response('Message is succesful sended')
    
class GetMessages(APIView):
    def post(self, request):
        current_chat = request.data['current_chat']
        messages = Messages.objects.filter(chat_id=current_chat).order_by('-date_send').all()
        serialized_messages = MessagesSerializer(messages, many=True).data
        return Response(serialized_messages)


