from rest_framework.authentication import get_user_model
from rest_framework.generics import get_object_or_404
from rest_framework.test import APIClient, APITestCase

from account.models import User
from boards.models import BoardPhoto, Board
from boards.serializers import BoardCreateSerializer, BoardCustomerSerializer
from market.models import Market
from products.models import Product
from shop.models import Shop


class TestBoard(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.board_request = {
            "market_id": 1,
            "shop_id": 1,
            "market_name": "강남시장",
            "shop_name": "바삭마차",
            "purchased_products": [1, 2],
            "photo": ["이미지", "이미지2"],
            "content": "맛있어요",
            "rating": 4
        }
        cls.second_board_no_photo = {
            "market_id": 1,
            "shop_id": 1,
            "market_name": "강남시장",
            "shop_name": "바삭마차",
            "purchased_products": [3, 2],
            "content": "별로에요",
            "rating": 2
        }
        cls.invalid_request = {
            "market_id": 1,
            "shop_id": 3,
            "market_name": "강남시장",
            "shop_name": "바삭마차",
            "purchased_products": [1, 2],
            "photo": ["이미지", "이미지2"],
            "content": "맛있어요",
            "rating": 4
        }
        cls.update_request = {
            "market_name": "강남시장",
            "shop_name": "바삭마차",
            "purchased_products": [1, 2, 3],
            "photo": ["이미지 6", "이미지 5", "이미지 4"],
            "content": "맛있어요",
            "rating": 3
        }
        cls.market = Market.objects.create(
            market_id=1,
            market_name="강남시장",
            street_address="서울특별시 강남구 압구정로 2길 46",
            postal_address="서울특별시 강남구 신사동 510-11",
            has_toilet=True,
            has_parking=True
        )
        print("MARKET initial")
        cls.user = User.objects.create(
            id=1,
            email="test@example.com",
            is_owner=False,
            nickname="손님 1",
            profile="https://cdn.pixabay.com/photo/2015/03/10/17/23/youtube-667451_1280.png",
            introduction="testUser1"
        )
        print("USER initial")
        cls.owner = User.objects.create(
            id=2,
            email="owner@example.com",
            is_owner=True,
            nickname="사장 1",
            profile="https://cdn.pixabay.com/photo/2015/03/10/17/23/youtube-667451_1280.png",
            introduction="testOwner"
        )
        print("Owner initial")
        cls.shop = Shop.objects.create(
            shop_id=1,
            market_id=cls.market.market_id,
            user_id=cls.owner.id,
            shop_name="바삭마차",
            shop_address="마포구 서교동 120-3",
            selling_products="돈까스, 제육",
            opening_time="13:00",
            closing_time="21:00",
            opening_frequency="weekly",
            rating=3.4
        )
        print("SHOP initial")
        Product(product_id=1, product_type="먹거리").save()
        Product(product_id=2, product_type="해산물").save()
        Product(product_id=3, product_type="채소/과일").save()
        Product(product_id=4, product_type="기타").save()

    def setUp(self):
        self.client = APIClient()

    def test_serializer_validation(self):
        data = self.board_request.copy()
        data["user_id"] = 1
        serializer = BoardCustomerSerializer(data=data)
        data.pop("photo", [])
        self.assertEqual(True, serializer.is_valid())

    def test_serializer_save(self):
        data = self.board_request
        data["user_id"] = 1
        photo_data = data.pop("photo", [])
        serializer = BoardCustomerSerializer(data=data)

        if serializer.is_valid(raise_exception=True):
            board = serializer.save()
            for image in photo_data:
                BoardPhoto.objects.create(board_id=board.board_id, image=image)
            self.assertEqual(board.rating, self.board_request.get("rating"))
            self.assertEqual(2, len(board.photo.all()))

    def test_post(self):
        # given
        url_login = "/user/login/"
        url_post = "/board/"
        request_login = {"email": "test@example.com"}

        response_login = self.client.post(url_login, request_login)
        access_token = response_login.data.get("access_token")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)

        response_post = self.client.post(url_post, self.board_request)
        response_post_invalid = self.client.post(url_post, self.invalid_request)
        response_post_no_photo = self.client.post(url_post, self.second_board_no_photo)

        self.assertEqual(201, response_post.status_code)
        self.assertEqual(2, len(response_post.data.get("photo")))
        self.assertEqual(404, response_post_invalid.status_code)
        self.assertEqual(201, response_post_no_photo.status_code)
        print(response_post.data)
        print(response_post_no_photo.data)

    def test_update(self):
        # given
        url_login = "/user/login/"
        url_post = "/board/"
        url_update = "/board/1/"

        request_login = {"email": "test@example.com"}

        response_login = self.client.post(url_login, request_login)
        access_token = response_login.data.get("access_token")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)

        response_post = self.client.post(url_post, self.board_request)
        print(response_post.data)
        self.assertEqual(201, response_post.status_code)

        response_update = self.client.put(url_update, self.update_request)
        print(response_update)
        print(response_update.data)
        self.assertEqual(response_update.data.get("rating"), 3)
        self.assertEqual(3, len(response_update.data.get("photo")))
        self.assertEqual(200, response_update.status_code)

    def test_delete(self):
        # given
        url_login = "/user/login/"
        url_post = "/board/"
        url_delete = "/board/1/"
        request_login = {"email": "test@example.com"}

        response_login = self.client.post(url_login, request_login)
        access_token = response_login.data.get("access_token")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)

        response_post = self.client.post(url_post, self.board_request)
        print(response_post.data)
        print(response_post)

        board_to_delete = Board.objects.filter(pk=1).first()
        self.assertIsNotNone(board_to_delete, "삭제할 Board 객체가 존재하지 않습니다.")

        response_delete = self.client.delete(url_delete, data=None)
        print(response_delete)
        self.assertEqual(response_delete.status_code, 200)

        board_after_delete = Board.objects.filter(pk=1).first()
        self.assertIsNone(board_after_delete, "Board 객체가 삭제되지 않았습니다.")

    def test_single_read(self):
        # given
        url_login = "/user/login/"
        url_post = "/board/"
        url_retrieve = "/board/1/"
        request_login = {"email": "test@example.com"}

        response_login = self.client.post(url_login, request_login)
        access_token = response_login.data.get("access_token")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)

        response_post = self.client.post(url_post, self.board_request)
        print('게시글 등록')
        print(response_post)

        response_post_no_photo = self.client.post(url_post, self.second_board_no_photo)
        print('게시글 등록2')
        print(response_post_no_photo)

        response_retrieve = self.client.get(url_retrieve, data=None)
        print(response_retrieve.data)

        response_retrieve_no_photo = self.client.get("/board/2/", data=None)
        print(response_retrieve_no_photo.data)

        self.assertEqual(self.user.id, response_retrieve.data["user_info"]["id"])
        self.assertEqual(self.shop.shop_name, response_retrieve.data.get("shop_info").get("shop_name"))
        self.assertEqual(2, len(response_retrieve.data.get("board_info").get("photo")))
        board = get_object_or_404(Board, pk=1)
        self.assertEqual(str(board.updated_at), response_retrieve.data.get("board_info").get("updated_at"))

        self.assertEqual(self.user.id, response_retrieve_no_photo.data["user_info"]["id"])
        self.assertEqual(self.shop.shop_name, response_retrieve_no_photo.data.get("shop_info").get("shop_name"))
        self.assertEqual(0, len(response_retrieve_no_photo.data.get("board_info").get("photo")))
        board = get_object_or_404(Board, pk=2)
        self.assertEqual(str(board.updated_at), response_retrieve_no_photo.data.get("board_info").get("updated_at"))

    def test_list_read(self):
        # given
        url_login = "/user/login/"
        url_post = "/board/"
        url_list = "/board/?market_id=1"
        request_login = {"email": "test@example.com"}

        response_login = self.client.post(url_login, request_login)
        access_token = response_login.data.get("access_token")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)

        response_post = self.client.post(url_post, self.board_request)
        print('게시글 등록')
        print(response_post)

        response_post_two = self.client.post(url_post, self.second_board_no_photo)
        print('게시글 등록2')
        print(response_post_two)

        response_list = self.client.get(url_list, None)
        print(response_list)
        print(response_list.data)

        self.assertEqual(2, len(response_list.data))
        self.assertNotEquals(response_list.data[0], response_list.data[1])
        self.assertEqual(response_list.status_code, 200)

    def test_like_dislike(self):
        # given
        url_login = "/user/login/"
        url_post = "/board/"
        url_like = "/board/1/like/"
        url_unlike = "/board/1/unlike/"
        url_retrieve = "/board/1/"

        request_login = {"email": "test@example.com"}

        response_login = self.client.post(url_login, request_login)
        access_token = response_login.data.get("access_token")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)

        response_post = self.client.post(url_post, self.board_request)
        print('게시글 등록')
        print(response_post)

        response_retrieve_before = self.client.get(url_retrieve, data=None)
        self.assertEqual(response_retrieve_before.data["board_info"]["likes"], 0)
        self.assertEqual(response_retrieve_before.data["board_info"]["is_liked"], False)

        response_like = self.client.patch(url_like, None)
        print(response_like)
        self.assertEqual(200, response_like.status_code)

        response_retrieve = self.client.get(url_retrieve, data=None)
        self.assertEqual(response_retrieve.data["board_info"]["likes"], 1)
        self.assertEqual(response_retrieve.data["board_info"]["is_liked"], True)


        response_unlike = self.client.patch(url_unlike, None)
        print(response_unlike)
        self.assertEqual(200, response_unlike.status_code)

        response_retrieve_after = self.client.get(url_retrieve, data=None)
        self.assertEqual(response_retrieve_after.data["board_info"]["likes"], 0)
        self.assertEqual(response_retrieve_after.data["board_info"]["is_liked"], False)

    def test_my_list(self):
        # given
        url_login = "/user/login/"
        url_board = "/board/"
        request_login = {"email": "test@example.com"}

        response_login = self.client.post(url_login, request_login)
        access_token = response_login.data.get("access_token")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)

        response_post = self.client.post(url_board, self.board_request)
        print('게시글 등록')
        print(response_post)

        response_post_two = self.client.post(url_board, self.second_board_no_photo)
        print('게시글 등록2')
        print(response_post_two)

        response_my_list = self.client.get(url_board, None)
        print(response_my_list)
        print(response_my_list.data)

        self.assertEqual(2, len(response_my_list.data))
        self.assertEqual(response_my_list.data[0].get("shop_info"), response_my_list.data[1].get("shop_info"))
        self.assertEqual(response_my_list.status_code, 200)

    def test_my_review(self):
        # given
        url_login = "/user/login/"
        url_board = "/board/"
        url_review = "/board/review/"
        customer_login = {"email": "test@example.com"}
        owner_login = {"email": "owner@example.com"}
        # 고객 로그인
        response_customer_login = self.client.post(url_login, customer_login)
        access_token = response_customer_login.data.get("access_token")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)
        # 고객이 가게에 대해 게시글 2개 등록
        response_post = self.client.post(url_board, self.board_request)
        print('게시글 등록')
        print(response_post)

        response_post_two = self.client.post(url_board, self.second_board_no_photo)
        print('게시글 등록2')
        print(response_post_two)
        # 사장으로 로그인
        response_owner_login = self.client.post(url_login, owner_login)
        access_token = response_owner_login.data.get("access_token")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)
        # 사장으로 가게에 대한 리뷰 받기
        response_review = self.client.get(url_review, None)
        print(response_review.data)
        self.assertEqual(response_review.status_code, 200)
        self.assertEqual(2, len(response_review.data))

    def test_report(self):
        # given
        url_login = "/user/login/"
        url_post = "/board/"
        url_list = "/board/?market_id=1"
        url_report = "/board/1/report/"

        request_login = {"email": "test@example.com"}

        response_login = self.client.post(url_login, request_login)
        access_token = response_login.data.get("access_token")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)

        response_post = self.client.post(url_post, self.board_request)
        print('게시글 등록')
        print(response_post)

        response_post_two = self.client.post(url_post, self.second_board_no_photo)
        print('게시글 등록2')
        print(response_post_two)

        board = get_object_or_404(Board, pk=1)

        response_report = self.client.patch(url_report, None)
        print(response_report)
        self.assertEqual(1, board.get_report_count())
        self.assertEqual(200, response_report.status_code)