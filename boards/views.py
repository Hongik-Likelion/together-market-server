from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404

from account.models import User
from boards.models import BoardPhoto, Board
from boards.serializers import SingleBoardOwnerSerializer, \
    SingleBoardCustomerSerializer, BoardReadSerializer, UserReadSerializer, ShopReadSerializer, MixValidSerializer, \
    BoardReadListSerializer, MixValidListSerializer, MyShopSerializer, MyBoardSerializer, MyMixedSerializer, \
    ReviewBoardSerializer, ReviewUserSerializer, ReviewSerializer, BoardCreateSerializer
from rest_framework.response import Response
from rest_framework import status

from market.models import Market
from shop.models import Shop


@api_view(["POST", "GET"])
@permission_classes([IsAuthenticated])
def post_board_view(request):
    if request.method == "POST":  # 게시글 생성
        user = request.user
        data = request.data.copy()
        data["user_id"] = user.id

        try:  # 사진 있으면 따로 데이터 빼줌
            photo_data = data.pop("photo")
        except:
            photo_data = None

        get_object_or_404(Market, pk=request.data.get("market_id"))
        shop = get_object_or_404(Shop, pk=request.data.get("shop_id"))

        serializer = BoardCreateSerializer(data=data)

        if serializer.is_valid():
            board = serializer.save()
            response_data = serializer.data.copy()

            shop_boards = Board.objects.filter(shop_id=shop.shop_id)  # rating 반영해서 shop 의 avg_rating 설정
            if board.rating is not None:  #
                avg_rating = 0
                total_count = 0
                for shop_board in shop_boards:
                    if shop_board.user_id.is_owner is False:
                        avg_rating += shop_board.rating
                        total_count += 1
                avg_rating = avg_rating/total_count
                shop.rating = avg_rating
                shop.save()

            if photo_data is not None:  # 사진 있으면 따로 연결된 객체 생성
                for image in photo_data:
                    BoardPhoto.objects.create(board_id=board.board_id, image=image)
                response_data["photo"] = photo_data
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(data={"message": "요청 형식이 잘못됨"}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "GET":
        market_id = request.GET.get("market_id")
        if market_id is not None:  # 시장에 대한 게시글 전체 조회
            boards = Board.objects.filter(market_id=market_id)
            data = []
            for board in boards:

                if board.get_report_count() > 4:  # 신고 누적 조회
                    continue

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

                mixSerializer = MixValidListSerializer(data=res_data)
                likes = board.get_like_count()  # 좋아요 수
                if user.liked_boards.filter(board_id=board.board_id).exists():  # 유저가 좋아요 했는지 확인
                    is_liked = True
                else:
                    is_liked = False

                res_data["board_info"]["likes"] = likes
                res_data["board_info"]["is_liked"] = is_liked

                res_data["board_info"]["updated_at"] = board.updated_at.strftime("%Y.%m.%d")

                if board.photo.first() is not None:
                    res_data["board_info"]["photo"] = str(board.photo.first())

                if mixSerializer.is_valid():
                    data.append(res_data)
                    print("등록 성공")
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "validation 실패"})

            return Response(data=data, status=status.HTTP_200_OK)

        else:  # 나의 게시글 조회
            user = request.user
            boards = Board.objects.filter(user_id=user.id)
            my_data = []

            for board in boards:
                shop = get_object_or_404(Shop, pk=board.shop_id.shop_id)
                shop_serializer = MyShopSerializer(instance=shop)
                board_serializer = MyBoardSerializer(instance=board)

                res_data = {
                    "shop_info": shop_serializer.data,
                    "board_info": board_serializer.data,
                }
                res_data["board_info"]["updated_at"] = board.updated_at.strftime("%Y.%m.%d")

                if board.photo.first() is not None:  # 만약 게시글에 등록한 사진이 있으면 첫번째만 추가
                    res_data["board_info"]["photo"] = board.photo.first().image

                if MyMixedSerializer(data=res_data).is_valid(raise_exception=True):
                    my_data.append(res_data)
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)

            return Response(data=my_data, status=status.HTTP_200_OK)




