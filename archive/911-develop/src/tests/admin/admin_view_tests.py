import json
from unittest import mock

from django.urls import reverse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.test import APITestCase

from src.models import Client
from src.models.order import Order
from src.models.technic import Technic, TechnicCategory
from src.serializers.client_serializer import ClientInfoForAdminSerializer
from src.serializers.partner_serializer import PartnerInfoForAdminSerializer
from src.tests.mock.test_creator import TestMockCreator


class AdminTestCase(APITestCase):
    def setUp(self):
        factory = TestMockCreator()
        self.admin = factory.create_admin()
        self.partner = factory.create_partner()
        self.client_1 = factory.create_active_client()
        self.technic_category = TechnicCategory.objects.create(title="test")
        self.technics = Technic.objects.create(
            brand="test",
            car_model="test",
            category=self.technic_category,
            client=self.client_1,
        )
        conditions = {"10": "100"}
        self.orders = Order.objects.create(
            point_coordinates=["test"],
            total_price="1",
            address="test",
            conditions=conditions,
            client=self.client_1,
        )

    @mock.patch.object(IsAuthenticated, "has_permission", return_value=True)
    @mock.patch.object(IsAdminUser, "has_permission", return_value=True)
    def test_update_info_for_admin(
        self, mock_has_permission_is_authenticated, mock_has_permission_is_admin_user
    ):
        url = reverse("partner-update-info-for-admin", args=(self.admin.id,))
        data = {"first_name": "updated_name"}
        json_data = json.dumps(data)
        response = self.client.patch(
            url, data=json_data, content_type="application/json"
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.admin.refresh_from_db()
        self.assertEqual("updated_name", self.admin.first_name)

    @mock.patch.object(IsAuthenticated, "has_permission", return_value=True)
    @mock.patch.object(IsAdminUser, "has_permission", return_value=True)
    def test_get_info_partner_for_admin(
        self, mock_has_permission_is_authenticated, mock_has_permission_is_admin_user
    ):
        self.partner.accepted_orders = 0
        self.partner.cancelled_orders = 0
        url = reverse("partner-get-info-partner-for-admin", args=(self.partner.id,))
        response = self.client.get(url)
        serializer_data = PartnerInfoForAdminSerializer(self.partner).data
        self.assertEqual(serializer_data, response.data["results"])
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    @mock.patch.object(IsAuthenticated, "has_permission", return_value=True)
    @mock.patch.object(IsAdminUser, "has_permission", return_value=True)
    def test_update_partner(
        self, mock_has_permission_is_authenticated, mock_has_permission_is_admin_user
    ):
        url = reverse("partner-update-partner", args=(self.partner.id,))
        data = {"first_name": "updated_name"}
        json_data = json.dumps(data)
        response = self.client.patch(
            url, data=json_data, content_type="application/json"
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.partner.refresh_from_db()
        self.assertEqual("updated_name", self.partner.first_name)

    @mock.patch.object(IsAuthenticated, "has_permission", return_value=True)
    @mock.patch.object(IsAdminUser, "has_permission", return_value=True)
    def test_get_info_client_for_admin(
        self, mock_has_permission_is_authenticated, mock_has_permission_is_admin_user
    ):
        url = reverse("partner-get-info-client-for-admin", args=(self.client_1.id,))
        response = self.client.get(url)
        serializer_data = ClientInfoForAdminSerializer(self.client_1).data
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    @mock.patch.object(IsAuthenticated, "has_permission", return_value=True)
    @mock.patch.object(IsAdminUser, "has_permission", return_value=True)
    def test_add_client_by_admin(
        self, mock_has_permission_is_authenticated, mock_has_permission_is_admin_user
    ):
        self.assertEqual(1, Client.objects.count())
        url = reverse("partner-add-client-by-admin")
        data = {"first_name": "updated_name", "phone": "456"}
        json_data = json.dumps(data)
        response = self.client.post(
            url, data=json_data, content_type="application/json"
        )
        self.client_1.refresh_from_db()
        self.assertEqual(2, Client.objects.count())
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
