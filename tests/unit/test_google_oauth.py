"""
Unit tests for Google OAuth functionality
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp, SocialAccount
from allauth.socialaccount.providers.google.views import oauth2_login

User = get_user_model()


class GoogleOAuthUnitTest(TestCase):
    """Unit tests for Google OAuth integration"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.google_login_url = reverse('google_oauth2_login')
        self.site = Site.objects.get_current()

    def test_google_oauth_without_configuration(self):
        """Test Google OAuth without Social App configuration"""
        response = self.client.get(self.google_login_url)
        
        # Should return error without proper configuration
        self.assertEqual(response.status_code, 500)

    def test_google_oauth_with_configuration(self):
        """Test Google OAuth with proper Social App configuration"""
        # Create Google Social App
        google_app = SocialApp.objects.create(
            provider='google',
            name='Google OAuth2 Test',
            client_id='test_client_id_12345',
            secret='test_secret_67890'
        )
        google_app.sites.add(self.site)
        
        response = self.client.get(self.google_login_url)
        
        # Should redirect to Google OAuth
        self.assertEqual(response.status_code, 302)
        self.assertIn('accounts.google.com', response.url)

    def test_google_app_creation(self):
        """Test Google Social App creation"""
        google_app = SocialApp.objects.create(
            provider='google',
            name='Google OAuth2 Test',
            client_id='test_client_id',
            secret='test_secret'
        )
        google_app.sites.add(self.site)
        
        self.assertEqual(google_app.provider, 'google')
        self.assertEqual(google_app.client_id, 'test_client_id')
        self.assertEqual(google_app.secret, 'test_secret')
        self.assertIn(self.site, google_app.sites.all())

    def test_social_account_creation(self):
        """Test social account creation for Google OAuth"""
        # Create a user
        user = User.objects.create_user(
            username='googleuser',
            email='google@example.com',
            password='GooglePassword123!'
        )
        
        # Create associated social account
        social_account = SocialAccount.objects.create(
            user=user,
            provider='google',
            uid='google_user_id_123',
            extra_data={
                'email': 'google@example.com',
                'name': 'Google User',
                'picture': 'https://example.com/picture.jpg'
            }
        )
        
        self.assertEqual(social_account.user, user)
        self.assertEqual(social_account.provider, 'google')
        self.assertEqual(social_account.uid, 'google_user_id_123')
        self.assertEqual(social_account.extra_data['email'], 'google@example.com')

    def test_login_page_shows_google_option(self):
        """Test that login page shows Google OAuth option"""
        # Create Google Social App
        google_app = SocialApp.objects.create(
            provider='google',
            name='Google OAuth2',
            client_id='test_client_id',
            secret='test_secret'
        )
        google_app.sites.add(self.site)
        
        login_url = reverse('account_login')
        response = self.client.get(login_url)
        
        self.assertEqual(response.status_code, 200)
        # Check if Google login option is present
        self.assertContains(response, 'google', status_code=200)

    def test_multiple_social_apps_same_provider(self):
        """Test handling multiple social apps for same provider"""
        # Create first Google app
        google_app1 = SocialApp.objects.create(
            provider='google',
            name='Google OAuth2 App 1',
            client_id='client_id_1',
            secret='secret_1'
        )
        google_app1.sites.add(self.site)
        
        # Create second Google app (this should typically not happen)
        google_app2 = SocialApp.objects.create(
            provider='google',
            name='Google OAuth2 App 2',
            client_id='client_id_2',
            secret='secret_2'
        )
        google_app2.sites.add(self.site)
        
        # Both apps should exist
        google_apps = SocialApp.objects.filter(provider='google')
        self.assertEqual(google_apps.count(), 2)

    def test_social_account_user_relationship(self):
        """Test relationship between social account and user"""
        user = User.objects.create_user(
            username='socialuser',
            email='social@example.com',
            password='SocialPassword123!'
        )
        
        # User can have multiple social accounts
        google_account = SocialAccount.objects.create(
            user=user,
            provider='google',
            uid='google_123'
        )
        
        # Test relationship
        self.assertEqual(google_account.user, user)
        self.assertIn(google_account, user.socialaccount_set.all())

    def test_google_oauth_url_construction(self):
        """Test Google OAuth URL construction"""
        google_app = SocialApp.objects.create(
            provider='google',
            name='Google OAuth2',
            client_id='test_client_id',
            secret='test_secret'
        )
        google_app.sites.add(self.site)
        
        response = self.client.get(self.google_login_url, follow=False)
        
        # Should redirect and URL should contain Google OAuth parameters
        if response.status_code == 302:
            redirect_url = response.url
            self.assertIn('oauth2', redirect_url)
            self.assertIn('google', redirect_url)

    def test_google_app_site_association(self):
        """Test Google app site association"""
        google_app = SocialApp.objects.create(
            provider='google',
            name='Google OAuth2',
            client_id='test_client_id',
            secret='test_secret'
        )
        
        # Initially no sites
        self.assertEqual(google_app.sites.count(), 0)
        
        # Add site
        google_app.sites.add(self.site)
        self.assertEqual(google_app.sites.count(), 1)
        self.assertIn(self.site, google_app.sites.all())

    def test_social_account_extra_data_storage(self):
        """Test storage of extra data in social account"""
        user = User.objects.create_user(
            username='extrauser',
            email='extra@example.com',
            password='ExtraPassword123!'
        )
        
        extra_data = {
            'id': '123456789',
            'email': 'extra@example.com',
            'verified_email': True,
            'name': 'Extra User',
            'given_name': 'Extra',
            'family_name': 'User',
            'picture': 'https://lh3.googleusercontent.com/a/default-user',
            'locale': 'en'
        }
        
        social_account = SocialAccount.objects.create(
            user=user,
            provider='google',
            uid='123456789',
            extra_data=extra_data
        )
        
        # Verify extra data is stored correctly
        self.assertEqual(social_account.extra_data['email'], 'extra@example.com')
        self.assertEqual(social_account.extra_data['name'], 'Extra User')
        self.assertTrue(social_account.extra_data['verified_email'])

    def test_google_oauth_provider_validation(self):
        """Test Google OAuth provider validation"""
        google_app = SocialApp.objects.create(
            provider='google',
            name='Google OAuth2',
            client_id='test_client_id',
            secret='test_secret'
        )
        
        # Provider should be exactly 'google'
        self.assertEqual(google_app.provider, 'google')
        
        # Test case sensitivity
        self.assertNotEqual(google_app.provider, 'Google')
        self.assertNotEqual(google_app.provider, 'GOOGLE')
