from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404

from account.models import User
from boards.models import BoardPhoto, Board
from boards.serializers import BoardOwnerSerializer, BoardCustomerSerializer, SingleBoardOwnerSerializer, \
    SingleBoardCustomerSerializer, BoardReadSerializer, UserReadSerializer, ShopReadSerializer, MixValidSerializer, \
    BoardReadListSerializer, MixValidListSerializer
from rest_framework.response import Response
from rest_framework import status

from market.models import Market
from shop.models import Shop


@api_view(["POST", "GET"])
@permission_classes([IsAuthenticated])
def post_board_view(request):
    if request.method == "POST":
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

    if request.method == "GET":
        market_id = request.GET.get("market_id")
        boards = Board.objects.filter(market_id=market_id)
        data = []
        for board in boards:
            # 게시글 상세 보기
            board = get_object_or_404(Board, pk=board.board_id)
            user = get_object_or_404(User, pk=request.user.id)
            shop = get_object_or_404(Shop, pk=board.shop_id.shop_id)

            board_serializer = BoardReadListSerializer(instance=board)
            user_serializer = UserReadSerializer(instance=user)
            shop_serializer = ShopReadSerializer(instance=shop)

            res_data = {
                "user_info": user_serializer.data,
                "shop_info": shop_serializer.data,
                "board_info": board_serializer.data
            }
            res_data["board_info"]["updated_at"] = board.updated_at
            mixSerializer = MixValidListSerializer(data=res_data)
            likes = board.likes.all().count()  # 좋아요 수
            if user.liked_boards.filter(board_id=board.board_id).exists():  # 유저가 좋아요 했는지 확인
                is_liked = True
            else:
                is_liked = False

            res_data["board_info"]["likes"] = likes
            res_data["board_info"]["is_liked"] = is_liked
            res_data["board_info"]["photo"] = board.photo.first().image

            if mixSerializer.is_valid():
                data.append(res_data)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(data=data, status=status.HTTP_200_OK)


@api_view(["PUT", "DELETE", "GET"])
@permission_classes([IsAuthenticated])
def single_board_view(request, board_id):
    if request.method == "PUT":
        # 게시글 수정
        data = request.data.copy()
        data["board_id"] = board_id
        photo_data = data.pop("photo")
        board = get_object_or_404(Board, pk=board_id)  # board 객체 찾기, 없으면 404

        if request.user.is_owner:  # user 유형에 따라 분기
            serializer = SingleBoardOwnerSerializer(board, data=data)
        else:
            serializer = SingleBoardCustomerSerializer(board, data=data)

        photos = BoardPhoto.objects.filter(board_id=board_id)  # 게시글 사진들

        if serializer.is_valid():  # serializer 이용해 valid
            serializer.save()
            for photo, image in zip(photos, photo_data):  # 원래 있던 사진 교체
                photo.image = image
                photo.save()
                photo_data.remove(image)

            for image in photo_data:  # 원래 있었던 사진 수 보다 더 추가 할 때
                BoardPhoto.objects.create(board_id=board.board_id, image=image)

            new_photos = BoardPhoto.objects.filter(board_id=board_id)  # 응답에 photo 추가
            photo_string = [photo.image for photo in new_photos]
            response_data = serializer.data.copy()
            response_data['photo'] = photo_string

            return Response(data=response_data, status=status.HTTP_200_OK)
        else:  # serializer 로 넘어온 데이터 이상할 때
            return Response(data={"message": "요청 형식이 잘못됨"}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        # 게시글 삭제
        board = get_object_or_404(Board, pk=board_id)  # board 객체 찾기, 없으면 404
        board.delete()
        return Response(data={"message": "삭제 완료"}, status=status.HTTP_200_OK)

    if request.method == "GET":
        # 게시글 상세 보기
        board = get_object_or_404(Board, pk=board_id)
        user = get_object_or_404(User, pk=request.user.id)
        shop = get_object_or_404(Shop, pk=board.shop_id.shop_id)

        board_serializer = BoardReadSerializer(instance=board)
        user_serializer = UserReadSerializer(instance=user)
        shop_serializer = ShopReadSerializer(instance=shop)  # 좋아요 추가 필요

        res_data = {
            "user_info": user_serializer.data,
            "shop_info": shop_serializer.data,
            "board_info": board_serializer.data
        }
        res_data["board_info"]["updated_at"] = board.updated_at
        mixSerializer = MixValidSerializer(data=res_data)
        likes = board.likes.all().count()
        if user in board.likes.all():
            is_liked = True
        else:
            is_liked = False

        res_data["board_info"]["likes"] = likes
        res_data["board_info"]["is_liked"] = is_liked

        if mixSerializer.is_valid(raise_exception=True):
            return Response(data=res_data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def board_like_view(request, board_id):
    board = get_object_or_404(Board, pk=board_id)
    user = request.user
    board.likes.add(user)

    return Response(data={"message": "좋아요 추가 성공"}, status=status.HTTP_200_OK)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def board_unlike_view(request, board_id):
    board = get_object_or_404(Board, pk=board_id)
    user = request.user
    board.likes.remove(user)

    return Response(data={"message": "좋아요 취소 성공"}, status=status.HTTP_200_OK)