@api_view(["PUT", "DELETE", "GET"])
@permission_classes([IsAuthenticated])
def single_board_view(request, board_id):
    if request.method == "PUT":
        # 게시글 수정
        data = request.data.copy()
        data["board_id"] = board_id
        try:
            photo_data = data.pop("photo")
        except:
            photo_data = None

        board = get_object_or_404(Board, pk=board_id)  # board 객체 찾기, 없으면 404

        if request.user.is_owner:  # user 유형에 따라 분기
            serializer = SingleBoardOwnerSerializer(board, data=data)
        else:
            serializer = SingleBoardCustomerSerializer(board, data=data)

        photos = board.photo.all()  # 게시글 사진들

        if serializer.is_valid():  # serializer 이용해 valid
            serializer.save()
            if photo_data is not None:  # 교체하려는 사진이 있는 경우
                for photo in photos:  # 원래 있던 사진 교체
                    try:
                        photo.image = photo_data.pop(0)
                        photo.save()
                    except:  # 원래 있던 사진이 더 많으면 삭제
                        photo.delete()

                if photo_data is not None:  # 교체 사진이 더 많은 경우
                    for image in photo_data:  # 원래 있었던 사진 수 보다 더 추가 할 때
                        BoardPhoto.objects.create(board_id=board.board_id, image=image)
                else:  # 갯수 딱 맞음
                    pass

                new_photos = BoardPhoto.objects.filter(board_id=board_id)  # 응답에 photo 추가
                photo_string = [photo.image for photo in new_photos]
                response_data = serializer.data.copy()
                response_data['photo'] = photo_string
            else:  # 사진을 아예 안 넣었을 때
                photos.all().delete()
                response_data = serializer.data.copy()

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

        if board.get_report_count() > 4:  # 신고 누적 조회
            return Response(data={"message: 신고 누적된 게시물"}, status=status.HTTP_400_BAD_REQUEST)


        board_serializer = BoardReadSerializer(instance=board)
        user_serializer = UserReadSerializer(instance=user)
        shop_serializer = ShopReadSerializer(instance=shop)  # 좋아요 추가 필요

        res_data = {
            "user_info": user_serializer.data,
            "shop_info": shop_serializer.data,
            "board_info": board_serializer.data
        }

        mixSerializer = MixValidSerializer(data=res_data)
        likes = board.get_like_count()
        if user in board.likes.all():
            is_liked = True
        else:
            is_liked = False

        res_data["board_info"]["updated_at"] = board.updated_at.strftime("%Y.%m.%d")
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


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def board_report_view(request, board_id):
    board = get_object_or_404(Board, pk=board_id)
    board.reports.add(request.user)

    return Response(data={"message": "신고 성공"}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def board_review_view(request):
    shop = get_object_or_404(Shop, user_id=request.user.id)
    boards = Board.objects.filter(shop_id=shop.shop_id)

    review_data = []
    for board in boards:
        user = get_object_or_404(User, pk=board.user_id.id)
        if user == request.user:
            continue

        like_count = board.get_like_count()

        if request.user in board.likes.all():
            is_liked = True
        else:
            is_liked = False

        board_serializer = ReviewBoardSerializer(instance=board)
        user_serializer = ReviewUserSerializer(instance=user)
        data = {
            'user_info': user_serializer.data,
            'board_info': board_serializer.data
        }
        data["board_info"]["updated_at"] = board.updated_at.strftime("%Y.%m.%d")
        data["board_info"]["like_count"] = like_count
        data["board_info"]["is_liked"] = is_liked
        if BoardPhoto.objects.filter(board_id=board.board_id).first() is not None:
            data["board_info"]["photo"] = str(BoardPhoto.objects.filter(board_id=board.board_id).first())

        review_serializer = ReviewSerializer(data=data)

        if review_serializer.is_valid():
            review_data.append(data)
        else:
            print(review_serializer.errors)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    return Response(data=review_data, status=status.HTTP_200_OK)

