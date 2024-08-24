from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
import os

from .models import Friends, CustomUser
from .serializers import *

from .DataBase import *

class FriendsSerializer(serializers.ModelSerializer):
    date_send = serializers.SerializerMethodField()
    date_friend = serializers.SerializerMethodField()

    class Meta:
        model = Friends
        fields = ['id', 'from_user', 'to_user', 'date_send', 'date_friend']

    def get_date_send(self, obj):
        return obj.date_send.strftime('%H:%M, %d %B, %Y')
    
    def get_date_friend(self, obj):
        if obj.date_friend:
            return obj.date_friend.strftime('%d %B, %Y')
        return None

class FriendRequest(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        friend_id = request.data['friend_id']

        checkToRequestExist = Friends.objects.filter(Q(from_user=user.id, to_user=friend_id) | Q(to_user=user.id, from_user=friend_id))

        if checkToRequestExist:
            return Response('Request is already exist')
        else:
            friends = Friends(from_user=user.id, date_send=timezone.now(), to_user=friend_id)
            friends.save()
            return Response({'msg': 'Request to friend is currently sent'})

class CheckFriendsRequests(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        current_user = request.user
        rf = Friends.objects.filter(to_user=current_user.id, is_accept=False, in_subscribe=False).order_by('-date_send').first()

        data = ''
        if rf:
            user = CustomUser.objects.filter(id=rf.from_user).first()
            data = {
                'id': rf.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'sender_username': user.username,
                'date_send': rf.date_send.strftime('%H:%M, %d %B, %Y')
            }
        if data:
            return Response(data)
        else: return Response (None)

class CheckAllFriendsRequests(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        current_user = request.user
        rf = Friends.objects.filter(to_user=current_user.id, is_accept=False).order_by('-date_send').all()

        user_ids = [friend.from_user for friend in rf]
        users = CustomUser.objects.filter(id__in=user_ids)

        serializer = FriendsSerializer(rf, many=True)
        user_serializer = UserSerializerForFriendRequest(users, many=True)

        data = ''
        if rf:
            data = {
                'friends': serializer.data,
                'users': user_serializer.data
            }
        
        return Response({'data': data})
    
class AcceptFriendRequest(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request_id = request.data['request_id']
        rf = Friends.objects.filter(id=request_id).first()
        
        if rf:
            rf.is_accept = True
            rf.date_friend = timezone.now()
            rf.save()
            return Response('Request is successful accepted')
        else: return Response('Request is not found')

class RejectFriendRequest(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request_id = request.data['request_id']
        rf = Friends.objects.filter(id=request_id).first()
        
        if rf:
            rf.in_subscribe = True
            rf.save()
            return Response('Request is successful rejected')
        else: return Response('Request is not found')

class CheckFriendList(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request_username = request.data['username']
        current_user = CustomUser.objects.filter(username=request_username).first()
        if current_user:
            rf = Friends.objects.filter(Q(from_user=current_user.id) | Q(to_user=current_user.id), is_accept=True).all()

            UserList = []
            seen = set()

            for el in rf:
                if el.from_user != current_user.id and el.from_user not in seen:
                    UserList.append(el.from_user)
                    seen.add(el.from_user)
                if el.to_user != current_user.id and el.to_user not in seen:
                    UserList.append(el.to_user)
                    seen.add(el.to_user)

            user_ids = [friend for friend in UserList]
            users = CustomUser.objects.filter(id__in=user_ids)

            avatarList = []

            for usr in users:
                avatar_path = os.path.join('myapp/images/avatars', usr.avatar)

                if os.path.exists(avatar_path):
                # Return the URL path instead of the file itself
                    avatar_url = request.build_absolute_uri(f'/images/avatars/{usr.avatar}')
                    avatarList.append({'id': usr.id, 'avatar_url': avatar_url})

            user_data = UserSerializerForFriendRequest(users, many=True).data
            friend_data = FriendsSerializer(rf, many=True).data

            return Response({'friend_data': friend_data, 'user_data': user_data, 'avatarList': avatarList})
        else: return Response({'not_found': 'User is not found :('})

class ProfileFriends(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        username = request.data.get('username')
        current_user = request.user
        user = CustomUser.objects.filter(username=username).first()

        if user:
            is_friends = isFriends(current_user.id, user.id)
            friend = IsFriendsSerializer(is_friends, many=True)

            YouAreSubscriber = False
            RequestIsSended = False
            YouDidRejected = False
            YouCanToAccept = False

            for el in is_friends:
                if el.to_user == current_user.id and not el.is_accept:
                    YouCanToAccept = True
                    
                if el.from_user == current_user.id and el.in_subscribe:
                    YouAreSubscriber = True

                if el.from_user == current_user.id and not el.in_subscribe and not el.is_accept:
                    RequestIsSended = True

                if el.to_user == current_user.id and el.in_subscribe:
                    YouDidRejected = True


            return Response({'friend': friend.data, 'YouAreSubscriber': YouAreSubscriber, 'RequestIsSended': RequestIsSended, 'YouDidRejected': YouDidRejected, 'YouCanToAccept': YouCanToAccept})
        else: return Response(False)

class ToBeFriends(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        friend_id = request.data.get('friend_id')
        rf = Friends.objects.filter(id=friend_id).first()
        
        rf.in_subscribe = False
        rf.is_accept = True
        rf.date_friend = timezone.now()
        rf.save()

        return Response('Is successfully accepted')
    
class RemoveFriend(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        friend_id = request.data.get('friend_id')
        rf = Friends.objects.filter(id=friend_id).first()
        
        rf.delete()

        return Response('Is successfully deleted')