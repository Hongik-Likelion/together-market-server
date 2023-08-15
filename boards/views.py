from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from boards.serializers import BoardSerializer
from rest_framework.response import Response
from rest_framework import status


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def post_board_view(request):
    data = request.data.copy()
    data["user"] = request.user.id

    serializer = BoardSerializer(data=data)

    if serializer.is_valid():
        board = serializer.save()
        return Response(data=BoardSerializer(board).data, status=status.HTTP_201_CREATED)

    return Response(status=status.HTTP_400_BAD_REQUEST)

