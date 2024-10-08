# Generated by Django 5.0.6 on 2024-06-29 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_customuser_bio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bio',
            name='biography',
            field=models.CharField(max_length=400, null=True),
        ),
        migrations.AlterField(
            model_name='bio',
            name='birthday_day',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='bio',
            name='birthday_month',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='bio',
            name='birthday_year',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='bio',
            name='status',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
