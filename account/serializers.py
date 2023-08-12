from rest_framework import serializers
from rest_framework.authentication import get_user_model
from rest_framework.exceptions import ValidationError

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "nickname", "profile", "is_owner")

    def create(self, validated_data):
        email = validated_data.get("email")
        nickname = validated_data.get("nickname")
        profile = validated_data.get("profile")
        is_owner = validated_data.get("is_owner")

        user = User(email=email, nickname=nickname, profile=profile, is_owner=is_owner)
        user.save()
        return user
