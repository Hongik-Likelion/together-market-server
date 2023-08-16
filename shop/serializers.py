from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404

from market.models import Market
from products.models import Product
from shop.models import Shop


class ShopCreateSerializer(serializers.ModelSerializer):
    market_id = serializers.IntegerField()
    product_categories = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = Shop
        fields = (
            "market_id",
            "shop_name",
            "shop_address",
            "selling_products",
            "opening_time",
            "closing_time",
            "opening_frequency",
            "product_categories",
        )

    def validate(self, data):
        market_id = data["market_id"]
        try:
            Market.objects.get(market_id=market_id)
            return data

        except Market.DoesNotExist:
            raise NotFound

    def create(self, validated_data):
        user = validated_data.get("user")
        market_id = validated_data.get("market_id")
        shop_name = validated_data.get("shop_name")
        shop_address = validated_data.get("shop_address")
        selling_products = validated_data.get("selling_products")
        opening_time = validated_data.get("opening_time")
        closing_time = validated_data.get("closing_time")
        opening_frequency = validated_data.get("opening_frequency")
        product_categories = validated_data.get("product_categories")

        market = Market.objects.get(market_id=market_id)
        shop = Shop(
            user=user,
            market=market,
            shop_name=shop_name,
            shop_address=shop_address,
            selling_products=selling_products,
            opening_time=opening_time,
            closing_time=closing_time,
            opening_frequency=opening_frequency,
        )
        shop.save()

        for product_id in product_categories:
            product = get_object_or_404(Product, product_id=product_id)
            shop.product.add(product)

        return shop


class ShopListInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ("shop_id", "shop_name")


class ShopDetailInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = "__all__"


class ShopModifySerializer(serializers.ModelSerializer):

    class Meta:
        model = Shop
        fields = ("shop_name", "opening_time", "closing_time")

    def update(self, instance, validated_data):
        instance.shop_name = validated_data.get("shop_name")
        instance.opening_time = validated_data.get("opening_time")
        instance.closing_time = validated_data.get("closing_time")
        instance.save()

        return instance
