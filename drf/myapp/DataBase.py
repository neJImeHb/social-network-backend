from .models import *
from django.utils import timezone
from django.db.models import Q
from channels.db import database_sync_to_async

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

@database_sync_to_async
def GetLastActivity(id):
    instance = CustomUser.objects.get(id=id)
    online_status = instance.online_status
    last_activity = ''
    now = timezone.now()
    now_date = now.date()
    last_activity_time = instance.last_activity
    last_activity_date = last_activity_time.date()
    if last_activity_date != now_date:
        if (now_date - last_activity_date).days > 1:
            last_activity = 'Last activity: ' + last_activity_time.strftime('%H:%M, %d %B')
        elif (now_date - last_activity_date).days == 1:
            last_activity = 'Was online Yesterday at ' + last_activity_time.strftime('%H:%M')
    else:
        last_activity = 'Was online Today at ' + last_activity_time.strftime('%H:%M')

    return last_activity, online_status

def GetDate(unformatted_date):
    now = timezone.now()
    now_date = now.date()
    date = unformatted_date.date()
    
    if date != now_date:
        if (now_date - date).days > 365: formatted = unformatted_date.strftime('%d %B, %Y')
        elif (now_date - date).days > 1 < 365: formatted = unformatted_date.strftime('%H:%M, %d %B')
        elif (now_date - date).days == 1: formatted = 'Yesterday at ' + unformatted_date.strftime('%H:%M')
    else: formatted = unformatted_date.strftime('%H:%M')
    
    return formatted
        
    
