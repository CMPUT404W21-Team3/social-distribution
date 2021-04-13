from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from Profile.models import Author

# Create your models here.
class Search(models.Model):
    query = models.TextField(max_length=250, blank=True)


class FriendRequest(models.Model):
    receiver = models.ForeignKey(Author, on_delete=models.CASCADE, null=False, related_name='receiver')
    sender = models.ForeignKey(Author, on_delete=models.CASCADE, null=True, blank=True, related_name='sender')
    remote_sender = models.CharField(max_length=100, blank=True, null=True)
    remote_username = models.CharField(max_length=100, blank=True, null=True)

    # https://stackoverflow.com/questions/18396547/django-rest-framework-adding-additional-field-to-modelserializer
    @property
    def type(self):
        return 'Follow'

    # https://stackoverflow.com/questions/35584059/django-cant-set-attribute-in-model
    @type.setter
    def type(self, val):
        pass

    # https://stackoverflow.com/questions/18396547/django-rest-framework-adding-additional-field-to-modelserializer
    @property
    def summary(self):
        try:
            return str(self.sender.user) + ' wants to follow ' + str(self.receiver.user)
        except:
            return 'A remote user' + 'wants to follow' + str(self.receiver.user)

    # https://stackoverflow.com/questions/35584059/django-cant-set-attribute-in-model
    @summary.setter
    def summary(self, val):
        pass

    @property
    def url(self):
        return Site.objects.get_current().domain + reverse('api:author', kwargs={'author_id':self.id})

    @property
    def host(self):
        return Site.objects.get_current().domain
