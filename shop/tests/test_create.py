from rest_framework.authentication import get_user_model
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.test import APIClient, APITestCase
from market.models import Market
from products.models import Product
from shop.models import Shop
from shop.serializers import ShopCreateSerializer

User = get_user_model()


class ShopCreateTest(APITestCase):
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

        Product(product_id=1, product_type="먹거리").save()
        Product(product_id=2, product_type="해산물").save()
        Product(product_id=3, product_type="채소/과일").save()
        Product(product_id=4, product_type="기타").save()

    def setUp(self) -> None:
        self.client = APIClient()

    def test_shop_serializer_validation(self):
        # given
        valid_data = {
            "market_id": 1,
            "shop_name": "테스트 상점1",
            "shop_address": "강서구 방화동 615-14",
            "selling_products": "치킨, 삼겹살",
            "opening_time": "15:00",
            "closing_time": "18:00",
            "opening_frequency": "자주",
            "product_categories": [1, 2, 3],
        }
        inValid_data = {
            "market_id": 100,
            "shop_name": "테스트 상점1",
            "shop_address": "강서구 방화동 615-14",
            "selling_products": "치킨, 삼겹살",
            "opening_time": "15:00",
            "closing_time": "18:00",
            "opening_frequency": "자주",
            "product_categories": [1, 2, 3],
        }
        serializer = ShopCreateSerializer(data=valid_data)
        serializer_404 = ShopCreateSerializer(data=inValid_data)
        # when
        valid = serializer.is_valid(raise_exception=True)
        # then
        self.assertEqual(True, valid)

    def test_serializer_create(self):
        # given
        data = {
            "market_id": 1,
            "shop_name": "테스트 상점1",
            "shop_address": "강서구 방화동 615-14",
            "selling_products": "치킨, 삼겹살",
            "opening_time": "15:00",
            "closing_time": "18:00",
            "opening_frequency": "자주",
            "product_categories": [1, 3],
        }
        # when
        serializer = ShopCreateSerializer(data=data)
        user = User.objects.get(id=1)
        if serializer.is_valid():
            shop = serializer.save(user=user)
        # then
        find_by_user_id = Shop.objects.get(user_id=1)
        find_by_shop_name = Shop.objects.get(shop_name="테스트 상점1")

        self.assertEqual("테스트 상점1", find_by_user_id.shop_name)
        self.assertEqual("테스트 상점1", find_by_shop_name.shop_name)

    def test_shop_create(self):
        # given
        url = "/shop/"
        data = {
            "market_id": 1,
            "shop_name": "테스트 상점1",
            "shop_address": "강서구 방화동 615-14",
            "selling_products": "치킨, 삼겹살",
            "opening_time": "15:00",
            "closing_time": "18:00",
            "opening_frequency": "자주",
            "product_categories": [1, 3],
        }
        data_400 = {
            "market_id": 1,
            "shop_name": "테스트 상점1",
            "shop_address": "강서구 방화동 615-14",
            "selling_products": "치킨, 삼겹살",
            "opening_time": "15:00",
            "closing_time": "18:00",
            "product_categories": [1, 3],
        }
        data_404 = {
            "market_id": 10083293829,
            "shop_name": "테스트 상점1",
            "shop_address": "강서구 방화동 615-14",
            "selling_products": "치킨, 삼겹살",
            "opening_time": "15:00",
            "closing_time": "18:00",
            "opening_frequency": "자주",
            "product_categories": [1, 3],
        }
        # when
        response = self.client.post("/user/login/", {"email": "customer1@gmail.com"})
        access_token = response.data.get("access_token")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)

        response_201 = self.client.post(url, data)
        response_400 = self.client.post(url, data_400)
        response_401 = APIClient().post(url, data)
        response_404 = self.client.post(url, data_404)

        # then
        self.assertEqual(201, response_201.status_code)
        self.assertEqual(400, response_400.status_code)
        self.assertEqual(401, response_401.status_code)
        self.assertEqual(404, response_404.status_code)
