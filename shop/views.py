from rest_framework import status
from rest_framework.authentication import get_user_model
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes

from boards.models import Board
from market.models import Market
from shop.models import Shop

from shop.serializers import (
    ShopCreateSerializer,
    ShopDetailInfoSerializer,
    ShopListInfoSerializer,
)

User = get_user_model()


# Create your views here.
class ShopView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 상점 등록
        serializer = ShopCreateSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            shop = serializer.save(user=request.user)
            return Response(
                data={
                    "market_id": shop.market_id,
                    "shop_name": shop.shop_name,
                    "shop_address": shop.shop_address,
                    "selling_products": shop.selling_products,
                    "opening_time": shop.opening_time,
                    "closing_time": shop.closing_time,
                    "opening_frequency": shop.opening_frequency,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        market_id = request.query_params.get("market_id", None)
        if market_id != None:
            # 리스트 조회
            result = Shop.objects.filter(market_id=market_id)

            serializer = ShopListInfoSerializer(result, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            # 나의 관심 가게
            shop_ids = request.user.user_shop_favourites.all().values_list(
                "shop_id", flat=True
            )

            print(f"shop_ids={shop_ids}")
            res_data = []
            for shop_id in shop_ids:
                shop = get_object_or_404(Shop, pk=shop_id)
                serializer = ShopDetailInfoSerializer(instance=shop)
                market_id = serializer.data["market"]
                market = get_object_or_404(Market, market_id=market_id)

                data = {
                    "market_name": market.market_name,
                    "shop_name": serializer.data["shop_name"],
                    "shop_address": serializer.data["shop_address"],
                    "opening_time": serializer.data["opening_time"],
                    "closing_time": serializer.data["closing_time"],
                    "average_rating": serializer.data["rating"],
                    "is_liked": True,
                }
                res_data.append(data)
            return Response(data=res_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def fetch_shop_detail_view(request, shop_id):
    if shop_id == None:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # 상점 상세 조회
    shop = get_object_or_404(Shop, shop_id=shop_id)
    serializer = ShopDetailInfoSerializer(shop)

    return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def add_shop_favourites_view(request, shop_id):
    # 가게 즐겨찾기 등록
    shop = get_object_or_404(Shop, shop_id=shop_id)

    try:
        shop.favourites.get(id=request.user.id)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    except User.DoesNotExist:
        shop.favourites.add(request.user)
        return Response(status=status.HTTP_201_CREATED)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def remove_shop_favourites_view(request, shop_id):
    # 가게 즐겨찾기 해제
    shop = get_object_or_404(Shop, shop_id=shop_id)

    try:
        shop.favourites.get(id=request.user.id)
        shop.favourites.remove(request.user)
        return Response(status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
