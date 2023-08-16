from django.db import models

from account.models import User
from market.models import Market
from products.models import Product
from shop.models import Shop


# Create your models here.
class Board(models.Model):
    board_id = models.BigAutoField(primary_key=True, null=False, unique=True)
    market_id = models.ForeignKey(Market, on_delete=models.CASCADE)
    shop_id = models.ForeignKey(Shop, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    market_name = models.CharField(max_length=30)
    shop_name = models.CharField(max_length=20)
    content = models.CharField(max_length=500)
    rating = models.IntegerField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    purchased_products = models.ManyToManyField(Product, related_name="board_purchased_products")
    likes = models.ManyToManyField(User, related_name="liked_boards", blank=True)
    reports = models.ManyToManyField(User, related_name="reported_boards", blank=True)

    def get_report_count(self):
        return self.reports.all().count()

    def get_like_count(self):
        return self.likes.all().count()


class BoardPhoto(models.Model):
    image_id = models.BigAutoField(primary_key=True, null=False, unique=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='photo')
    image = models.CharField(max_length=2750)

    def __str__(self) -> str:
        return f"{self.image}"
