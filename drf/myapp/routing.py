from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/online/(?P<userID>\w+)/$', consumers.OnlineStatusConsumer.as_asgi()),
    re_path(r'ws/users/status/(?P<user_ids>[\w,]+)/$', consumers.UserStatusConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<user_id>\d+)/(?P<room_id>\d+)/$', consumers.ChatConsumer.as_asgi()),  
]
