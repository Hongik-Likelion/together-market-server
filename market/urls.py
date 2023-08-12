from django.urls import path

from market.views import MarketListAPIView

urlpatterns = [
    path('', MarketListAPIView.as_view()),
]
