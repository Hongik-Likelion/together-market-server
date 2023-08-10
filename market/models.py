from django.db import models

# Create your models here.
class Market(models.Model):
    market_id = models.BigAutoField(primary_key=True, null=False, unique=True)
    market_name = models.CharField(max_length=30)
    street_address = models.CharField(max_length=50)
    postal_address = models.CharField(max_length=50)
    has_toilet = models.BooleanField()
    has_parking = models.BooleanField()
