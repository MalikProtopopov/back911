"""Tests for SEO Meta API endpoints"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from website_api.models import City, Service, SeoMeta


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sample_seo_data(db):
    """Create sample SEO data for testing"""
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
    
    # Home page SEO
    home_seo = SeoMeta.objects.create(
        page_type='home',
        title="911 - Экстренные автоуслуги",
        meta_description="Описание главной",
        h1_title="Экстренная помощь",
        full_slug="/",
        is_active=True
    )
    
    # City page SEO
    city_seo = SeoMeta.objects.create(
        page_type='city',
        city=city,
        title="Услуги в Москве",
        meta_description="Описание города",
        h1_title="Автоуслуги в Москве",
        full_slug="/moskva/",
        is_active=True
    )
    
    # City-service page SEO
    city_service_seo = SeoMeta.objects.create(
        page_type='city_service',
        city=city,
        service=service,
        title="Шиномонтаж в Москве",
        meta_description="Описание",
        h1_title="Шиномонтаж в Москве",
        full_slug="/moskva/shinomontazh/",
        og_title="Шиномонтаж в Москве | 911",
        og_description="OG описание",
        schema_json={"@type": "Service"},
        is_active=True
    )
    
    return {
        'city': city,
        'service': service,
        'home_seo': home_seo,
        'city_seo': city_seo,
        'city_service_seo': city_service_seo
    }


@pytest.mark.django_db
class TestSeoMetaListAPI:
    """Tests for SEO meta list endpoint"""
    
    def test_seo_list_returns_200(self, api_client, sample_seo_data):
        """Test that SEO list returns 200 OK"""
        url = reverse('seo-meta-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
    
    def test_seo_list_filter_by_page_type(self, api_client, sample_seo_data):
        """Test SEO list filter by page type"""
        url = reverse('seo-meta-list')
        response = api_client.get(url, {'page_type': 'city'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['page_type'] == 'city'
    
    def test_seo_list_filter_by_slug(self, api_client, sample_seo_data):
        """Test SEO list filter by full_slug"""
        url = reverse('seo-meta-list')
        response = api_client.get(url, {'full_slug': '/moskva/'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['full_slug'] == '/moskva/'


@pytest.mark.django_db
class TestSeoMetaBySlugAPI:
    """Tests for SEO by slug endpoint"""
    
    def test_seo_by_slug_returns_200(self, api_client, sample_seo_data):
        """Test that SEO by slug returns 200 OK"""
        url = reverse('seo-meta-by-slug')
        response = api_client.get(url, {'slug': '/moskva/shinomontazh/'})
        assert response.status_code == status.HTTP_200_OK
    
    def test_seo_by_slug_returns_correct_data(self, api_client, sample_seo_data):
        """Test that SEO by slug returns correct data"""
        url = reverse('seo-meta-by-slug')
        response = api_client.get(url, {'slug': '/moskva/shinomontazh/'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Шиномонтаж в Москве'
        assert response.data['h1_title'] == 'Шиномонтаж в Москве'
    
    def test_seo_by_slug_requires_slug(self, api_client, sample_seo_data):
        """Test that slug parameter is required"""
        url = reverse('seo-meta-by-slug')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_seo_by_slug_not_found(self, api_client, sample_seo_data):
        """Test 404 when SEO not found"""
        url = reverse('seo-meta-by-slug')
        response = api_client.get(url, {'slug': '/nonexistent/'})
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_seo_by_slug_with_existing_data(self, api_client, sample_seo_data):
        """Test that slug lookup works with complete slug"""
        url = reverse('seo-meta-by-slug')
        # Test with the complete correct slug
        response = api_client.get(url, {'slug': '/moskva/shinomontazh/'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['full_slug'] == '/moskva/shinomontazh/'
    
    def test_seo_by_slug_includes_og_tags(self, api_client, sample_seo_data):
        """Test that response includes Open Graph tags"""
        url = reverse('seo-meta-by-slug')
        response = api_client.get(url, {'slug': '/moskva/shinomontazh/'})
        
        assert response.status_code == status.HTTP_200_OK
        assert 'og_title' in response.data
        assert 'og_description' in response.data
    
    def test_seo_by_slug_includes_schema(self, api_client, sample_seo_data):
        """Test that response includes Schema.org JSON"""
        url = reverse('seo-meta-by-slug')
        response = api_client.get(url, {'slug': '/moskva/shinomontazh/'})
        
        assert response.status_code == status.HTTP_200_OK
        assert 'schema_json' in response.data
        assert response.data['schema_json']['@type'] == 'Service'

