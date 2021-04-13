from django.db import models
import uuid

# Create your models here.

class Connection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20, null=True, blank=True)
    url = models.CharField(max_length=50, null=True, blank=True)

    incoming_username = models.CharField(max_length=20, null=True, blank=True)
    incoming_password = models.CharField(max_length=20, null=True, blank=True)
    outgoing_username = models.CharField(max_length=20, null=True, blank=True)
    outgoing_password = models.CharField(max_length=20, null=True, blank=True)

    def is_authenticated(self):
        return True

    def __str__(self):
        return self.name