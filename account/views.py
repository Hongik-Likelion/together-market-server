from pprint import pprint

from rest_framework import status
from rest_framework.authentication import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.generics import get_object_or_404

from account.serializers import BlackListSerializer, LoginSerializer, RegisterSerializer, CustomerUpdateSerializer
from market.models import Market
from shop.serializers import ShopModifySerializer

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
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid(raise_exception=True):
        user = serializer.validated_data

        token = TokenObtainPairSerializer.get_token(user)
        refresh_token = str(token)
        access_token = str(token.access_token)
        res = Response(
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
            status=status.HTTP_200_OK,
        )
        return res


"""개인정보 조회 뷰  
Returns:
    200: 개인 정보 조회 성공 시 정보 반환, 손님일 경우 선호하는 시장도 포함
    401: access_token이 valid 하지 않은 경우
"""


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_info_view(request):
    user = request.user

    if not user.is_owner:
        favourite_markets = user.user_favorite_markets.all()
        market = []
        for favourite_market in favourite_markets:
            market_data = {
                "market_id": favourite_market.market_id,
                "market_name": favourite_market.market_name
            }
            market.append(market_data)

    res = Response(
        data={
            "user_id": user.id,
            "email": user.email,
            "nickname": user.nickname,
            "profile": user.profile,
            "introduction": user.introduction,
            "is_owner": user.is_owner,
            "favourite_market": market
        },
        status=status.HTTP_200_OK,
    )

    return res


"""사용자 차단 뷰
Returns:
    200: 차단 성공, 차단한 유저 정보 return
    401: access_token이 valid 하지 않은 경우
    404: 차단할 유저를 발견하지 못함
"""


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def user_block_view(request, user_id):
    # 차단하려는 유저자 존재하는지 검색
    serializer = BlackListSerializer(data={"blocked_user_id": user_id})

    if serializer.is_valid(raise_exception=True):
        user = serializer.save(user=request.user)
        return Response(
            data={
                "id": user.id,
                "email": user.email,
                "nickname": user.nickname,
                "profile": user.profile,
                "introduction": user.introduction,
                "is_owner": user.is_owner,
            },
            status=status.HTTP_200_OK,
        )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def user_modify_view(request):
    user = request.user
    if user.is_owner:
        change_data = request.data.copy()
        shop = user.my_shop
        introduction = change_data.pop("introduction")
        shop_serializer = ShopModifySerializer(instance=shop, data=change_data)
        if shop_serializer.is_valid():
            shop_serializer.save()
            user.introduction = introduction
            user.save()
            return Response(
                data={
                    "email": user.email,
                    "nickname": user.nickname,
                    "profile": user.profile,
                    "introduction": user.introduction,
                    "is_owner": user.is_owner
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    else:
        serializer = CustomerUpdateSerializer(instance=user, data=request.data)
        change_data = request.data.copy()
        favourite_markets = change_data.pop("favourite_markets")

        market_id = favourite_markets[0]
        market = get_object_or_404(Market, pk=market_id)
        user.user_favorite_markets.clear()
        user.user_favorite_markets.add(market)

        if serializer.is_valid():
            serializer.save()
            return Response(
                data={
                    "email": user.email,
                    "nickname": user.nickname,
                    "profile": user.profile,
                    "introduction": user.introduction,
                    "is_owner": user.is_owner
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


