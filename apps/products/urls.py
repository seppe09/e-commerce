from django.urls import path
from .views import ProductListView, ProductCreateView, ProductEditView


urlpatterns = [
    path("list/", ProductListView.as_view(), name="product_list"),
    path("create/", ProductCreateView.as_view(), name="create_product"),
    path("<int:pk>/edit/", ProductEditView.as_view(), name="product_edit"),
]
