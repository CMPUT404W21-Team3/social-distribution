# Generated by Django 3.2 on 2021-04-12 01:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0032_remove_author_followers'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='followers',
            field=models.ManyToManyField(related_name='follower_list', to='Profile.Author'),
        ),
    ]
