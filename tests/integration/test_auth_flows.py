"""
Integration tests for complete authentication flows
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
import time

User = get_user_model()


class AuthenticationFlowIntegrationTest(TestCase):
    """Integration tests for complete authentication workflows"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.site = Site.objects.get_current()

    def test_complete_registration_to_login_flow(self):
        """Test complete flow from registration to login"""
        # Step 1: Register a new user
        signup_url = reverse('account_signup')
        timestamp = str(int(time.time()))
        
        registration_data = {
            'username': f'flowuser{timestamp}',
            'email': f'flowuser{timestamp}@example.com',
            'password1': 'ComplexPassword123!',
            'password2': 'ComplexPassword123!'
        }
        
        # Submit registration
        response = self.client.post(signup_url, registration_data)
        self.assertEqual(response.status_code, 302)  # Successful registration redirects
        
        # Verify user was created
        user = User.objects.get(email=registration_data['email'])
        self.assertEqual(user.username, registration_data['username'])
        
        # Step 2: Logout (clear any auto-login from registration)
        logout_url = reverse('account_logout')
        self.client.post(logout_url)
        
        # Step 3: Login with the registered credentials
        login_url = reverse('account_login')
        login_data = {
            'login': registration_data['email'],
            'password': registration_data['password1']
        }
        
        response = self.client.post(login_url, login_data)
        self.assertEqual(response.status_code, 302)  # Successful login redirects
        
        # Verify user is authenticated
        self.assertIn('_auth_user_id', self.client.session)

    def test_registration_with_existing_email_fails(self):
        """Test that registration fails with existing email"""
        # Create initial user
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='ExistingPassword123!'
        )
        
        # Attempt to register with same email
        signup_url = reverse('account_signup')
        duplicate_data = {
            'username': 'newuser',
            'email': 'existing@example.com',  # Same email
            'password1': 'NewPassword123!',
            'password2': 'NewPassword123!'
        }
        
        response = self.client.post(signup_url, duplicate_data)
        
        # Should not redirect (stays on form with errors)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already exists')
        
        # Verify no duplicate user was created
        users_with_email = User.objects.filter(email='existing@example.com')
        self.assertEqual(users_with_email.count(), 1)

    def test_login_logout_login_cycle(self):
        """Test login -> logout -> login cycle"""
        # Create user
        user_data = {
            'username': 'cycleuser',
            'email': 'cycle@example.com',
            'password': 'CyclePassword123!'
        }
        user = User.objects.create_user(**user_data)
        
        login_url = reverse('account_login')
        logout_url = reverse('account_logout')
        
        # First login
        login_data = {
            'login': user_data['email'],
            'password': user_data['password']
        }
        response = self.client.post(login_url, login_data)
        self.assertEqual(response.status_code, 302)
        self.assertIn('_auth_user_id', self.client.session)
        
        # Logout
        response = self.client.post(logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)
        
        # Login again
        response = self.client.post(login_url, login_data)
        self.assertEqual(response.status_code, 302)
        self.assertIn('_auth_user_id', self.client.session)

    def test_password_reset_flow_initiation(self):
        """Test password reset flow initiation"""
        # Create user
        user = User.objects.create_user(
            username='resetuser',
            email='reset@example.com',
            password='ResetPassword123!'
        )
        
        # Request password reset
        reset_url = reverse('account_reset_password')
        reset_data = {
            'email': 'reset@example.com'
        }
        
        response = self.client.post(reset_url, reset_data)
        
        # Should redirect after submitting reset request
        self.assertEqual(response.status_code, 302)

    def test_google_oauth_configuration_flow(self):
        """Test Google OAuth configuration and access"""
        # Step 1: Test without configuration (should fail)
        google_login_url = reverse('google_oauth2_login')
        response = self.client.get(google_login_url)
        self.assertEqual(response.status_code, 500)  # No configuration
        
        # Step 2: Add configuration
        google_app = SocialApp.objects.create(
            provider='google',
            name='Google OAuth2 Test',
            client_id='test_client_id_integration',
            secret='test_secret_integration'
        )
        google_app.sites.add(self.site)
        
        # Step 3: Test with configuration (should redirect)
        response = self.client.get(google_login_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('oauth2', response.url)

    def test_authentication_redirects(self):
        """Test authentication-based redirects"""
        # Create user
        user = User.objects.create_user(
            username='redirectuser',
            email='redirect@example.com',
            password='RedirectPassword123!'
        )
        
        # Try to access protected admin area (should redirect to login)
        admin_url = '/admin/'
        response = self.client.get(admin_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
        
        # Login
        login_url = reverse('account_login')
        login_data = {
            'login': 'redirect@example.com',
            'password': 'RedirectPassword123!'
        }
        self.client.post(login_url, login_data)
        
        # Try admin again (might still redirect because user is not staff)
        response = self.client.get(admin_url)
        # Regular users still can't access admin, but they're authenticated
        self.assertIn('_auth_user_id', self.client.session)

    def test_session_management_across_requests(self):
        """Test session management across multiple requests"""
        # Create user and login
        user = User.objects.create_user(
            username='sessionuser',
            email='session@example.com',
            password='SessionPassword123!'
        )
        
        login_url = reverse('account_login')
        login_data = {
            'login': 'session@example.com',
            'password': 'SessionPassword123!'
        }
        self.client.post(login_url, login_data)
        
        # Make multiple requests - session should persist
        for i in range(5):
            response = self.client.get(reverse('account_login'))
            self.assertEqual(response.status_code, 200)
            # User should remain authenticated
            self.assertIn('_auth_user_id', self.client.session)

    def test_concurrent_user_registrations(self):
        """Test handling of concurrent user registrations"""
        signup_url = reverse('account_signup')
        base_timestamp = str(int(time.time()))
        
        # Simulate rapid registrations with different data
        registrations = []
        for i in range(3):
            data = {
                'username': f'concurrent{base_timestamp}_{i}',
                'email': f'concurrent{base_timestamp}_{i}@example.com',
                'password1': 'ConcurrentPassword123!',
                'password2': 'ConcurrentPassword123!'
            }
            registrations.append(data)
        
        # Register all users
        for reg_data in registrations:
            response = self.client.post(signup_url, reg_data)
            self.assertEqual(response.status_code, 302)
        
        # Verify all users were created
        for reg_data in registrations:
            self.assertTrue(User.objects.filter(email=reg_data['email']).exists())

    def test_form_validation_persistence(self):
        """Test that form validation errors persist properly"""
        signup_url = reverse('account_signup')
        
        # Submit invalid data
        invalid_data = {
            'username': 'user',
            'email': 'invalid-email',
            'password1': 'weak',
            'password2': 'different'
        }
        
        response = self.client.post(signup_url, invalid_data)
        
        # Should return form with errors
        self.assertEqual(response.status_code, 200)
        
        # Form should retain the submitted username
        self.assertContains(response, 'value="user"')
        
        # Should show validation errors
        self.assertContains(response, 'error')

    def test_authentication_state_consistency(self):
        """Test authentication state consistency"""
        user = User.objects.create_user(
            username='stateuser',
            email='state@example.com',
            password='StatePassword123!'
        )
        
        # Check initial state (not authenticated)
        self.assertNotIn('_auth_user_id', self.client.session)
        
        # Login
        login_url = reverse('account_login')
        login_data = {
            'login': 'state@example.com',
            'password': 'StatePassword123!'
        }
        self.client.post(login_url, login_data)
        
        # Check authenticated state
        self.assertIn('_auth_user_id', self.client.session)
        user_id = int(self.client.session['_auth_user_id'])
        self.assertEqual(user_id, user.pk)
        
        # Logout
        logout_url = reverse('account_logout')
        self.client.post(logout_url)
        
        # Check final state (not authenticated)
        self.assertNotIn('_auth_user_id', self.client.session)
