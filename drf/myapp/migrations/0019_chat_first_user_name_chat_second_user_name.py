# Generated by Django 5.0.6 on 2024-07-12 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0018_chat_messages'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='first_user_name',
            field=models.CharField(max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='chat',
            name='second_user_name',
            field=models.CharField(max_length=25, null=True),
        ),
    ]
