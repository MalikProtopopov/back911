"""Tests for City API endpoints"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from website_api.models import City, CityContent, Service


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sample_city(db):
    """Create a sample city for testing"""
    city = City.objects.create(
        title="Москва",
        slug="moskva",
        is_active=True,
        display_order=1
    )
    CityContent.objects.create(
        city=city,
        meta_title="Автоуслуги в Москве",
        meta_description="Описание услуг в Москве",
        h1_title="Услуги в Москве",
        short_description="Краткое описание",
        full_description="<p>Полное описание</p>",
        partner_count=10,
        avg_rating=4.5,
        review_count=100
    )
    return city


@pytest.fixture
def sample_cities(db):
    """Create multiple sample cities for testing"""
    cities = []
    for i, name in enumerate(["Москва", "Казань", "Краснодар"], start=1):
        city = City.objects.create(
            title=name,
            slug=name.lower().replace(" ", "-"),
            is_active=True,
            display_order=i
        )
        cities.append(city)
    return cities


@pytest.fixture
def inactive_city(db):
    """Create an inactive city"""
    return City.objects.create(
        title="Неактивный город",
        slug="inactive-city",
        is_active=False,
        display_order=99
    )


@pytest.mark.django_db
class TestCityListAPI:
    """Tests for city list endpoint"""
    
    def test_city_list_returns_200(self, api_client, sample_cities):
        """Test that city list returns 200 OK"""
        url = reverse('city-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
    
    def test_city_list_returns_only_active(self, api_client, sample_cities, inactive_city):
        """Test that city list returns only active cities"""
        url = reverse('city-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3
        
        slugs = [c['slug'] for c in response.data['results']]
        assert 'inactive-city' not in slugs
    
    def test_city_list_search(self, api_client, sample_cities):
        """Test city search functionality"""
        url = reverse('city-list')
        response = api_client.get(url, {'search': 'Москва'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'Москва'
    
    def test_city_list_ordering(self, api_client, sample_cities):
        """Test city list is ordered by display_order"""
        url = reverse('city-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        titles = [c['title'] for c in response.data['results']]
        assert titles == ['Москва', 'Казань', 'Краснодар']


@pytest.mark.django_db
class TestCityDetailAPI:
    """Tests for city detail endpoint"""
    
    def test_city_detail_returns_200(self, api_client, sample_city):
        """Test that city detail returns 200 OK"""
        url = reverse('city-detail', kwargs={'slug': 'moskva'})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
    
    def test_city_detail_has_content(self, api_client, sample_city):
        """Test that city detail includes content"""
        url = reverse('city-detail', kwargs={'slug': 'moskva'})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'content' in response.data
        assert response.data['content']['partner_count'] == 10
        assert response.data['content']['avg_rating'] == '4.50'
    
    def test_city_detail_not_found(self, api_client, sample_city):
        """Test that non-existent city returns 404"""
        url = reverse('city-detail', kwargs={'slug': 'nonexistent'})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_inactive_city_not_accessible(self, api_client, inactive_city):
        """Test that inactive city is not accessible"""
        url = reverse('city-detail', kwargs={'slug': 'inactive-city'})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestCityServicesAPI:
    """Tests for city services endpoint"""
    
    def test_city_services_returns_200(self, api_client, sample_city):
        """Test that city services returns 200 OK"""
        # Create a service
        Service.objects.create(
            title="Шиномонтаж",
            slug="shinomontazh",
            is_active=True
        )
        
        url = reverse('city-services', kwargs={'slug': 'moskva'})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
    
    def test_city_services_returns_only_active(self, api_client, sample_city):
        """Test that city services returns only active services"""
        Service.objects.create(title="Активная", slug="active", is_active=True)
        Service.objects.create(title="Неактивная", slug="inactive", is_active=False)
        
        url = reverse('city-services', kwargs={'slug': 'moskva'})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['slug'] == 'active'

