import uuid, commonmark

from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.forms import ModelForm
from django.urls import reverse
from django.core.validators import int_list_validator


# https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
# https://stackoverflow.com/questions/16925129/generate-unique-id-in-django-from-a-model-field/30637668

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='author', null=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    github = models.CharField(max_length=50, blank=True)
    url = models.CharField(max_length=300, default="http://localhost:8000/", null=True)

    following = models.ManyToManyField('self', symmetrical=False, related_name="following_list")
    followers = models.ManyToManyField('self', symmetrical=False, related_name="follower_list")


    posts_cleared = models.ManyToManyField('Post', related_name="posts_cleared")
    friend_requests_cleared = models.ManyToManyField('Search.FriendRequest', related_name="friend_requests_cleared")
    # Can't find an effective way of setting displayName for a remote author.
    # Because remote author doesn't have a "user" model linked.
    remote_host = models.CharField(max_length=50, blank=True)
    remote_username = models.CharField(max_length=50, blank=True)

    remote_friends_uuid = models.TextField(validators=[int_list_validator], null=True, blank=True)
    remote_following_uuid = models.TextField(validators=[int_list_validator], null=True, blank=True)
    remote_followers_uuid = models.TextField(validators=[int_list_validator], null=True, blank=True)

    # https://stackoverflow.com/questions/18396547/django-rest-framework-adding-additional-field-to-modelserializer
    @property
    def type(self):
        return 'author'

    # https://stackoverflow.com/questions/35584059/django-cant-set-attribute-in-model
    @type.setter
    def type(self, val):
        pass

    @property
    def displayName(self):
        try:
            return self.user.username
        except:
            return self.remote_username

    @displayName.setter
    def displayName(self, val):
        pass

    @property
    def url(self):
        # return Site.objects.get_current().domain + reverse('api:author', kwargs={'author_id':self.id})
        return self.host + 'author/' + str(self.id) + '/'

    @url.setter
    def url(self, value):
        self.url = value

    @property
    def host(self):
        if self.remote_host:
            return self.remote_host
        else:
            return Site.objects.get_current().domain


    @host.setter
    def host(self, value):
        self.remote_host = value

class Post(models.Model):
    title = models.CharField(max_length=200)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.CharField(max_length=200, blank=True, null=True)
    _host = models.CharField(max_length=50, blank=True, db_column='host') # https://stackoverflow.com/q/1454727
    source = models.CharField(max_length=200, blank=True)
    origin = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)

    remote_url = models.CharField(max_length=200, blank=True, null=True)

    class ContentType(models.TextChoices):
        MARKDOWN = 'text/markdown' # common mark
        PLAIN = 'text/plain' # UTF-8
        BASE64 = 'application/base64'
        PNG = 'image/png;base64' # embedded png
        JPEG = 'image/jpeg;base64' # embedded jpeg

    contentType = models.CharField(
        max_length=40,
        choices = ContentType.choices,
        default=ContentType.PLAIN
    )

    content = models.TextField(blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True, related_name="posts")

    remote_author_id = models.CharField(max_length=200, blank=True, null=True)
    remote_author_displayName = models.CharField(max_length=200, blank=True, null=True)

    categories = models.ManyToManyField('PostCategory', blank=True)
    #comments_count = models.IntegerField(default=0)
    #comments_page_size = models.IntegerField(default=50)
    #comments_first_page = models.CharField(max_length=200, null=True) # URL to first page of comments for this post
    #comments = models.ManyToManyField('Comment', blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    likes_count = models.IntegerField(default=0)

    class Visibility(models.TextChoices):
        PUBLIC = 'PUBLIC'
        FRIENDS = 'FRIENDS'
        PRIVATE = 'PRIVATE'

    visibility = models.CharField(
        max_length=10,
        choices=Visibility.choices,
        default=Visibility.PUBLIC
    )

    to_author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True, blank=True, related_name="to_author")

    unlisted = models.BooleanField(default=False) # used for images so that they don't show up in timelines

    # https://stackoverflow.com/questions/18396547/django-rest-framework-adding-additional-field-to-modelserializer
    @property
    def type(self):
        return 'post'

    # https://stackoverflow.com/questions/35584059/django-cant-set-attribute-in-model
    @type.setter
    def type(self, val):
        pass


    # https://stackoverflow.com/questions/18396547/django-rest-framework-adding-additional-field-to-modelserializer
    @property
    def comments(self):
        return Comment.objects.filter(post_id=id, author=author).all().order_by('-timestamp')[:5]

    # https://stackoverflow.com/questions/35584059/django-cant-set-attribute-in-model
    @comments.setter
    def comments(self, val):
        pass


    @property
    def url(self):
        return Site.objects.get_current().domain + reverse('api:post', kwargs={'author_id':self.author.id, 'post_id':self.id})

    @property
    def host(self):
        if self._host == "":
            return Site.objects.get_current().domain
        else:
            return self._host

    def content_html(self):
        if self.contentType == Post.ContentType.PLAIN:
            return self.content
        elif self.contentType == Post.ContentType.MARKDOWN:
            return commonmark.commonmark(self.content)

