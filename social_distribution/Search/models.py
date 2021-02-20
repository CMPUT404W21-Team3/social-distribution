from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Search(models.Model):
    query = models.TextField(max_length=250, blank=True)


class FriendRequest(models.Model):
    type = models.CharField(max_length=25, blank=True)
    sender = models.CharField(max_length=50, blank=True)
    receiver = models.CharField(max_length=50, blank=True)
