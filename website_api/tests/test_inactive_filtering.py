"""Tests for inactive objects filtering across all endpoints"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from website_api.models import (
    City, Service, Option, Advantage, Contact, AppLink, SeoMeta
)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def inactive_objects(db):
    """Create inactive objects for testing"""
    # Inactive city
    inactive_city = City.objects.create(
        title="Неактивный город",
        slug="inactive-city",
        is_active=False
    )
    
    # Active city for comparison
    active_city = City.objects.create(
        title="Активный город",
        slug="active-city",
        is_active=True
    )
    
    # Inactive service
    inactive_service = Service.objects.create(
        title="Неактивная услуга",
        slug="inactive-service",
        is_active=False
    )
    
    # Active service for comparison
    active_service = Service.objects.create(
        title="Активная услуга",
        slug="active-service",
        is_active=True
    )
    
    # Inactive option
    inactive_option = Option.objects.create(
        service=active_service,
        title="Неактивная опция",
        is_active=False
    )
    
    # Active option for comparison
    active_option = Option.objects.create(
        service=active_service,
        title="Активная опция",
        is_active=True
    )
    
    # Inactive advantage
    inactive_advantage = Advantage.objects.create(
        title="Неактивное преимущество",
        description="Описание",
        target_audience="client",
        is_active=False,
        display_order=1
    )
    
    # Active advantage for comparison
    active_advantage = Advantage.objects.create(
        title="Активное преимущество",
        description="Описание",
        target_audience="client",
        is_active=True,
        display_order=2
    )
    
    # Inactive contact
    inactive_contact = Contact.objects.create(
        contact_type="phone",
        value="+79999999999",
        label="Неактивный контакт",
        is_active=False,
        display_order=1
    )
    
    # Active contact for comparison
    active_contact = Contact.objects.create(
        contact_type="phone",
        value="+79998887766",
        label="Активный контакт",
        is_active=True,
        display_order=2
    )
    
    # Inactive app link
    inactive_app_link = AppLink.objects.create(
        platform="ios",
        app_type="client",
        store_url="https://example.com/inactive",
        is_active=False
    )
    
    # Active app link for comparison
    active_app_link = AppLink.objects.create(
        platform="android",
        app_type="client",
        store_url="https://example.com/active",
        is_active=True
    )
    
    # Inactive SEO meta
    inactive_seo = SeoMeta.objects.create(
        page_type="home",
        title="Неактивное SEO",
        meta_description="Описание",
        h1_title="H1",
        full_slug="/inactive-seo/",
        is_active=False
    )
    
    # Active SEO meta for comparison
    active_seo = SeoMeta.objects.create(
        page_type="city",
        city=active_city,
        title="Активное SEO",
        meta_description="Описание",
        h1_title="H1",
        full_slug="/active-seo/",
        is_active=True
    )
    
    return {
        'inactive_city': inactive_city,
        'active_city': active_city,
        'inactive_service': inactive_service,
        'active_service': active_service,
        'inactive_option': inactive_option,
        'active_option': active_option,
        'inactive_advantage': inactive_advantage,
        'active_advantage': active_advantage,
        'inactive_contact': inactive_contact,
        'active_contact': active_contact,
        'inactive_app_link': inactive_app_link,
        'active_app_link': active_app_link,
        'inactive_seo': inactive_seo,
        'active_seo': active_seo,
    }


@pytest.mark.django_db
class TestCityInactiveFiltering:
    """Tests for City inactive filtering"""
    
    def test_city_list_excludes_inactive(self, api_client, inactive_objects):
        """Test that inactive cities are not in list"""
        url = reverse('city-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        slugs = [city['slug'] for city in response.data['results']]
        assert 'inactive-city' not in slugs
        assert 'active-city' in slugs
    
    def test_city_detail_inactive_returns_404(self, api_client, inactive_objects):
        """Test that inactive city detail returns 404"""
        url = reverse('city-detail', kwargs={'slug': 'inactive-city'})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_city_detail_active_returns_200(self, api_client, inactive_objects):
        """Test that active city detail returns 200"""
        url = reverse('city-detail', kwargs={'slug': 'active-city'})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestServiceInactiveFiltering:
    """Tests for Service inactive filtering"""
    
    def test_service_list_excludes_inactive(self, api_client, inactive_objects):
        """Test that inactive services are not in list"""
        url = reverse('service-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        slugs = [service['slug'] for service in response.data['results']]
        assert 'inactive-service' not in slugs
        assert 'active-service' in slugs
    
    def test_service_detail_inactive_returns_404(self, api_client, inactive_objects):
        """Test that inactive service detail returns 404"""
        url = reverse('service-detail', kwargs={'slug': 'inactive-service'})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_service_detail_active_returns_200(self, api_client, inactive_objects):
        """Test that active service detail returns 200"""
        url = reverse('service-detail', kwargs={'slug': 'active-service'})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestOptionInactiveFiltering:
    """Tests for Option inactive filtering"""
    
    def test_option_list_excludes_inactive(self, api_client, inactive_objects):
        """Test that inactive options are not in list"""
        url = reverse('option-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        titles = [option['title'] for option in response.data['results']]
        assert 'Неактивная опция' not in titles
        assert 'Активная опция' in titles


@pytest.mark.django_db
class TestAdvantageInactiveFiltering:
    """Tests for Advantage inactive filtering"""
    
    def test_advantage_list_excludes_inactive(self, api_client, inactive_objects):
        """Test that inactive advantages are not in list"""
        url = reverse('advantage-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        titles = [adv['title'] for adv in response.data['results']]
        assert 'Неактивное преимущество' not in titles
        assert 'Активное преимущество' in titles
    
    def test_advantage_detail_inactive_returns_404(self, api_client, inactive_objects):
        """Test that inactive advantage detail returns 404"""
        adv_id = inactive_objects['inactive_advantage'].id
        url = reverse('advantage-detail', kwargs={'pk': adv_id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_advantage_detail_active_returns_200(self, api_client, inactive_objects):
        """Test that active advantage detail returns 200"""
        adv_id = inactive_objects['active_advantage'].id
        url = reverse('advantage-detail', kwargs={'pk': adv_id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestContactInactiveFiltering:
    """Tests for Contact inactive filtering"""
    
    def test_contact_list_excludes_inactive(self, api_client, inactive_objects):
        """Test that inactive contacts are not in list"""
        url = reverse('contact-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        labels = [contact['label'] for contact in response.data['results']]
        assert 'Неактивный контакт' not in labels
        assert 'Активный контакт' in labels
    
    def test_contact_detail_inactive_returns_404(self, api_client, inactive_objects):
        """Test that inactive contact detail returns 404"""
        contact_id = inactive_objects['inactive_contact'].id
        url = reverse('contact-detail', kwargs={'pk': contact_id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestAppLinkInactiveFiltering:
    """Tests for AppLink inactive filtering"""
    
    def test_app_link_list_excludes_inactive(self, api_client, inactive_objects):
        """Test that inactive app links are not in list"""
        url = reverse('app-link-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        urls = [link['store_url'] for link in response.data['results']]
        assert 'https://example.com/inactive' not in urls
        assert 'https://example.com/active' in urls
    
    def test_app_link_detail_inactive_returns_404(self, api_client, inactive_objects):
        """Test that inactive app link detail returns 404"""
        link_id = inactive_objects['inactive_app_link'].id
        url = reverse('app-link-detail', kwargs={'pk': link_id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestSeoMetaInactiveFiltering:
    """Tests for SeoMeta inactive filtering"""
    
    def test_seo_list_excludes_inactive(self, api_client, inactive_objects):
        """Test that inactive SEO meta are not in list"""
        url = reverse('seo-meta-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        slugs = [seo['full_slug'] for seo in response.data['results']]
        assert '/inactive-seo/' not in slugs
        assert '/active-seo/' in slugs
    
    def test_seo_by_slug_inactive_returns_404(self, api_client, inactive_objects):
        """Test that inactive SEO by slug returns 404"""
        url = reverse('seo-meta-by-slug')
        response = api_client.get(url, {'slug': '/inactive-seo/'})
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_seo_by_slug_active_returns_200(self, api_client, inactive_objects):
        """Test that active SEO by slug returns 200"""
        url = reverse('seo-meta-by-slug')
        response = api_client.get(url, {'slug': '/active-seo/'})
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestCityServiceInactiveFiltering:
    """Tests for City-Service view inactive filtering"""
    
    def test_city_service_inactive_city_returns_404(self, api_client, inactive_objects):
        """Test that inactive city in city-service returns 404"""
        url = reverse('city-service', kwargs={
            'city_slug': 'inactive-city',
            'service_slug': 'active-service'
        })
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_city_service_inactive_service_returns_404(self, api_client, inactive_objects):
        """Test that inactive service in city-service returns 404"""
        url = reverse('city-service', kwargs={
            'city_slug': 'active-city',
            'service_slug': 'inactive-service'
        })
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_city_service_both_active_returns_200(self, api_client, inactive_objects):
        """Test that active city and service return 200"""
        url = reverse('city-service', kwargs={
            'city_slug': 'active-city',
            'service_slug': 'active-service'
        })
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'city' in response.data
        assert 'service' in response.data
        assert 'options' in response.data

