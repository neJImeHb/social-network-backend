from .models import *
from django.utils import timezone
from django.db.models import Q

def update_activity(username):
    user = CustomUser.objects.filter(username=username).first()
    if user:
        user.last_activity = timezone.now()
        user.save()
        return user.last_activity.strftime("%H:%M, %d %B")
    
def isFriends(current_user, friend_user):
    is_friends = Friends.objects.filter(Q(from_user=current_user, to_user=friend_user) | Q(to_user=current_user, from_user=friend_user)).all()
    return is_friends

def GetCurrentlyUserChats(current_user):
    chats = Chat.objects.filter(Q(first_user=current_user.id) | Q(second_user=current_user.id))
    type(chats)
    return chats
    
