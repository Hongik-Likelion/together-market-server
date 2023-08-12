from django.urls import path

from products.views import products_list_view


urlpatterns = [path("", products_list_view)]
