from pprint import pprint

from rest_framework.authentication import get_user_model
from rest_framework.test import APIClient, APITestCase
from account.serializers import RegisterSerializer
from market.models import Market

User = get_user_model()


class FavouriteMarketTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        User(
            id=1,
            email="customer1@gmail.com",
            nickname="손님1",
            is_owner=False,
            profile="https://cdn.pixabay.com/photo/2015/03/10/17/23/youtube-667451_1280.png",
        ).save()
        User(
            id=2,
            email="customer2@gmail.com",
            nickname="손님2",
            is_owner=False,
            profile="https://cdn.pixabay.com/photo/2015/03/10/17/23/youtube-667451_1280.png",
        ).save()

        markets = [
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
        for market in markets:
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

    def setUp(self) -> None:
        self.client = APIClient()

    def test_favourite_market(self):
        # given
        url_login = "/user/login/"
        url = "/markets/favourite/"

        market_ids = [1, 2]
        # when
        response_login = self.client.post(url_login, {"email": "customer1@gmail.com"})

        access_token = response_login.data["access_token"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)

        response = self.client.post(url, {"market_id": market_ids})
        # then

        user = User.objects.get(email="customer1@gmail.com")
        favouriteMarkets = user.user_favorite_markets.all()

        self.assertEqual(2, len(favouriteMarkets))
        self.assertEqual(201, response.status_code)
