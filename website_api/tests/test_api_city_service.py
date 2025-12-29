"""Tests for City-Service combination API endpoint"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from website_api.models import (
    City, Service, Option, OptionPrice, 
    TechnicCategory, ServiceContent, SeoMeta
)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sample_data(db):
    """Create sample data for testing city-service endpoint"""
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
        title="Легковой",
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
    
    # City-specific content
    content = ServiceContent.objects.create(
        service=service,
        city=city,
        meta_title="Шиномонтаж в Москве",
        meta_description="Описание",
        h1_title="Шиномонтаж в Москве",
        description="<p>Описание</p>"
    )
    
    # SEO metadata
    seo = SeoMeta.objects.create(
        page_type='city_service',
        city=city,
        service=service,
        title="Шиномонтаж в Москве | 911",
        meta_description="SEO описание",
        h1_title="Шиномонтаж в Москве",
        full_slug="/moskva/shinomontazh/",
        is_active=True
    )
    
    return {
        'city': city,
        'service': service,
        'option': option,
        'price': price,
        'content': content,
        'seo': seo
    }


@pytest.mark.django_db
class TestCityServiceAPI:
    """Tests for city-service combination endpoint"""
    
    def test_city_service_returns_200(self, api_client, sample_data):
        """Test that city-service returns 200 OK"""
        url = reverse('city-service', kwargs={
            'city_slug': 'moskva',
            'service_slug': 'shinomontazh'
        })
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
    
    def test_city_service_returns_city_info(self, api_client, sample_data):
        """Test that response includes city information"""
        url = reverse('city-service', kwargs={
            'city_slug': 'moskva',
            'service_slug': 'shinomontazh'
        })
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'city' in response.data
        assert response.data['city']['slug'] == 'moskva'
    
    def test_city_service_returns_service_info(self, api_client, sample_data):
        """Test that response includes service information"""
        url = reverse('city-service', kwargs={
            'city_slug': 'moskva',
            'service_slug': 'shinomontazh'
        })
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'service' in response.data
        assert response.data['service']['slug'] == 'shinomontazh'
    
    def test_city_service_returns_options_with_prices(self, api_client, sample_data):
        """Test that response includes options with city-specific prices"""
        url = reverse('city-service', kwargs={
            'city_slug': 'moskva',
            'service_slug': 'shinomontazh'
        })
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'options' in response.data
        assert len(response.data['options']) == 1
        assert response.data['options'][0]['price'] is not None
    
    def test_city_service_returns_content(self, api_client, sample_data):
        """Test that response includes city-specific content"""
        url = reverse('city-service', kwargs={
            'city_slug': 'moskva',
            'service_slug': 'shinomontazh'
        })
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'content' in response.data
        assert response.data['content']['h1_title'] == 'Шиномонтаж в Москве'
    
    def test_city_service_returns_seo(self, api_client, sample_data):
        """Test that response includes SEO metadata"""
        url = reverse('city-service', kwargs={
            'city_slug': 'moskva',
            'service_slug': 'shinomontazh'
        })
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'seo' in response.data
        assert response.data['seo']['full_slug'] == '/moskva/shinomontazh/'
    
    def test_city_service_not_found_city(self, api_client, sample_data):
        """Test 404 when city doesn't exist"""
        url = reverse('city-service', kwargs={
            'city_slug': 'nonexistent',
            'service_slug': 'shinomontazh'
        })
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_city_service_not_found_service(self, api_client, sample_data):
        """Test 404 when service doesn't exist"""
        url = reverse('city-service', kwargs={
            'city_slug': 'moskva',
            'service_slug': 'nonexistent'
        })
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

