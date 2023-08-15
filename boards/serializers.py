from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from account.models import User
from boards.models import Board, BoardPhoto
from market.models import Market
from products.models import Product
from shop.models import Shop


class BoardSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    market_id = serializers.PrimaryKeyRelatedField(queryset=Market.objects.all())
    shop_id = serializers.PrimaryKeyRelatedField(queryset=Shop.objects.all())
    photo = serializers.ListSerializer(child=serializers.CharField(max_length=2750, allow_blank=True))

    class Meta:
        model = Board
        fields = ("user_id", "market_id", "market_name", "shop_id", "shop_name", "purchased_products", "content")

    def create(self, validated_data):
        purchased_products_data = validated_data.pop('purchased_products', [])

        board = Board.objects.create(**validated_data)

        for product_id in purchased_products_data:
            board.purchased_products.add(product_id)

        return board


class BoardCustomerSerializer(BoardSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)
    class Meta(BoardSerializer.Meta):
        fields = BoardSerializer.Meta.fields + ("rating",)


class BoardOwnerSerializer(BoardSerializer):
    class Meta(BoardSerializer.Meta):
        pass
