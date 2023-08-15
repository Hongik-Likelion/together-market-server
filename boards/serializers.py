from rest_framework import serializers

from boards.models import Board, BoardPhoto


class ImageSerializer(serializers.Serializer):
    photo = serializers.CharField(max_length=2750)


class BoardSerializer(serializers.ModelSerializer):
    photo = ImageSerializer(many=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Board
        fields = ("market", "market_name", "shop", "shop_name", "purchased_products", "content", "rating", "user", "photo")

    def create(self, validated_data):
        user = self.context['request'].user
