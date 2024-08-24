from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .DataBase import GetLastActivity

@receiver(post_save, sender=CustomUser)
def user_status_changed(sender, instance, **kwargs):
    channel_layer = get_channel_layer()

    if instance.tracker.has_changed('online_status'):
        last_activity, online_status = async_to_sync(GetLastActivity)(instance.id)

        data = {
            'user_id': instance.id,
            'new_status': instance.online_status,
            'last_activity': last_activity,
        }
        
        # Используем async_to_sync для вызова асинхронной функции group_send
        async_to_sync(channel_layer.group_send)(
            f"user_{instance.id}_status",
            {
                "type": "send_status_update",
                "data": data,
            }
        )
