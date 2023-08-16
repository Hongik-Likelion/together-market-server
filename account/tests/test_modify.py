from rest_framework.authentication import get_user_model
from rest_framework.generics import get_object_or_404
from rest_framework.test import APIClient, APITestCase
from account.models import BlackList, User
from account.serializers import RegisterSerializer

from market.models import Market
from pprint import pprint

from shop.models import Shop


class AccountLoginTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_modify(self):
        # given
        url_login = "/user/login/"
        url_modify = "/user/modify/"

        request_owner = User.objects.create(
            email="owner@gmail.com",
            nickname="사장님",
            is_owner=True,
            profile="https://cdn.pixabay.com/photo/2015/03/10/17/23/youtube-667451_1280.png",
            introduction="owner1",
        )
        request_customer = User.objects.create(
            email="customer@gmail.com",
            nickname="손님",
            is_owner=False,
            profile="https://cdn.pixabay.com/photo/2015/03/10/17/23/youtube-667451_1280.png",
            introduction="customer1",
        )
        # {
        #     "email": "customer@gmail.com",
        #     "nickname": "손님",
        #     "is_owner": False,
        #     "profile": "https://cdn.pixabay.com/photo/2015/03/10/17/23/youtube-667451_1280.png",
        # }
        market = Market.objects.create(
            market_id=1,
            market_name="강남시장",
            street_address="서울특별시 강남구 압구정로 2길 46",
            postal_address="서울특별시 강남구 신사동 510-11",
            has_toilet=True,
            has_parking=True
        )
        shop = Shop.objects.create(
            shop_id=1,
            market_id=market.market_id,
            user_id=request_owner.id,
            shop_name="바삭마차",
            shop_address="마포구 서교동 120-3",
            selling_products="돈까스, 제육",
            opening_time="13:00",
            closing_time="21:00",
            opening_frequency="weekly",
            rating=3.4
        )

        request_login_owner = {"email": "owner@gmail.com"}
        request_login_customer = {"email": "customer@gmail.com"}

        response_login_owner = self.client.post(url_login, request_login_owner)
        access_token_owner = response_login_owner.data.get("access_token")

        request_login_customer = self.client.post(url_login, request_login_customer)
        access_token_customer = request_login_customer.data.get("access_token")

        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token_owner)

        owner_modify_data = {
            "shop_name": "바삭열차",
            "introduction": "튀김집",
            "opening_time": "12:30",
            "closing_time": "15:30"
        }
        response_owner = self.client.patch(url_modify, owner_modify_data)
        print(response_owner.data)
        self.assertEqual(200, response_owner.status_code)
        shop = get_object_or_404(Shop, pk=1)
        print(shop.shop_name, shop.opening_time)

        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token_customer)

        customer_modify_data = {
            "nickname": "야식이",
            "introduction": "인트로",
            "favourite_markets": [1,]
        }

        response_customer = self.client.patch(url_modify, customer_modify_data)
        print(response_customer.data)
        self.assertEqual(200, response_customer.status_code)