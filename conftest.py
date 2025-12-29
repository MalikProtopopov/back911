"""Pytest configuration for 911 Corporate Website"""
import os
import django
from django.conf import settings

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website_project.settings.dev')

# Setup Django
django.setup()

import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """Create an API client for testing"""
    return APIClient()


@pytest.fixture(scope='session')
def django_db_setup():
    """Configure database for testing"""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': settings.DATABASES['default']['NAME'],
        'USER': settings.DATABASES['default']['USER'],
        'PASSWORD': settings.DATABASES['default']['PASSWORD'],
        'HOST': settings.DATABASES['default']['HOST'],
        'PORT': settings.DATABASES['default']['PORT'],
        'ATOMIC_REQUESTS': True,
    }

