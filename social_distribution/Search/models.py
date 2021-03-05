from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from Profile.models import Author

# Create your models here.
class Search(models.Model):
    query = models.TextField(max_length=250, blank=True)


class FriendRequest(models.Model):
    sender = models.ForeignKey(Author, on_delete=models.CASCADE, null=False, related_name='sender')
    receiver = models.ForeignKey(Author, on_delete=models.CASCADE, null=False, related_name='receiver')
