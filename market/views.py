from rest_framework import status
from rest_framework.authentication import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from market.models import Market

User = get_user_model()


@api_view(["GET"])
def get_market_list_view(request):
    data = []
    markets = Market.objects.all()
    for market in markets:
        data.append(
            {
                "market_id": market.market_id,
                "market_name": market.market_name,
            }
        )

    return Response(data=data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def post_favourite_market(request):
    user = request.user
    market_ids = request.data.getlist("market_id")

    for market_id in market_ids:
        market = get_object_or_404(Market, pk=market_id)

        if user in market.favourite_markets.all():
            return Response(
                data={"message": "이미 등록된 시장"}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            market.favourite_markets.add(request.user)

    return Response(
        data={
            "message": "등록 성공",
        },
        status=status.HTTP_201_CREATED,
    )
