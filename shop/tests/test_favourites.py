from rest_framework.authentication import get_user_model
from rest_framework.test import APIClient, APITestCase
from market.models import Market
from products.models import Product
from shop.models import Shop
from rest_framework.test import APITestCase

User = get_user_model()


class ShopListTest(APITestCase):
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

        product1 = Product(product_id=1, product_type="먹거리")
        product2 = Product(product_id=2, product_type="해산물")
        product3 = Product(product_id=3, product_type="채소/과일")
        product4 = Product(product_id=4, product_type="기타")

        product1.save()
        product2.save()
        product3.save()
        product4.save()

        shop1 = Shop(
            shop_id=1,
            user_id=1,
            market_id=1,
            shop_name="테스트 상점1",
            shop_address="강서구 방화동 615-14",
            selling_products="치킨, 삼겹살",
            opening_time="15:00",
            closing_time="18:00",
        )
        shop2 = Shop(
            shop_id=2,
            user_id=2,
            market_id=1,
            shop_name="테스트 상점2",
            shop_address="강서구 방화동 615-14",
            selling_products="삼겹살",
            opening_time="12:00",
            closing_time="18:00",
        )

        shop1.save()
        shop2.save()

        shop1.product.add(product1)
        shop1.product.add(product2)
        shop2.product.add(product3)
        shop2.product.add(product4)

    def setUp(self) -> None:
        self.client = APIClient()

    def test_favourite(self):
        # given
        url = "/shop/1/favourite"
        url_404 = "/shop/1293892/favourite"
        # when
        response_login = self.client.post(
            "/user/login/", {"email": "customer1@gmail.com"}
        )

        access_token = response_login.data.get("access_token")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)

        response_200 = self.client.patch(url)
        response_400 = self.client.patch(url)
        response_401 = APIClient().patch(url)
        response_404 = self.client.patch(url_404)
        # then
        self.assertEqual(201, response_200.status_code)
        self.assertEqual(400, response_400.status_code)
        self.assertEqual(401, response_401.status_code)
        self.assertEqual(404, response_404.status_code)

    def test_remove_favourite(self):
        # given
        url_favourite = "/shop/1/favourite"
        url_de_favourite = "/shop/1/de-favourite"
        url_404 = "/shop/1293892/favourite"
        # when
        response_login = self.client.post(
            "/user/login/", {"email": "customer1@gmail.com"}
        )
        access_token = response_login.data.get("access_token")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)

        response_201_favourite = self.client.patch(url_favourite)
        response_400_favourite = self.client.patch(url_favourite)
        response_200_de_favourite = self.client.patch(url_de_favourite)
        response_404_de_favourite = self.client.patch(url_de_favourite)
        # then
        self.assertEqual(201, response_201_favourite.status_code)
        self.assertEqual(400, response_400_favourite.status_code)
        self.assertEqual(200, response_200_de_favourite.status_code)
        self.assertEqual(404, response_404_de_favourite.status_code)
