# Generated by Django 5.0.6 on 2024-08-23 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0029_comments_likes'),
    ]

    operations = [
        migrations.AddField(
            model_name='posts',
            name='disabled_comments',
            field=models.BooleanField(default=False),
        ),
    ]
