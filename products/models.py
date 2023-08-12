from django.db import models


# Create your models here.
class Product(models.Model):
    product_id = models.BigAutoField(primary_key=True, null=False, unique=True)
    product_type = models.CharField(max_length=10)
