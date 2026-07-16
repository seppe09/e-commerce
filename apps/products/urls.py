from django.urls import path
from .views import ProductListView, ProductCreateView, ProductEditView, ProductDeleteView, ProductRecoveryView


urlpatterns = [
    path("list/", ProductListView.as_view(), name="product_list"),
    path("create/", ProductCreateView.as_view(), name="create_product"),
    path("<int:pk>/edit/", ProductEditView.as_view(), name="product_edit"),
    path("<int:pk>/delete/", ProductDeleteView.as_view(), name="product_delete"),
    path("<int:pk>/recover/", ProductRecoveryView.as_view(), name="product_recover"),
]
