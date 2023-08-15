from django.db import models

from account.models import User
from market.models import Market
from products.models import Product
from shop.models import Shop


# Create your models here.
class Board(models.Model):
    board_id = models.BigAutoField(primary_key=True, null=False, unique=True)
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    market_name = models.CharField(max_length=30)
    shop_name = models.CharField(max_length=20)
    content = models.CharField(max_length=500)
    rating = models.IntegerField(blank=True)
    created_at = models.DateTimeField(auto_created=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    purchased_products = models.ManyToManyField(Product, related_name="board_purchased_products")


class BoardPhoto(models.Model):
    image_id = models.BigAutoField(primary_key=True, null=False, unique=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='images')
    image = models.CharField(max_length=2750)
