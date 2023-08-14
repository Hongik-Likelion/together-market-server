from pprint import pprint

from rest_framework.authentication import get_user_model
from rest_framework.test import APIClient, APITestCase
from account.serializers import RegisterSerializer

User = get_user_model()


class SignUpTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_serializer_save(self):
        # given
        request_valid = {
            "email": "owner@gmail.com",
            "nickname": "사장님",
            "is_owner": True,
            "profile": "https://cdn.pixabay.com/photo/2015/03/10/17/23/youtube-667451_1280.png",
        }
        # when
        serializer = RegisterSerializer(data=request_valid)

        # then
        if serializer.is_valid():
            user = serializer.save()
            self.assertEqual(user.email, request_valid["email"])

    def test_serializer_data_validate(self):
        # given
        request_customer = {
            "email": "customer@gmail.com",
            "nickname": "손님",
            "is_owner": False,
            "profile": "https://cdn.pixabay.com/photo/2015/03/10/17/23/youtube-667451_1280.png",
        }

        request_fail_customer = {
            "email": "customer@gmail.com",
            "is_owner": False,
            "profile": "https://cdn.pixabay.com/photo/2015/03/10/17/23/youtube-667451_1280.png",
        }
        # when
        serializer = RegisterSerializer(data=request_customer)
        fail = RegisterSerializer(data=request_fail_customer)

        # then
        validation = serializer.is_valid()
        valid_fail = fail.is_valid()

        self.assertEqual(validation, True)
        self.assertEqual(valid_fail, False)

    def test_register(self):
        # given
        url = "/user/"

        request_owner = {
            "email": "owner@gmail.com",
            "nickname": "사장님",
            "is_owner": True,
            "profile": "https://cdn.pixabay.com/photo/2015/03/10/17/23/youtube-667451_1280.png",
        }

        request_customer = {
            "email": "customer@gmail.com",
            "nickname": "손님",
            "is_owner": False,
            "profile": "https://cdn.pixabay.com/photo/2015/03/10/17/23/youtube-667451_1280.png",
        }

        request_400 = {
            "email": "customer@gmail.com",
            "is_owner": False,
            "profile": "https://cdn.pixabay.com/photo/2015/03/10/17/23/youtube-667451_1280.png",
        }
        # when
        response_owner = self.client.post(url, request_owner)
        response_customer = self.client.post(url, request_customer)
        response_400 = self.client.post(url, request_400)
        # then
        self.assertEqual(201, response_owner.status_code)
        self.assertEqual(201, response_customer.status_code)
        self.assertEqual(400, response_400.status_code)
