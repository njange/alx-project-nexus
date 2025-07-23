"""
Pytest configuration and fixtures for authentication testing
"""
import pytest
import os
import tempfile
from django.test import override_settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

User = get_user_model()


# Test settings override for better performance and isolation
TEST_SETTINGS = {
    'EMAIL_BACKEND': 'django.core.mail.backends.locmem.EmailBackend',
    'PASSWORD_HASHERS': [
        'django.contrib.auth.hashers.MD5PasswordHasher',  # Faster for testing
    ],
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
    'CACHES': {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
    'MEDIA_ROOT': tempfile.mkdtemp(),
    'ACCOUNT_EMAIL_VERIFICATION': 'none',  # Disable for testing
}


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Allow database access for all tests"""
    pass


@pytest.fixture(autouse=True)
def use_test_settings():
    """Automatically use test settings for all tests"""
    with override_settings(**TEST_SETTINGS):
        yield


@pytest.fixture
def user_data():
    """Standard user data for testing"""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'ComplexPassword123!'
    }


@pytest.fixture
def test_user(user_data):
    """Create a test user"""
    return User.objects.create_user(**user_data)


@pytest.fixture
def admin_user():
    """Create an admin user"""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='AdminPassword123!'
    )


@pytest.fixture
def google_social_app():
    """Create Google Social App for OAuth testing"""
    site = Site.objects.get_current()
    app = SocialApp.objects.create(
        provider='google',
        name='Google OAuth2 Test',
        client_id='test_client_id_12345',
        secret='test_secret_67890'
    )
    app.sites.add(site)
    return app


@pytest.fixture
def chrome_driver():
    """Chrome WebDriver for E2E testing"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    
    yield driver
    
    driver.quit()
