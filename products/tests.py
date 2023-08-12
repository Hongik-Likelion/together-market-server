from rest_framework.test import APIClient, APITestCase

from products.models import Product


# Create your tests here.
class ProductsTest(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        Product(product_id=1, product_type="먹거리").save()
        Product(product_id=2, product_type="해산물").save()
        Product(product_id=3, product_type="채소/과일").save()
        Product(product_id=4, product_type="기타").save()

    def setUp(self):
        self.client = APIClient()

    def test_fetch_product_list(self):
        url = "/products/"

        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        self.assertEqual(4, len(response.data))
