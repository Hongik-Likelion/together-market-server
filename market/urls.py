from django.urls import path

from market.views import post_favourite_market, get_market_list_view

urlpatterns = [
    path('', get_market_list_view),
    path('favourite/', post_favourite_market),
]
