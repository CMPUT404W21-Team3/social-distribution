# Generated by Django 3.1.6 on 2021-04-08 05:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0024_author_friend_requests_cleared'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='remote_url',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]