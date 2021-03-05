import uuid

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.forms import ModelForm

# https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
# https://stackoverflow.com/questions/16925129/generate-unique-id-in-django-from-a-model-field/30637668

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='author')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    github = models.CharField(max_length=50, blank=True)


    friends = models.ManyToManyField('self')
    following = models.ManyToManyField('self', symmetrical=False, related_name="following_list")
    followers = models.ManyToManyField('self', symmetrical=False, related_name="follower_list")

    # https://stackoverflow.com/questions/18396547/django-rest-framework-adding-additional-field-to-modelserializer
    @property
    def type(self):
        return 'author'

    # https://stackoverflow.com/questions/35584059/django-cant-set-attribute-in-model
    @type.setter
    def type(self, val):
        pass

    @property
    def user_name(self):
        return self.user.username

    @user_name.setter
    def user_name(self, val):
        pass

class Post(models.Model):
    title = models.CharField(max_length=200)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True, related_name="posts")

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

    # https://stackoverflow.com/questions/18396547/django-rest-framework-adding-additional-field-to-modelserializer
    @property
    def type(self):
        return 'post'

    # https://stackoverflow.com/questions/35584059/django-cant-set-attribute-in-model
    @type.setter
    def type(self, val):
        pass

class PostCategory(models.Model):
    name = models.CharField(max_length=50)

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True, related_name="comments")
    content = models.TextField()

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

    timestamp = models.DateTimeField(default=timezone.now)

    # https://stackoverflow.com/questions/18396547/django-rest-framework-adding-additional-field-to-modelserializer
    @property
    def type(self):
        return 'comment'

    # https://stackoverflow.com/questions/35584059/django-cant-set-attribute-in-model
    @type.setter
    def type(self, val):
        pass
