from django.db import models
from django.contrib.auth.models import AbstractUser

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.BooleanField(default=False, null=True)

    class Meta:
        abstract = True

class User(TimeStampedModel,AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username
    
