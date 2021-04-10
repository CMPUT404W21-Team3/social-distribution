from django.db import models
import uuid
from django.contrib.auth.models import User

# Create your models here.

class Connection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20, null=True)
    url = models.CharField(max_length=50, null=True)
    incoming_username = models.CharField(max_length=20, null=True)
    incoming_password = models.CharField(max_length=20, null=True)
    outgoing_username = models.CharField(max_length=20, null=True)
    outgoing_password = models.CharField(max_length=20, null=True)

    def is_authenticated(self):
        return True

    def __str__(self):
        return self.name