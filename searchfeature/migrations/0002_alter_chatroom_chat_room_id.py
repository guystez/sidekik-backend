# Generated by Django 4.2 on 2023-06-23 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("searchfeature", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chatroom",
            name="chat_room_id",
            field=models.IntegerField(null=True),
        ),
    ]
