import rest_framework.generics
from django.shortcuts import render

from market.models import Market
from market.serializers import MarketSerializer


# Create your views here.
class MarketListAPIView(rest_framework.generics.ListAPIView):
    queryset = Market.objects.all()
    serializer_class = MarketSerializer

