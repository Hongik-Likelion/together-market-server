from rest_framework.authentication import get_user_model
from rest_framework.generics import get_object_or_404
from rest_framework.test import APIClient, APITestCase

from account.models import User
from boards.serializers import BoardSerializer
from market.models import Market
from products.models import Product
from shop.models import Shop


class TestBoard(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.board_request = {
            "market": 1,
            "shop": 1,
            "market_name": "강남시장",
            "shop_name": "바삭마차",
            "purchased_products": [1, 2],
            "photo": ["image1", "image2"],
            "content": "맛있어요",
            "rating": 4
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
        cls.shop = Shop.objects.create(
            shop_id=1,
            market_id=cls.market,
            user_id=cls.user,
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

    def test_post(self):
        # given
        url_login = "/user/login/"
        url_post = "/board/"
        request_login = {"email": "test@example.com"}

        response_login = self.client.post(url_login, request_login)
        access_token = response_login.data.get("access_token")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)

        serializer = BoardSerializer(data=self.board_request, context={'request': self.client.request()})

        if serializer.is_valid():
            serializer.save()
        else:
            print(serializer.errors)


        response_post = self.client.post(url_post, self.board_request)

        print(response_post.content)

        self.assertEqual(201, response_post.status_code)
