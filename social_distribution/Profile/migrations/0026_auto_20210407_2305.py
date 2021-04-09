# Generated by Django 3.1.6 on 2021-04-08 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0025_post_remote_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='remote_author_id',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='remote_author_username',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]