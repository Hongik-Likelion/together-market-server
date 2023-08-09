from django.db import models

from account.models import User


# Create your models here.
class Market(models.Model):
    market_id = models.BigAutoField(primary_key=True, null=False, unique=True)
    market_name = models.CharField(max_length=30)
    street_address = models.CharField(max_length=50)
    postal_address = models.CharField(max_length=50)
    has_toilet = models.BooleanField()
    has_parking = models.BooleanField()


class Shop(models.Model):
    shop_id = models.BigAutoField(primary_key=True, null=False, unique=True)
    market_id = models.ForeignKey(Market, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    shop_name = models.CharField(max_length=20)
    shop_address = models.CharField(max_length=50)
    selling_products = models.CharField(max_length=30)
    opening_time = models.CharField(max_length=10)
    closing_time = models.CharField(max_length=10)
    opening_frequency = models.CharField(max_length=10)
    rating = models.FloatField()

