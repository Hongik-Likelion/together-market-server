from django.urls import path

from shop.views import (
    ShopView,
    add_shop_favourites_view,
    fetch_shop_detail_view,
    remove_shop_favourites_view,
)


urlpatterns = [
    path("", ShopView.as_view()),
    path("<int:shop_id>", fetch_shop_detail_view),
    path("<int:shop_id>/favourite", add_shop_favourites_view),
    path("<int:shop_id>/de-favourite", remove_shop_favourites_view),
]
