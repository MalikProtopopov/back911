"""Tests for Lead API endpoints"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from website_api.models import City, Service, Lead


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sample_data(db):
    """Create sample data for testing"""
    city = City.objects.create(
        title="Москва",
        slug="moskva",
        is_active=True
    )
    
    service = Service.objects.create(
        title="Шиномонтаж",
        slug="shinomontazh",
        is_active=True
    )
    
    return {'city': city, 'service': service}


@pytest.mark.django_db
class TestLeadCreateAPI:
    """Tests for lead creation endpoint"""
    
    def test_create_lead_returns_201(self, api_client, sample_data):
        """Test that lead creation returns 201 Created"""
        url = reverse('lead-list')
        data = {
            'name': 'Иван Иванов',
            'phone': '+79991234567',
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_create_lead_with_all_fields(self, api_client, sample_data):
        """Test lead creation with all fields"""
        url = reverse('lead-list')
        data = {
            'name': 'Иван Иванов',
            'phone': '+79991234567',
            'email': 'ivan@example.com',
            'city': sample_data['city'].pk,
            'service': sample_data['service'].pk,
            'message': 'Нужен шиномонтаж',
            'source_page': '/moskva/shinomontazh/',
            'utm_source': 'google',
            'utm_medium': 'cpc',
            'utm_campaign': 'test'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Иван Иванов'
        assert response.data['city_title'] == 'Москва'
    
    def test_create_lead_validates_phone(self, api_client, sample_data):
        """Test that phone number is validated"""
        url = reverse('lead-list')
        data = {
            'name': 'Иван',
            'phone': '123',  # Too short
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'phone' in response.data
    
    def test_create_lead_validates_name(self, api_client, sample_data):
        """Test that name is validated"""
        url = reverse('lead-list')
        data = {
            'name': 'И',  # Too short
            'phone': '+79991234567',
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data
    
    def test_create_lead_requires_name(self, api_client, sample_data):
        """Test that name is required"""
        url = reverse('lead-list')
        data = {
            'phone': '+79991234567',
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data
    
    def test_create_lead_requires_phone(self, api_client, sample_data):
        """Test that phone is required"""
        url = reverse('lead-list')
        data = {
            'name': 'Иван',
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'phone' in response.data
    
    def test_lead_has_default_status(self, api_client, sample_data):
        """Test that new lead has default status 'new'"""
        url = reverse('lead-list')
        data = {
            'name': 'Иван',
            'phone': '+79991234567',
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['status'] == 'new'
