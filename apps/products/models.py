from django.db import models
from django.conf import settings
from apps.users.models import TimeStampedModel

class Category(TimeStampedModel, models.Model):
    name = models.CharField("Category Name", max_length=200)

    def __str__(self):
        return self.name
    

class Product(TimeStampedModel, models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="products")
    name = models.CharField(max_length=200)
    price = models.DecimalField(decimal_places=2, max_digits=8)
    description = models.TextField(max_length=600)
    image = models.ImageField(upload_to="products/")

    def __str__(self):
        return f"{self.name} - ({self.price})"