from rest_framework.authentication import get_user_model
from rest_framework.test import APIClient, APITestCase
from account.serializers import RegisterSerializer

from market.models import Market
from pprint import pprint

User = get_user_model()


# Create your tests here.
class AccoutTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.request_valid = {
            "email": "testuser@gmail.com",
            "nickname": "테스트 유저1",
            "is_owner": True,
            "profile": "https://cdn.pixabay.com/photo/2015/03/10/17/23/youtube-667451_1280.png",
        }

        cls.request_inValid = {
            "nickname": "테스트 유저1",
            "is_owner": True,
            "profile": "https://cdn.pixabay.com/photo/2015/03/10/17/23/youtube-667451_1280.png",
        }

        cls.request_owner = {
            "email": "owner@gmail.com",
            "nickname": "사장님 1",
            "is_owner": True,
            "profile": "https://cdn.pixabay.com/photo/2015/03/10/17/23/youtube-667451_1280.png",
        }

        cls.request_customer = {
            "email": "customer@gmail.com",
            "nickname": "손님 1",
            "is_owner": False,
            "profile": "https://cdn.pixabay.com/photo/2015/03/10/17/23/youtube-667451_1280.png",
        }

        cls.marketList = [
            {
                "market_id": 1,
                "market_name": "강남 시장",
                "street_address": "서울특별시 강남구 압구정로 2길 46",
                "postal_address": "서울특별시 강남구 신사동 510-11",
                "has_toilet": True,
                "has_parking": True,
            },
            {
                "market_id": 2,
                "market_name": "방신 시장",
                "street_address": "서울특별시 강남구 압구정로29길 72-1",
                "postal_address": "서울특별시 강남구 압구정동 454",
                "has_toilet": False,
                "has_parking": True,
            },
            {
                "market_id": 3,
                "market_name": "까치산 시장",
                "street_address": "서울특별시 강남구 학동로 101길 26",
                "postal_address": "서울특별시 강남구 청담동 134-20",
                "has_toilet": True,
                "has_parking": False,
            },
        ]

        print("Initialize Market")
        for market in cls.marketList:
            print(f'marketId={market["market_id"]} marketName={market["market_name"]}')
            newMarket = Market(
                market_id=market["market_id"],
                market_name=market["market_name"],
                street_address=market["street_address"],
                postal_address=market["postal_address"],
                has_toilet=market["has_toilet"],
                has_parking=market["has_parking"],
            )
            newMarket.save()

    def setUp(self):
        self.client = APIClient()

    def test_register_user_serializer(self):
        serializer_valid = RegisterSerializer(data=self.request_valid)
        serializer_inValid = RegisterSerializer(data=self.request_inValid)

        self.assertEqual(serializer_valid.is_valid(), True)
        self.assertEqual(serializer_inValid.is_valid(), False)

    def test_serializer_save(self):
        serializer = RegisterSerializer(data=self.request_valid)

        if serializer.is_valid():
            user = serializer.save()
            self.assertEqual(user.email, self.request_valid["email"])

    def test_serializer_data_validate(self):
        serializer = RegisterSerializer(data=self.request_customer)
        fail = RegisterSerializer(data=self.request_inValid)
        validation = serializer.is_valid()
        valid_fail = fail.is_valid()

        self.assertEqual(validation, True)
        self.assertEqual(valid_fail, False)

    def test_register(self):
        url = "/user/"

        # given
        # when
        response_owner = self.client.post(url, self.request_owner)
        response_customer = self.client.post(url, self.request_customer)
        response_400 = self.client.post(url, self.request_inValid)
        # then
        self.assertEqual(201, response_owner.status_code)
        self.assertEqual(201, response_customer.status_code)
        self.assertEqual(400, response_400.status_code)

    def test_login(self):
        # given
        url_sign_up = "/user/"
        url_login = "/user/login/"

        response_sign_up = self.client.post(url_sign_up, self.request_owner)

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

        # when
        response_sign_up = self.client.post(url_sign_up, self.request_owner)
        response_login = self.client.post(url_login, request_200)

        refresh_token = response_login.data["token"].get("refresh")

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

        # when
        response_sign_up = self.client.post(url_sign_up, self.request_customer)
        response_login = self.client.post(url_login, request_200)

        access_token = response_login.data["token"].get("access")

        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)
        response = self.client.get(url_user_info)

        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data["email"], request_200["email"])

        self.client.credentials(HTTP_AUTHORIZATION="Bearer ")
        response_401 = self.client.get(url_user_info)

        self.assertEqual(401, response_401.status_code)
