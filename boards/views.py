from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404
from boards.models import BoardPhoto
from boards.serializers import BoardOwnerSerializer, BoardCustomerSerializer
from rest_framework.response import Response
from rest_framework import status

from market.models import Market
from shop.models import Shop


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def post_board_view(request):
    user = request.user
    data = request.data.copy()
    data["user_id"] = user.id
    photo_data = data.pop("photo")

    get_object_or_404(Market, pk=request.data.get("market_id"))
    get_object_or_404(Shop, pk=request.data.get("shop_id"))

    if user.is_owner:
        serializer = BoardOwnerSerializer(data=data)
    else:
        serializer = BoardCustomerSerializer(data=data)
    if serializer.is_valid():
        board = serializer.save()
        for image in photo_data:
            BoardPhoto.objects.create(board_id=board.board_id, image=image)
            response_data = serializer.data.copy()
        response_data["photo"] = photo_data
        return Response(data=response_data, status=status.HTTP_201_CREATED)
    else:
        return Response(data={"message": "요청 형식이 잘못됨"}, status=status.HTTP_400_BAD_REQUEST)


