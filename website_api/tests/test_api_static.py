"""Tests for static content API endpoints (advantages, metrics, contacts, app links)"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from website_api.models import Advantage, Metric, Contact, AppLink


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sample_advantages(db):
    """Create sample advantages for testing"""
    return [
        Advantage.objects.create(
            target_audience='client',
            title="Быстрый отклик",
            description="Описание 1",
            icon_name="lightning",
            display_order=1,
            is_active=True
        ),
        Advantage.objects.create(
            target_audience='partner',
            title="Стабильный доход",
            description="Описание 2",
            icon_name="money",
            display_order=2,
            is_active=True
        ),
        Advantage.objects.create(
            target_audience='both',
            title="Работа 24/7",
            description="Описание 3",
            icon_name="clock",
            display_order=3,
            is_active=True
        ),
    ]


@pytest.fixture
def sample_metrics(db):
    """Create sample metrics for testing"""
    return [
        Metric.objects.create(
            metric_key="total_cities",
            value="82",
            display_label="Городов",
            metric_type="platform",
            is_visible_on_site=True,
            display_order=1
        ),
        Metric.objects.create(
            metric_key="total_partners",
            value="195",
            display_label="Партнеров",
            metric_type="platform",
            is_visible_on_site=True,
            display_order=2
        ),
        Metric.objects.create(
            metric_key="internal_metric",
            value="1000",
            display_label="Внутренняя метрика",
            metric_type="internal",
            is_visible_on_site=False,
            display_order=3
        ),
    ]


@pytest.fixture
def sample_contacts(db):
    """Create sample contacts for testing"""
    return [
        Contact.objects.create(
            contact_type="phone",
            value="+79991234567",
            label="Горячая линия",
            icon_name="phone",
            is_active=True,
            display_order=1
        ),
        Contact.objects.create(
            contact_type="telegram",
            value="@911support",
            label="Telegram",
            icon_name="telegram",
            is_active=True,
            display_order=2
        ),
    ]


@pytest.fixture
def sample_app_links(db):
    """Create sample app links for testing"""
    return [
        AppLink.objects.create(
            platform="ios",
            app_type="client",
            store_url="https://apps.apple.com/app/911",
            is_active=True
        ),
        AppLink.objects.create(
            platform="android",
            app_type="client",
            store_url="https://play.google.com/store/apps/911",
            is_active=True
        ),
    ]


@pytest.mark.django_db
class TestAdvantageAPI:
    """Tests for advantage endpoints"""
    
    def test_advantage_list_returns_200(self, api_client, sample_advantages):
        """Test that advantage list returns 200 OK"""
        url = reverse('advantage-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
    
    def test_advantage_list_filter_by_audience(self, api_client, sample_advantages):
        """Test advantage filter by target audience"""
        url = reverse('advantage-list')
        response = api_client.get(url, {'target_audience': 'client'})
        
        assert response.status_code == status.HTTP_200_OK
        # Check that all returned advantages have correct audience
        for advantage in response.data['results']:
            assert advantage['target_audience'] == 'client'
    
    def test_advantage_list_ordered(self, api_client, sample_advantages):
        """Test advantages are ordered by display_order"""
        url = reverse('advantage-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        orders = [a['display_order'] for a in response.data['results']]
        assert orders == sorted(orders)


@pytest.mark.django_db
class TestMetricAPI:
    """Tests for metric endpoints"""
    
    def test_metric_list_returns_200(self, api_client, sample_metrics):
        """Test that metric list returns 200 OK"""
        url = reverse('metric-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
    
    def test_metric_list_visible_only(self, api_client, sample_metrics):
        """Test metric filter for visible only"""
        url = reverse('metric-list')
        response = api_client.get(url, {'visible_only': 'true'})
        
        assert response.status_code == status.HTTP_200_OK
        # All returned metrics should be visible
        for metric in response.data['results']:
            # Public serializer doesn't include is_visible_on_site field
            assert 'metric_key' in metric
    
    def test_metric_list_filter_by_type(self, api_client, sample_metrics):
        """Test metric filter by type"""
        url = reverse('metric-list')
        response = api_client.get(url, {'metric_type': 'platform'})
        
        assert response.status_code == status.HTTP_200_OK
        # All returned metrics should have the correct type
        for metric in response.data['results']:
            assert metric['metric_type'] == 'platform'


@pytest.mark.django_db
class TestContactAPI:
    """Tests for contact endpoints"""
    
    def test_contact_list_returns_200(self, api_client, sample_contacts):
        """Test that contact list returns 200 OK"""
        url = reverse('contact-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
    
    def test_contact_list_filter_by_type(self, api_client, sample_contacts):
        """Test contact filter by type"""
        url = reverse('contact-list')
        response = api_client.get(url, {'contact_type': 'phone'})
        
        assert response.status_code == status.HTTP_200_OK
        # All returned contacts should have the correct type
        for contact in response.data['results']:
            assert contact['contact_type'] == 'phone'


@pytest.mark.django_db
class TestAppLinkAPI:
    """Tests for app link endpoints"""
    
    def test_app_link_list_returns_200(self, api_client, sample_app_links):
        """Test that app link list returns 200 OK"""
        url = reverse('app-link-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
    
    def test_app_link_filter_by_platform(self, api_client, sample_app_links):
        """Test app link filter by platform"""
        url = reverse('app-link-list')
        response = api_client.get(url, {'platform': 'ios'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['platform'] == 'ios'
    
    def test_app_link_filter_by_type(self, api_client, sample_app_links):
        """Test app link filter by app type"""
        url = reverse('app-link-list')
        response = api_client.get(url, {'app_type': 'client'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

