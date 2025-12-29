from unittest import mock

from django.conf import settings
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from src.models import Client
from users.models import CustomUser
from users.services.user_auth import UserAuth


class UserAuthTest(APITestCase):
    def setUp(self):
        self.phone = "8930"
        self.user_auth = UserAuth(self.phone)
        self.user1 = CustomUser.objects.create_user(phone="8928")

    def test_get_user_existing(self):
        user_auth = UserAuth(phone="8928")
        user = user_auth.get_user()
        self.assertIsNotNone(user)
        self.assertEqual(user, self.user1)
        self.assertEqual(user.phone, "8928")

    def test_get_user_non_existing(self):
        user_auth = UserAuth("0000")
        user = user_auth.get_user()
        self.assertIsNone(user)

    def test_create_user_correct(self):
        user_auth = UserAuth("1234")
        user = user_auth._create_user()
        self.assertIsNotNone(user)
        self.assertEqual(user.phone, "1234")

    def test_create_user_incorrect(self):
        user_auth = UserAuth("string")
        with self.assertRaises(ValidationError):
            user_auth._create_user()

    def test_create_client_correct(self):
        user_auth = UserAuth("1235")
        user = user_auth._create_client()
        self.assertIsNotNone(user)
        self.assertIsNotNone(user.client)
        self.assertEqual(user.phone, "1235")

    def test_create_client_incorrect(self):
        user_auth = UserAuth("str")
        initial_client_count = Client.objects.count()
        with self.assertRaises(ValidationError):
            user_auth._create_client()
        self.assertEqual(Client.objects.count(), initial_client_count)

    def test_create_code_debug(self):
        with mock.patch.object(settings, "DEBUG", True):
            code = self.user_auth._create_code()
            self.assertEqual(code, 1234)

    def test_create_code_production(self):
        with mock.patch.object(settings, "DEBUG", False):
            with mock.patch("random.randint", return_value=5678):
                code = self.user_auth._create_code()
                self.assertEqual(code, 5678)
