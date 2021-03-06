# Generated by Django 3.2 on 2021-04-11 01:13

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('Search', '0005_friendrequest_remote_username'),
        ('Profile', '0028_remove_author_friends'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inbox',
            fields=[
                ('follow_items', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inbox_follows', to='Search.friendrequest')),
                ('follow_items_cleared', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inbox_follows_cleared', to='Search.friendrequest')),
                ('post_items', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inbox_posts', to='Profile.post')),
                ('post_items_cleared', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inbox_posts_cleared', to='Profile.post')),
                ('post_like_items', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inbox_likes', to='Profile.postlike')),
                ('post_like_items_cleared', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inbox_likes_cleared', to='Profile.postlike')),
            ],
        ),
        migrations.AddField(
            model_name='author',
            name='inbox',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inbox', to='Profile.inbox'),
        ),
    ]
