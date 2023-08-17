from rest_framework.authentication import get_user_model
from rest_framework.generics import get_object_or_404
from rest_framework.test import APIClient, APITestCase
from account.models import BlackList
from account.serializers import RegisterSerializer

from market.models import Market
from pprint import pprint

from products.models import Product
from shop.models import Shop


class AccountLoginTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_login(self):
        # given
        url_sign_up = "/user/"
        url_login = "/user/login/"

        request_owner = {
            "email": "owner@gmail.com",
            "nickname": "사장님",
            "is_owner": True,
            "profile": "https://cdn.pixabay.com/photo/2015/03/10/17/23/youtube-667451_1280.png",
        }

        response_sign_up = self.client.post(url_sign_up, request_owner)

        request_200 = {"email": "owner@gmail.com"}
        request_400 = {}
        request_404 = {"email": "ownerfdsfs@gmail.com"}

        # when
        response_200 = self.client.post(url_login, request_200)
        response_400 = self.client.post(url_login, request_400)
        response_404 = self.client.post(url_login, request_404)

        # then
        self.assertEqual(201, response_sign_up.status_code)
        self.assertEqual(200, response_200.status_code)
        self.assertEqual(400, response_400.status_code)
        self.assertEqual(404, response_404.status_code)

    def test_refresh(self):
        # given
        url_refresh = "/user/reissue/"
        url_login = "/user/login/"
        url_sign_up = "/user/"

        request_200 = {"email": "owner@gmail.com"}

        request_owner = {
            "email": "owner@gmail.com",
            "nickname": "사장님",
            "is_owner": True,
            "profile": "https://cdn.pixabay.com/photo/2015/03/10/17/23/youtube-667451_1280.png",
        }

        # when
        response_sign_up = self.client.post(url_sign_up, request_owner)
        response_login = self.client.post(url_login, request_200)

        refresh_token = response_login.data["refresh_token"]

        # then
        response_200 = self.client.post(url_refresh, {"refresh": refresh_token})
        response_401 = self.client.post(url_refresh, {"refresh": "dfdsf"})

        self.assertEqual(200, response_200.status_code)
        self.assertEqual(401, response_401.status_code)

    def test_fetch_user_info(self):
        # given
        url_refresh = "/user/reissue/"
        url_login = "/user/login/"
        url_sign_up = "/user/"
        url_user_info = "/user/info"

        request_200 = {"email": "customer@gmail.com"}

        request_customer = {
            "email": "customer@gmail.com",
            "nickname": "손님",
            "is_owner": False,
            "profile": "https://cdn.pixabay.com/photo/2015/03/10/17/23/youtube-667451_1280.png",
        }
        request_owner = {
            "email": "owner@gmail.com",
            "nickname": "사장님",
            "is_owner": True,
            "profile": "https://cdn.pixabay.com/photo/2015/03/10/17/23/youtube-667451_1280.png",
        }

        Market.objects.create(
            market_id=1,
            market_name="강남시장",
            street_address="서울특별시 강남구 압구정로 2길 46",
            postal_address="서울특별시 강남구 신사동 510-11",
            has_toilet=True,
            has_parking=True
        )
        Market.objects.create(
            market_id=2,
            market_name="방신 시장",
            street_address="서울특별시 강남구 압구정로29길 72-1",
            postal_address="서울특별시 강남구 압구정동 454",
            has_toilet=False,
            has_parking=True
        )
        shop = Shop.objects.create(
            shop_id=1,
            market_id=1,
            user_id=2,
            shop_name="바삭마차",
            shop_address="마포구 서교동 120-3",
            selling_products="돈까스, 제육",
            opening_time="13:00",
            closing_time="21:00",
            opening_frequency="weekly",
            rating=3.4
        )
        Product(product_id=1, product_type="먹거리").save()
        Product(product_id=2, product_type="해산물").save()
        Product(product_id=3, product_type="채소/과일").save()
        Product(product_id=4, product_type="기타").save()

        shop.product.add(1)
        shop.product.add(2)
        # when
        response_sign_up = self.client.post(url_sign_up, request_customer)
        response_login = self.client.post(url_login, request_200)

        self.client.post(url_sign_up, request_owner)
        response_login_owner = self.client.post(url_login, {"email": "owner@gmail.com"})

        access_token = response_login.data.get("access_token")
        access_token_owner = response_login_owner.data.get("access_token")

        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)

        self.client.post(path="/markets/favourite/", data={"market_id": [1, 2]})

        response = self.client.get(url_user_info)
        print(response.data)

        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data["email"], request_200["email"])
        self.assertEqual(len(response.data.get("favourite_market")), 2)

        self.client.credentials(HTTP_AUTHORIZATION="Bearer ")
        response_401 = self.client.get(url_user_info)

        self.assertEqual(401, response_401.status_code)
        # 여기까지 손님

        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token_owner)
        response_owner = self.client.get(url_user_info)
        print(response_owner.data)
        self.assertEqual(len(response_owner.data["market"].get("product")), 2)
        self.assertEqual(response_owner.data["market"].get("market_id"), 1)
        self.assertEqual(response_owner.status_code, 200)
