import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from src.models import Client, Technic, TechnicCategory, Partner, City
from src.serializers.client_serializer import ClientProfileSerializer
from src.serializers.partner_serializer import PartnerSimplePhotoSerializer
from users.models import CustomUser


class ClientTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(phone="123")
        self.client_1 = Client.objects.create(first_name="first_name", client_status=1)
        self.user.client = self.client_1
        self.user.save()
        self.client.force_authenticate(self.user)
        self.technic_category = TechnicCategory.objects.create(title="title")
        self.technic = Technic.objects.create(
            brand="brand",
            car_model="model",
            category=self.technic_category,
            client=self.client_1,
        )

    def test_get_client_profile(self):
        url = reverse("client-get-client-profile")
        response = self.client.get(url)
        serializer_data = ClientProfileSerializer(self.client_1).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_update_client_profile(self):
        url = reverse("client-update-client-profile")
        data = {"first_name": "updated_first_name"}
        json_data = json.dumps(data)
        response = self.client.patch(
            url, data=json_data, content_type="application/json"
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.client_1.refresh_from_db()
        self.assertEqual("updated_first_name", self.client_1.first_name)

    def test_add_client_technic(self):
        self.assertEqual(1, Technic.objects.all().count())
        url = reverse("client-add-client-technic")
        data = {
            "brand": "brand",
            "car_model": "model",
            "category": self.technic_category.id,
        }
        json_data = json.dumps(data)
        response = self.client.post(
            url, data=json_data, content_type="application/json"
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, Technic.objects.all().count())

    def test_add_client_technic_400(self):
        url = reverse("client-add-client-technic")
        data = {"brand": "brand", "car_model": "model", "category": 0}
        json_data = json.dumps(data)
        response = self.client.post(
            url, data=json_data, content_type="application/json"
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_update_client_technic(self):
        url = reverse("client-update-client-technic", args=(self.technic.id,))
        data = {
            "brand": "updated_brand",
            "car_model": "updated_model",
            "category": self.technic_category.id,
        }
        json_data = json.dumps(data)
        response = self.client.patch(
            url, data=json_data, content_type="application/json"
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.technic.refresh_from_db()
        self.assertEqual("updated_brand", self.technic.brand)
        self.assertEqual("updated_model", self.technic.car_model)

    def test_update_client_technic_404(self):
        url = reverse("client-update-client-technic", args=(0,))
        response = self.client.patch(url)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_update_client_technic_400(self):
        url = reverse("client-update-client-technic", args=(self.technic.id,))
        data = {"brand": "updated_brand", "car_model": "updated_model", "category": 0}
        json_data = json.dumps(data)
        response = self.client.patch(
            url, data=json_data, content_type="application/json"
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_delete_client_technic(self):
        url = reverse("client-delete-client-technic", args=(self.technic.id,))
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(0, Technic.objects.all().count())

    def test_delete_client_technic_404(self):
        url = reverse("client-delete-client-technic", args=(0,))
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_get_list_of_partners(self):
        self.city = City.objects.create(title="test")
        self.partner = Partner.objects.create(
            first_name="test",
            last_name="test",
            legal_status="legal_entity",
            city=self.city,
            verify="confirmed",
        )

        url = reverse("client-get-list-of-partners")
        response = self.client.get(url)
        serializer_data = PartnerSimplePhotoSerializer([self.partner], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
