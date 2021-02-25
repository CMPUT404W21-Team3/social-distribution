from django.db import models
from Profile.models import Profile
import uuid
# Create your models here.

VISIBILITY_CHOICES = [
    ('PUBLIC', 'public to everyone'),
    ('PRIVATE', 'private to friends')
]

class Post(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="author")
    # https://stackoverflow.com/a/30637668/12826510
    post_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    unlisted = models.BooleanField(default=False)
    post_body = models.TextField(blank=True)
    visibility = models.CharField(max_length=15, choices=VISIBILITY_CHOICES, default='PUBLIC')
    last_modified = models.DateTimeField(auto_now=True)

class Comment(models.Model):
    commenter = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='commenter')
    comment = models.CharField(max_length=300)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comment_post')
    date_published = models.DateTimeField()

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='like_post')
    who_liked = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="like_author")