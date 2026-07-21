from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Cart, CartItem
from django.contrib.auth import logout , login

class AddToCart(LoginRequiredMixin, View):
    login_url = "login_view"

    def post(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        if created:
            CartItem.objects.create(
                cart=cart, product=product, quantity=1
            )
        CartItem.objects.update(quantity=Cart)
