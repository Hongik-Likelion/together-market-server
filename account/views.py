from pprint import pprint

from rest_framework import status
from rest_framework.authentication import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from account.serializers import RegisterSerializer


User = get_user_model()


# Create your views here.
"""회원가입 뷰  
Returns:
    201: 회원가입 성공 시 회원가입한 유저 정보와 jwt 토큰 발금
    400: 회원가입에 필요한 정보가 충족되지 않았을 시 
"""


@api_view(["POST"])
def sign_up_view(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        # 회원 저장
        user = serializer.save()

        # jwt token 발급
        token = TokenObtainPairSerializer.get_token(user)
        refresh_token = str(token)
        access_token = str(token.access_token)

        res = Response(
            {
                "user": serializer.data,
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
            status=status.HTTP_201_CREATED,
        )

        return res

    return Response(status=status.HTTP_400_BAD_REQUEST)


"""로그인 뷰  
Returns:
    200: 로그인 성공 시 jwt 토큰 발급
    400: email 전달 받지 못함
    404: 기존 회원이 아닌경우
"""


@api_view(["POST"])
def login_view(request):
    email = request.data.get("email")
    if email is None:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
        token = TokenObtainPairSerializer.get_token(user)
        refresh_token = str(token)
        access_token = str(token.access_token)
        res = Response(
            {
                "message": "login success",
                "token": {
                    "access": access_token,
                    "refresh": refresh_token,
                },
            },
            status=status.HTTP_200_OK,
        )
        return res
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


"""개인정보 조회 뷰  
Returns:
    200: 개인 정보 조회 성공 시 정보 반환, 손님일 경우 선호하는 시장도 포함
    401: access_token이 valid 하지 않은 경우
"""


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_info_view(request):
    user = request.user

    # 마켓 조회는 아직
    # if not user.is_owner:
    #     result = Market.objects.filter(favourite_markets__in=[user.id])
    #     print(result)

    res = Response(
        data={
            "email": user.email,
            "nickname": user.nickname,
            "profile": user.profile,
            "introduction": user.introduction,
            "is_owner": user.is_owner,
        },
        status=status.HTTP_200_OK,
    )

    return res
