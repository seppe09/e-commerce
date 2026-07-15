from django.shortcuts import render
from django.views import View
from decimal import Decimal

# Create your views here.

class ProductListView(View):
    template_name = "products/list.html"

    def get(self, request):

        

        return render(request, self.template_name)


class ProductCreateView(View):
    template_name = "products/create.html"

    def get(self, request):
        return render(request, self.template_name)

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

        if not description:
            errors["description"] = "Product description is required."

        if not image:
            errors["image"] = "Product image is required."

        if errors:
            context = {
                "errors": errors,
                "data": {
                    "post-data": request.POST,
                    "files-data": request.FILES,
                }
            }

            return render(request, self.template_name, context)

        price = Decimal(price_str)
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