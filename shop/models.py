from django.db import models

from account.models import User
from market.models import Market


# Create your models here.

class Shop(models.Model):
    shop_id = models.BigAutoField(primary_key=True, null=False, unique=True)
    market_id = models.ForeignKey(Market, on_delete=models.CASCADE)
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    shop_name = models.CharField(max_length=20)
    shop_address = models.CharField(max_length=50)
    selling_products = models.CharField(max_length=30)
    opening_time = models.CharField(max_length=10)
    closing_time = models.CharField(max_length=10)
    opening_frequency = models.CharField(max_length=10)
    rating = models.FloatField()

