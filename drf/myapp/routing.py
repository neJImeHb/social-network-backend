from django.urls import path

from .consumers import WSMessage

ws_urlpatterns = [
    path('ws/messages/', WSMessage.as_asgi()),
]