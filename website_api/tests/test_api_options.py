"""Tests for Option API endpoints"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from website_api.models import City, Service, Option, OptionPrice, TechnicCategory


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
    
    tech_category = TechnicCategory.objects.create(
        title="Легковой автомобиль",
        service=service
    )
    
    option = Option.objects.create(
        title="Замена колеса",
        service=service,
        is_active=True
    )
    
    price = OptionPrice.objects.create(
        option=option,
        city=city,
        technic_category=tech_category,
        amount=500.00
    )
    
    return {
        'city': city,
        'service': service,
        'tech_category': tech_category,
        'option': option,
        'price': price
    }


@pytest.mark.django_db
class TestOptionListAPI:
    """Tests for option list endpoint"""
    
    def test_option_list_returns_200(self, api_client, sample_data):
        """Test that option list returns 200 OK"""
        url = reverse('option-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
    
    def test_option_list_filter_by_service(self, api_client, sample_data):
        """Test option list filter by service"""
        url = reverse('option-list')
        response = api_client.get(url, {'service__slug': 'shinomontazh'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1


@pytest.mark.django_db
class TestOptionDetailAPI:
    """Tests for option detail endpoint"""
    
    def test_option_detail_returns_200(self, api_client, sample_data):
        """Test that option detail returns 200 OK"""
        url = reverse('option-detail', kwargs={'pk': sample_data['option'].pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
    
    def test_option_detail_has_prices(self, api_client, sample_data):
        """Test that option detail includes prices"""
        url = reverse('option-detail', kwargs={'pk': sample_data['option'].pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'prices' in response.data
        assert len(response.data['prices']) == 1


@pytest.mark.django_db
class TestOptionByCityAPI:
    """Tests for options by city endpoint"""
    
    def test_options_by_city_returns_200(self, api_client, sample_data):
        """Test that options by city returns 200 OK"""
        url = reverse('option-by-city')
        response = api_client.get(url, {'city': 'moskva'})
        assert response.status_code == status.HTTP_200_OK
    
    def test_options_by_city_requires_city_param(self, api_client, sample_data):
        """Test that city parameter is required"""
        url = reverse('option-by-city')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_options_by_city_filter_by_service(self, api_client, sample_data):
        """Test options by city with service filter"""
        url = reverse('option-by-city')
        response = api_client.get(url, {
            'city': 'moskva',
            'service': 'shinomontazh'
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
    
    def test_options_by_city_includes_price(self, api_client, sample_data):
        """Test that response includes price for the city"""
        url = reverse('option-by-city')
        response = api_client.get(url, {'city': 'moskva'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]['price'] is not None
        assert response.data[0]['price']['amount'] == '500.00'


@pytest.mark.django_db
class TestTechnicCategoryAPI:
    """Tests for technic category endpoint"""
    
    def test_technic_category_list_returns_200(self, api_client, sample_data):
        """Test that technic category list returns 200 OK"""
        url = reverse('technic-category-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
    
    def test_technic_category_filter_by_service(self, api_client, sample_data):
        """Test technic category filter by service"""
        url = reverse('technic-category-list')
        response = api_client.get(url, {'service__slug': 'shinomontazh'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