class PostCategory(models.Model):
    name = models.CharField(max_length=50)


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, related_name="comments")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True, related_name="commenter")

    content = models.TextField(blank=True)

    # class ContentType(models.TextChoices):
    #     MARKDOWN = 'text/markdown' # common mark
    #     PLAIN = 'text/plain' # UTF-8
    #     BASE64 = 'application/base64'
    #     PNG = 'image/png;base64' # embedded png
    #     JPEG = 'image/jpeg;base64' # embedded jpeg

    # contentType = models.CharField(
    #     max_length=40,
    #     choices = ContentType.choices,
    #     default=ContentType.PLAIN
    # )

    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['timestamp']

    # https://stackoverflow.com/questions/18396547/django-rest-framework-adding-additional-field-to-modelserializer
    @property
    def type(self):
        return 'comment'

    # https://stackoverflow.com/questions/35584059/django-cant-set-attribute-in-model
    @type.setter
    def type(self, val):
        pass

    @property
    def url(self):
        return Site.objects.get_current().domain + reverse('api:comment', kwargs={'author_id':self.author.id, 'post_id':self.post.id, 'comment_id':self.id})

class Like(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True)

    class Meta:
        abstract = True

    # https://stackoverflow.com/questions/18396547/django-rest-framework-adding-additional-field-to-modelserializer
    @property
    def type(self):
        return 'Like'

    # https://stackoverflow.com/questions/35584059/django-cant-set-attribute-in-model
    @type.setter
    def type(self, val):
        pass

    @property
    def url(self):
        return Site.objects.get_current().domain + reverse('api:liked', kwargs={'author_id':self.author.id, 'post_id':self.post.id, 'comment_id':self.id})

    @property
    def host(self):
        return Site.objects.get_current().domain


class CommentLike(Like):
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    comment_id = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True)

    # https://stackoverflow.com/questions/18396547/django-rest-framework-adding-additional-field-to-modelserializer

    # Buggy
    @property
    def object(self):
        return '/author/' + author.id.id + '/posts/' + post_id + '/comments/' + comment_id

    # https://stackoverflow.com/questions/35584059/django-cant-set-attribute-in-model
    @object.setter
    def object(self, val):
        pass

    # https://stackoverflow.com/questions/18396547/django-rest-framework-adding-additional-field-to-modelserializer

    @property
    def summary(self):
        return str(self.user) + "likes your comment"

    # https://stackoverflow.com/questions/35584059/django-cant-set-attribute-in-model
    @summary.setter
    def summary(self, val):
        pass

class PostLike(Like):
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    # https://stackoverflow.com/questions/18396547/django-rest-framework-adding-additional-field-to-modelserializer
    @property
    def object(self):
        return '/author/' + str(Author.id) + '/posts/' + str(self.post_id.id)

    # https://stackoverflow.com/questions/35584059/django-cant-set-attribute-in-model
    @object.setter
    def object(self, val):
        pass

    # https://stackoverflow.com/questions/18396547/django-rest-framework-adding-additional-field-to-modelserializer

    # How to get access to author?
    # Subclass initializer?

    @property
    def summary(self):
        return str(self.user) + " likes your post"

    # https://stackoverflow.com/questions/35584059/django-cant-set-attribute-in-model
    @summary.setter
    def summary(self, val):
        pass
