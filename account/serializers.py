from rest_framework import serializers
from rest_framework.authentication import get_user_model
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404
from account.models import BlackList

User = get_user_model()


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


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


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)

    """email에 해당하는 회원이 존재하는지 검증
        Returns: 
            회원이 존재한다면 해당 user Model return
            없다면 404 Not Found error raise
    """

    def validate(self, data):
        try:
            email = data.get("email")
            user = User.objects.get(email=email)
            return user
        except User.DoesNotExist:
            raise NotFound


class BlackListSerializer(serializers.ModelSerializer):
    user = UserInfoSerializer(read_only=True)

    class Meta:
        model = BlackList
        fields = (
            "user",
            "blocked_user_id",
        )

    """user_id에 해당하는 회원이 존재하는지 검증
        Returns: 
            회원이 존재한다면 해당 user_id return
            없다면 404 Not Found error raise
    """

    def validate(self, data):
        try:
            User.objects.get(id=data["blocked_user_id"])
            return data
        except User.DoesNotExist:
            raise NotFound

    """블랙리스트 생성
        @params blocked_user_id: 차단하고자 하는 유저의 아이디
        
        Returns: 
            차단한 유저의 정보    
    """

    def create(self, validated_data):
        user = validated_data.get("user")
        blocked_user_id = validated_data.get("blocked_user_id")

        BlackList(user_id=user.id, blocked_user_id=blocked_user_id).save()
        blocked_user = get_object_or_404(User, id=blocked_user_id)
        return blocked_user
