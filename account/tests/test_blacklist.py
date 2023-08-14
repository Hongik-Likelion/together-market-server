from pprint import pprint
from rest_framework.authentication import get_user_model
from rest_framework.generics import get_object_or_404
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class AccountBlackListTest(APITestCase):
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

    def setUp(self):
        self.client = APIClient()

    def test_blacklist(self):
        # given
        target_user = get_object_or_404(User, email="customer2@gmail.com")
        # when

        response = self.client.post("/user/login/", {"email": "customer1@gmail.com"})
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + response.data["access_token"]
        )

        url_200 = f"/user/{target_user.id}/block/"
        url_404 = f"/user/{3030}/block/"

        response_block_200 = self.client.patch(url_200)
        response_block_404 = self.client.patch(url_404)
        response_block_401 = APIClient().patch(url_200)
        # then

        self.assertEqual(200, response_block_200.status_code)
        self.assertEqual(response_block_200.data["id"], 2)
        self.assertEqual(401, response_block_401.status_code)
        self.assertEqual(404, response_block_404.status_code)
