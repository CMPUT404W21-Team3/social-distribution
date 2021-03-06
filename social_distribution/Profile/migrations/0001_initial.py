# Generated by Django 3.1.6 on 2021-03-05 21:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('bio', models.TextField(blank=True, max_length=500)),
                ('location', models.CharField(blank=True, max_length=30)),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('github', models.CharField(blank=True, max_length=50)),
                ('followers', models.ManyToManyField(related_name='follower_list', to='Profile.Author')),
                ('following', models.ManyToManyField(related_name='following_list', to='Profile.Author')),
                ('friends', models.ManyToManyField(related_name='_author_friends_+', to='Profile.Author')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='author', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('content', models.TextField()),
                ('content_type', models.CharField(choices=[('text/markdown', 'Markdown'), ('text/plain', 'Plain'), ('application/base64', 'Base64'), ('image/png;base64', 'Png'), ('image/jpeg;base64', 'Jpeg')], default='text/plain', max_length=40)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='Profile.author')),
            ],
        ),
        migrations.CreateModel(
            name='PostCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('title', models.CharField(max_length=200)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('url', models.CharField(blank=True, max_length=200)),
                ('source', models.CharField(blank=True, max_length=200)),
                ('origin', models.CharField(blank=True, max_length=200)),
                ('description', models.TextField(blank=True)),
                ('content_type', models.CharField(choices=[('text/markdown', 'Markdown'), ('text/plain', 'Plain'), ('application/base64', 'Base64'), ('image/png;base64', 'Png'), ('image/jpeg;base64', 'Jpeg')], default='text/plain', max_length=40)),
                ('content', models.TextField(blank=True)),
                ('comments_count', models.IntegerField(default=0)),
                ('comments_page_size', models.IntegerField(default=50)),
                ('comments_first_page', models.CharField(max_length=200, null=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('visibility', models.CharField(choices=[('PUBLIC', 'Public'), ('FRIENDS', 'Friends')], default='PUBLIC', max_length=10)),
                ('unlisted', models.BooleanField(default=False)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='Profile.author')),
                ('categories', models.ManyToManyField(blank=True, to='Profile.PostCategory')),
                ('comments', models.ManyToManyField(blank=True, to='Profile.Comment')),
            ],
        ),
    ]
