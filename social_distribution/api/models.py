from django.db import models
import uuid

# Create your models here.

class Connection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20, null=True)
    url = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.name