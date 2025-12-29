"""Tests for Service API endpoints"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from website_api.models import Service, Option, ServiceContent


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sample_service(db):
    """Create a sample service for testing"""
    service = Service.objects.create(
        title="Выездной шиномонтаж",
        slug="shinomontazh",
        is_active=True,
        display_order=1
    )
    ServiceContent.objects.create(
        service=service,
        city=None,
        meta_title="Шиномонтаж по всей России",
        meta_description="Описание шиномонтажа",
        h1_title="Шиномонтаж",
        description="<p>Описание услуги</p>",
        how_it_works_html="<p>Как это работает</p>",
        benefits_html="<p>Преимущества</p>",
        icon_url="/static/icons/tire.svg",
        cover_image_url="/static/images/tire.jpg"
    )
    return service


@pytest.fixture
def sample_services(db):
    """Create multiple sample services for testing"""
    services = []
    for i, (title, slug) in enumerate([
        ("Шиномонтаж", "shinomontazh"),
        ("Эвакуатор", "evakuator"),
        ("Доставка топлива", "dostavka-topliva")
    ], start=1):
        service = Service.objects.create(
            title=title,
            slug=slug,
            is_active=True,
            display_order=i
        )
        services.append(service)
    return services


@pytest.fixture
def inactive_service(db):
    """Create an inactive service"""
    return Service.objects.create(
        title="Неактивная услуга",
        slug="inactive-service",
        is_active=False,
        display_order=99
    )


@pytest.mark.django_db
class TestServiceListAPI:
    """Tests for service list endpoint"""
    
    def test_service_list_returns_200(self, api_client, sample_services):
        """Test that service list returns 200 OK"""
        url = reverse('service-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
    
    def test_service_list_returns_only_active(self, api_client, sample_services, inactive_service):
        """Test that service list returns only active services"""
        url = reverse('service-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3
        
        slugs = [s['slug'] for s in response.data['results']]
        assert 'inactive-service' not in slugs
    
    def test_service_list_search(self, api_client, sample_services):
        """Test service search functionality"""
        url = reverse('service-list')
        response = api_client.get(url, {'search': 'Эвакуатор'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'Эвакуатор'


@pytest.mark.django_db
class TestServiceDetailAPI:
    """Tests for service detail endpoint"""
    
    def test_service_detail_returns_200(self, api_client, sample_service):
        """Test that service detail returns 200 OK"""
        url = reverse('service-detail', kwargs={'slug': 'shinomontazh'})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
    
    def test_service_detail_has_content(self, api_client, sample_service):
        """Test that service detail includes content"""
        url = reverse('service-detail', kwargs={'slug': 'shinomontazh'})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'content' in response.data
        assert response.data['content']['icon_url'] == '/static/icons/tire.svg'
    
    def test_service_detail_not_found(self, api_client, sample_service):
        """Test that non-existent service returns 404"""
        url = reverse('service-detail', kwargs={'slug': 'nonexistent'})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestServiceOptionsAPI:
    """Tests for service options endpoint"""
    
    def test_service_options_returns_200(self, api_client, sample_service):
        """Test that service options returns 200 OK"""
        Option.objects.create(
            title="Замена колеса",
            service=sample_service,
            is_active=True
        )
        
        url = reverse('service-options', kwargs={'slug': 'shinomontazh'})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
    
    def test_service_options_returns_only_active(self, api_client, sample_service):
        """Test that service options returns only active options"""
        Option.objects.create(title="Активная", service=sample_service, is_active=True)
        Option.objects.create(title="Неактивная", service=sample_service, is_active=False)
        
        url = reverse('service-options', kwargs={'slug': 'shinomontazh'})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['title'] == 'Активная'

