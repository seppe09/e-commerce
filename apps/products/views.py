from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from decimal import Decimal
from .models import Product, Category

# Create your views here.

class ProductListView(View):
    template_name = "products/list.html"

    def get(self, request):
        # Retrieve all active (non-deleted) products
        products = Product.objects.filter(is_deleted=False).order_by("-created_at")
        
        context = {
            "products": products
        }

        return render(request, self.template_name, context)


class ProductCreateView(LoginRequiredMixin, View):
    login_url = "login_view"
    template_name = "products/create.html"

    def get(self, request):
        context = {
            "categories": Category.objects.all()
        }
        return render(request, self.template_name, context)

    def post(self, request):
        category_id = request.POST.get("category", "")
        name = request.POST.get("name", "").lower().strip()
        price_str = request.POST.get("price", "").strip()
        description = request.POST.get("description", "").lower().strip()
        image = request.FILES.get("image", "")

        errors = {}

        if not category_id:
            errors["category"] = "Please select a category."
        
        if not name:
            errors["name"] = "Product name is required."
        
        if not price_str:
            errors["price"] = "Product price is required."
        else:
            try:
                price = Decimal(price_str)
                if price <= 0:
                    errors["price"] = "Price must be greater than zero."
            except ValueError:
                errors["price"] = "Invalid price amount."

        if not description:
            errors["description"] = "Product description is required."

        if not image:
            errors["image"] = "Product image is required."

        if errors:
            context = {
                "errors": errors,
                "categories": Category.objects.all(),
                "data": request.POST
            }

            return render(request, self.template_name, context)

        category = Category.objects.get(id=category_id) if category_id else None
        
        product = Product.objects.create(
            category = category,
            name = name,
            price = price,
            description = description,
            image = image,
            seller = request.user
        )

        messages.success(request, "Product created successfully.")
        return redirect("product_list")


class ProductEditView(LoginRequiredMixin, View):
    login_url = "login_view"
    template_name = "products/edit.html"

    def get(self, request, pk):
        if not request.user.is_seller:
            return redirect("dashboard_view")

        product = get_object_or_404(Product, pk=pk, seller=request.user)
        categories = Category.objects.all()

        context = {
            "product": product,
            "categories": categories
        }

        return render(request, self.template_name, context)

    def post(self, request, pk):
        if not request.user.is_seller:
            return redirect("dashboard_view")

        categories = Category.objects.all()
        product = get_object_or_404(Product, pk=pk, seller=request.user)

        category_id = request.POST.get("category", "")
        name = request.POST.get("name", "").lower().strip()
        price_str = request.POST.get("price", "").strip()
        description = request.POST.get("description", "").lower().strip()
        image = request.FILES.get("image", "")

        errors = {}

        # Validate and assign name
        if not name:
            errors["name"] = "Product name is required."
        else:
            product.name = name

        # Validate and assign category
        if not category_id:
            errors["category"] = "Please select a category."
        else:
            try:
                category = Category.objects.get(id=category_id)
                product.category = category
            except Category.DoesNotExist:
                errors["category"] = "Selected category does not exist."

        # Validate and assign price
        if not price_str:
            errors["price"] = "Product price is required."
        else:
            try:
                price = Decimal(price_str)
                if price <= 0:
                    errors["price"] = "Price must be greater than zero."
                else:
                    product.price = price
            except ValueError:
                errors["price"] = "Invalid price amount."

        # Validate and assign description
        if not description:
            errors["description"] = "Product description is required."
        else:
            product.description = description

        # Handle optional image replacement
        if image:
            product.image = image

        if errors:
            context = {
                "errors": errors,
                "categories": categories,
                "product": product,
                "data": request.POST
            }
            return render(request, self.template_name, context)
        
        product.save()

        messages.success(request, "Product updated successfully.")
        return redirect("product_list")


class ProductDeleteView(LoginRequiredMixin, View):
    login_url = "login_view"
    template_name = "products/delete.html"

    def get(self, request, pk):
        if not request.user.is_seller:
            return redirect("dashboard_view")
        
        # Ensure we only fetch active, non-deleted products
        product = get_object_or_404(Product, pk=pk, seller=request.user, is_deleted=False)

        context = {
            "product": product
        }

        return render(request, self.template_name, context)

    
    def post(self, request, pk):
        if not request.user.is_seller:
            return redirect("dashboard_view")
        
        # Ensure we only fetch active, non-deleted products
        product = get_object_or_404(Product, pk=pk, seller=request.user, is_deleted=False)

        confirmed = request.POST.get("confirmation", "")

        if confirmed:
            product.is_deleted = True
            product.soft_delete()
            product.save(update_fields=["is_deleted", "deleted_at"])
            messages.success(request, "Product deleted successfully.")
            return redirect("product_list")
        
        messages.error(request, "Confirmation failed, No product is deleted.")
        return redirect("product_list")


class ProductRecoveryView(LoginRequiredMixin, View):
    login_url = "login_view"
    template_name = "products/recovery.html"

    def get(self, request, pk):
        if not request.user.is_seller:
            return redirect("dashboard_view")

        # Ensure we fetch the deleted product
        product = get_object_or_404(Product, pk=pk, seller=request.user, is_deleted=True)

        context = {
            "product": product
        }
        
        return render(request, self.template_name, context)

    def post(self, request, pk):
        if not request.user.is_seller:
            return redirect("dashboard_view")

        # Ensure we fetch the deleted product
        product = get_object_or_404(Product, pk=pk, seller=request.user, is_deleted=True)

        confirmed = request.POST.get("confirmation", "")

        if confirmed:
            product.is_deleted = False
            product.restore()
            product.save(update_fields=["is_deleted", "deleted_at"])
            messages.success(request, "Product recovered successfully.")
            return redirect("product_list")

        messages.error(request, "Confirmation failed, No product is recovered.")
        return redirect("product_list")