# Generated by Django 5.0.6 on 2024-07-04 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_alter_customuser_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='phone',
            field=models.IntegerField(null=True),
        ),
    ]
