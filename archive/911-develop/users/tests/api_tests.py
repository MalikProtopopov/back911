import json

from rest_framework import status
from rest_framework.test import APITestCase

from users.models import CustomUser


class CustomUserTestCase(APITestCase):
    def setUp(self) -> None:
        self.login_url = "/api/users/auth/login/"
        self.user = CustomUser.objects.create_user(phone="1234")

    def test_user_login_register_200(self) -> None:
        data = {"phone": "1234"}
        json_data = json.dumps(data)
        response = self.client.post(
            self.login_url, data=json_data, content_type="application/json"
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual({"success": True}, response.data)

    def test_user_login_register_400(self) -> None:
        data = {"phone": "phone"}
        json_data = json.dumps(data)
        response = self.client.post(
            self.login_url, data=json_data, content_type="application/json"
        )
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
