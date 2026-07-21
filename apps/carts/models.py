from django.core import validators
from django.db import models
from apps.users.models import TimeStampedModel
from django.conf import settings
from apps.products.models import Product
from django.core.validators import MinValueValidator


class Cart(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart"
    )


class CartItem(TimeStampedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_item")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="cart_item"
    )
