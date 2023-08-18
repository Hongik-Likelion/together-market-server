from rest_framework.test import APIClient, APITestCase
from rest_framework.authentication import get_user_model

from market.models import Market

User = get_user_model()


# Create your tests here.
class TestMarketApi(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.valid_user = {
            "email": "testuser@gmail.com",
            "nickname": "테스트 유저1",
            "is_owner": False,
            "profile": "https://cdn.pixabay.com/photo/2015/03/10/17/23/youtube-667451_1280.png",
        }
        newUser = User(
            id=1,
            email="testuser@gmail.com",
            profile="https://cdn.pixabay.com/photo/2015/03/10/17/23/youtube-667451_1280.png",
            nickname="testUser1",
            is_owner=False,
            introduction="I AM a Boy"
        )
        newUser.save()

        cls.valid_markets = [
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
        for market in cls.valid_markets:
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

    def test_market_list(self):
        # given
        url = "/markets/"
        # when
        response = self.client.get(url)
        # then
        self.assertEqual(200, response.status_code)
        self.assertEqual(3, len(response.data), msg="list test 성공")

    def test_post_favourite_market(self):
        # given
        url_login = "/user/login/"
        url_favourite = "/markets/favourite/"
        request_email = {"email": "testuser@gmail.com"}
        market_ids = {"market_id": [1]}
        # when
        login_response = self.client.post(url_login, request_email)

        access_token = login_response.data["token"].get("access")

        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)
        favourite_response = self.client.post(url_favourite, market_ids)
        # then
        user = User.objects.get(email=request_email["email"])

        # then
        self.assertEqual(201, favourite_response.status_code)
        self.assertEqual(2, len(user.user_favorite_markets.all()))
