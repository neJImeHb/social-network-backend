from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from model_utils import FieldTracker
import os

class CustomUser(AbstractUser):
    last_activity = models.DateTimeField(default=timezone.now)
    online_status = models.BooleanField(default=False)
    tracker = FieldTracker(fields=['online_status'])
    phone = models.IntegerField(null=True)
    bio = models.ForeignKey('Bio', on_delete=models.CASCADE, null=True)
    avatar = models.TextField(default='avatar_default.jpg')
    avatar_id = models.IntegerField(default=0)


class Bio(models.Model):
    status = models.CharField(max_length=100, null=True)
    biography = models.CharField(max_length=400, null=True)
    birthday_day = models.IntegerField(null=True)
    birthday_month = models.CharField(max_length=255, null=True)
    birthday_year = models.IntegerField(null=True)
    show = models.BooleanField(default=False)

class Friends(models.Model):
    from_user = models.IntegerField(null=True)
    date_send = models.DateTimeField(null=True)
    to_user = models.IntegerField(null=True)
    is_accept = models.BooleanField(default=False)
    date_friend = models.DateTimeField(null=True)
    in_subscribe = models.BooleanField(default=False)

class Chat(models.Model):
    first_user = models.IntegerField()
    second_user = models.IntegerField()
    date_created = models.DateTimeField(auto_now_add=True)
    reader = models.IntegerField(null=True)
    read = models.BooleanField(null=True)

    def __str__(self):
        return self.id, self.first_user, self.second_user, self.date_created

class Messages(models.Model):
    chat_id = models.IntegerField()
    sender_id = models.IntegerField()
    text = models.TextField()
    date_send = models.DateTimeField(auto_now_add=True)
    date_change = models.DateTimeField(null=True)
    date_look = models.DateTimeField(null=True)

    def __str__(self):
        return self.id, self.chat_id, self.sender_id, self.date_send, self.date_change, self.date_look
    
class Posts(models.Model):
    user_id = models.IntegerField()
    file_name = models.TextField(null=True)
    description = models.TextField(null=True)
    date = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)
    disabled_comments = models.BooleanField(default=False)
    only_friends_can_see = models.BooleanField()
    
class Likes(models.Model):
    post_id = models.IntegerField()
    from_user = models.IntegerField()

class Comments(models.Model):
    post_id = models.IntegerField()
    from_user = models.IntegerField()
    text = models.TextField()
    