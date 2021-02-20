from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	"""
	If new user added, create a profile for that user.
	Parameters
	----------
	sender: User model
	instance: a User model instance
	Returns
	-------
	Create a Profile model (refer it to the User model as well)
	"""
	if created:
		Profile.objects.create(user=instance)
