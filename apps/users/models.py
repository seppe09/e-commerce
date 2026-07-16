from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True
        
    def soft_delete(self):
        self.deleted_at = timezone.now()

    def restore(self):
        self.deleted_at = None

class User(TimeStampedModel,AbstractUser):
    email = models.EmailField(unique=True)
    is_seller = models.BooleanField(default=False)

    def __str__(self):
        return self.username
    
