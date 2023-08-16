from django.db import models

from account.models import User
from market.models import Market
from products.models import Product


# Create your models here.
class Shop(models.Model):
    shop_id = models.BigAutoField(primary_key=True, null=False, unique=True)
    user = models.OneToOneField(User, related_name="my_shop", on_delete=models.CASCADE)
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    product = models.ManyToManyField(Product, related_name="shop_selling_product")
    favourites = models.ManyToManyField(User, related_name="user_shop_favourites")
    shop_name = models.CharField(max_length=20)
    shop_address = models.CharField(max_length=50)
    selling_products = models.CharField(max_length=30)
    opening_time = models.CharField(max_length=10)
    closing_time = models.CharField(max_length=10)
    opening_frequency = models.CharField(max_length=10)
    rating = models.FloatField(null=True)
