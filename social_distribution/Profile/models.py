from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

#https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    
    # Not sure if this is the best way to do this
    friends = models.ManyToManyField('self')
    followers = models.ManyToManyField('self', symmetrical=False)

    def __str__(self):
        return self.user.username

class Friend(models.Model):
    friend = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='friend')
    follower = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='follower')
    # pending status: 0 for pending friend request; 1 for following
    status = models.IntegerField(default=0)