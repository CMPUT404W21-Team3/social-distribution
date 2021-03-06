# Generated by Django 3.1.6 on 2021-04-07 23:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Search', '0005_friendrequest_remote_username'),
        ('Profile', '0023_merge_20210401_1255'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='friend_requests_cleared',
            field=models.ManyToManyField(related_name='friend_requests_cleared', to='Search.FriendRequest'),
        ),
    ]
