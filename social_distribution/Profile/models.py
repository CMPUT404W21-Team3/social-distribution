from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.forms import ModelForm

#https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    # Not sure if this is the best way to do this
    friends = models.ManyToManyField('self')
    following = models.ManyToManyField('self', symmetrical=False)

    def __str__(self):
        return self.user.username

class Post(models.Model):
    title = models.CharField(max_length=200)
    url = models.CharField(max_length=200, blank=True)
    source = models.CharField(max_length=200, blank=True)
    origin = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)

    class ContentType(models.TextChoices):
        MARKDOWN = 'text/markdown' # common mark
        PLAIN = 'text/plain' # UTF-8
        BASE64 = 'application/base64'
        PNG = 'image/png;base64' # embedded png
        JPEG = 'image/jpeg;base64' # embedded jpeg

    content_type = models.CharField(
        max_length=40,
        choices = ContentType.choices,
        default=ContentType.PLAIN
    )

    content = models.TextField(blank=True)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, related_name="posts")

    categories = models.ManyToManyField('PostCategory', blank=True)
    comments_count = models.IntegerField(default=0)
    comments_page_size = models.IntegerField(default=50)
    comments_first_page = models.CharField(max_length=200, null=True) # URL to first page of comments for this post
    comments = models.ManyToManyField('Comment', blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Visibility(models.TextChoices):
        PUBLIC = 'PUBLIC'
        FRIENDS = 'FRIENDS'

    visibility = models.CharField(
        max_length=10,
        choices=Visibility.choices,
        default=Visibility.PUBLIC
    )

    unlisted = models.BooleanField(default=False) # used for images so that they don't show up in timelines

    # count for likes made to the post
    likes_count = models.IntegerField(default=0)

class PostCategory(models.Model):
    name = models.CharField(max_length=50)

class Comment(models.Model):
    content = models.TextField()
