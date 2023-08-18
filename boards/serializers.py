from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from account.models import User
from boards.models import Board, BoardPhoto
from market.models import Market
from products.models import Product
from shop.models import Shop


class SingleCreateBoardSerializer(serializers.ModelSerializer):  # 게시글 단일 수정 위한 serializer
    photo = serializers.ListSerializer(child=serializers.CharField(max_length=2750, allow_blank=True))

    class Meta:
        model = Board
        fields = ("market_name", "shop_name", "purchased_products", "content")

    def update(self, instance, validated_data):
        purchased_products_data = validated_data.pop('purchased_products', [])

        instance.purchased_products.clear()
        for product_id in purchased_products_data:
            instance.purchased_products.add(product_id)

        instance.market_name = validated_data.get("market_name", instance.market_name)
        instance.shop_name = validated_data.get("shop_name", instance.shop_name)
        instance.content = validated_data.get("content", instance.content)
        instance.save()

        return instance


class SingleBoardCustomerSerializer(SingleCreateBoardSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)

    class Meta(SingleCreateBoardSerializer.Meta):
        fields = SingleCreateBoardSerializer.Meta.fields + ("rating",)

    def update(self, instance, validated_data):
        rating = validated_data.pop('rating', None)
        instance = super().update(instance, validated_data)

        # Update the rating if it's provided
        if rating is not None:
            instance.rating = rating
            instance.save()

        return instance


class SingleBoardOwnerSerializer(SingleCreateBoardSerializer):
    class Meta(SingleCreateBoardSerializer.Meta):
        pass


class BoardCreateSerializer(serializers.ModelSerializer):  # 게시글 생성 위한 serializer
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


class BoardCustomerSerializer(BoardCreateSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)
    class Meta(BoardCreateSerializer.Meta):
        fields = BoardCreateSerializer.Meta.fields + ("rating",)


class BoardOwnerSerializer(BoardCreateSerializer):
    class Meta(BoardCreateSerializer.Meta):
        pass


class UserReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = User
        fields = ("id", "is_owner", "nickname", "profile")


class PhotoSerializer(serializers.ModelSerializer):

    class Meta:
        model = BoardPhoto
        fields = ("image",)



class BoardReadSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=5, required=False)
    photo = PhotoSerializer(many=True, required=False)
    updated_at = serializers.CharField(max_length=15, read_only=True)
    class Meta:
        model = Board
        fields = ("rating", "photo", "content", "updated_at")


class BoardReadListSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=5, required=False)
    updated_at = serializers.CharField(max_length=15, read_only=True)

    class Meta:
        model = Board
        fields = ("rating", "content", "updated_at")


class ShopReadSerializer(serializers.ModelSerializer):
    shop_id = serializers.IntegerField()
    class Meta:
        model = Shop
        fields = ("shop_id", "shop_name", "rating")


class MixValidSerializer(serializers.Serializer):
    board_info = BoardReadSerializer()
    shop_info = ShopReadSerializer()
    user_info = UserReadSerializer()


class MixValidListSerializer(serializers.Serializer):
    board_info = BoardReadListSerializer()
    shop_info = ShopReadSerializer()
    user_info = UserReadSerializer()


class MyShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ("shop_name",)


class MyBoardSerializer(serializers.ModelSerializer):
    board_id = serializers.IntegerField()
    updated_at = serializers.CharField(max_length=15, read_only=True)
    rating = serializers.IntegerField(min_value=1, max_value=5, required=False)
    class Meta:
        model = Board
        fields = ("board_id", "updated_at", "content", "rating")


class MyMixedSerializer(serializers.Serializer):
    shop_info = MyShopSerializer()
    board_info = MyBoardSerializer()


class ReviewUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("nickname",)


class ReviewBoardSerializer(serializers.ModelSerializer):
    board_id = serializers.IntegerField()
    updated_at = serializers.CharField(max_length=15, read_only=True)
    rating = serializers.IntegerField(min_value=1, max_value=5)
    class Meta:
        model = Board
        fields = ("board_id", "updated_at", "rating", "content")


class ReviewSerializer(serializers.Serializer):
    user_info = ReviewUserSerializer()
    board_info = ReviewBoardSerializer()
