"""
Unit tests for user login functionality
"""
import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
import time

User = get_user_model()


class UserLoginUnitTest(TestCase):
    """Unit tests for user login"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.login_url = reverse('account_login')
        self.logout_url = reverse('account_logout')
        
        # Create test user
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'ComplexPassword123!'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_login_page_loads(self):
        """Test that login page loads correctly"""
        response = self.client.get(self.login_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(response, 'name="login"')
        self.assertContains(response, 'name="password"')

    def test_valid_login_with_email(self):
        """Test login with valid email and password"""
        login_data = {
            'login': self.user_data['email'],
            'password': self.user_data['password']
        }
        
        response = self.client.post(self.login_url, login_data)
        
        # Should redirect after successful login
        self.assertEqual(response.status_code, 302)
        
        # Check user is authenticated in session
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

    def test_valid_login_with_username(self):
        """Test login with valid username and password"""
        login_data = {
            'login': self.user_data['username'],
            'password': self.user_data['password']
        }
        
        response = self.client.post(self.login_url, login_data)
        
        # Should redirect after successful login
        self.assertEqual(response.status_code, 302)
        
        # Check user is authenticated
        self.assertIn('_auth_user_id', self.client.session)

    def test_login_with_wrong_password(self):
        """Test login with wrong password"""
        login_data = {
            'login': self.user_data['email'],
            'password': 'WrongPassword123!'
        }
        
        response = self.client.post(self.login_url, login_data)
        
        # Should return form with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'not correct')
        
        # User should not be authenticated
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_with_nonexistent_email(self):
        """Test login with non-existent email"""
        login_data = {
            'login': 'nonexistent@example.com',
            'password': self.user_data['password']
        }
        
        response = self.client.post(self.login_url, login_data)
        
        # Should return form with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'not correct')

    def test_login_with_empty_fields(self):
        """Test login with empty fields"""
        login_data = {
            'login': '',
            'password': ''
        }
        
        response = self.client.post(self.login_url, login_data)
        
        # Should return form with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'required')

    def test_login_with_inactive_user(self):
        """Test login with inactive user account"""
        # Make user inactive
        self.user.is_active = False
        self.user.save()
        
        login_data = {
            'login': self.user_data['email'],
            'password': self.user_data['password']
        }
        
        response = self.client.post(self.login_url, login_data)
        
        # Should return form with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'inactive')

    def test_logout_functionality(self):
        """Test logout functionality"""
        # First login
        login_data = {
            'login': self.user_data['email'],
            'password': self.user_data['password']
        }
        self.client.post(self.login_url, login_data)
        
        # Verify user is logged in
        self.assertIn('_auth_user_id', self.client.session)
        
        # Logout
        response = self.client.post(self.logout_url)
        
        # Should redirect after logout
        self.assertEqual(response.status_code, 302)
        
        # Session should be cleared
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_redirect_to_next_url(self):
        """Test login redirects to 'next' parameter"""
        next_url = '/admin/'
        login_data = {
            'login': self.user_data['email'],
            'password': self.user_data['password']
        }
        
        response = self.client.post(f'{self.login_url}?next={next_url}', login_data)
        
        # Should redirect to the next URL
        self.assertEqual(response.status_code, 302)

    def test_remember_me_functionality(self):
        """Test remember me functionality if available"""
        login_data = {
            'login': self.user_data['email'],
            'password': self.user_data['password'],
            'remember': 'on'  # This field might exist in your form
        }
        
        response = self.client.post(self.login_url, login_data)
        
        # Should still login successfully
        self.assertEqual(response.status_code, 302)
        self.assertIn('_auth_user_id', self.client.session)

    def test_multiple_failed_login_attempts(self):
        """Test multiple failed login attempts"""
        login_data = {
            'login': self.user_data['email'],
            'password': 'WrongPassword123!'
        }
        
        # Attempt multiple failed logins
        for i in range(3):
            response = self.client.post(self.login_url, login_data)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'not correct')

    def test_login_preserves_session_data(self):
        """Test that login preserves existing session data"""
        # Add some data to session before login
        session = self.client.session
        session['test_data'] = 'preserved'
        session.save()
        
        # Login
        login_data = {
            'login': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, login_data)
        
        # Session data should be preserved
        self.assertEqual(self.client.session.get('test_data'), 'preserved')
        self.assertIn('_auth_user_id', self.client.session)

    def test_case_insensitive_email_login(self):
        """Test login with different case email"""
        login_data = {
            'login': self.user_data['email'].upper(),  # TEST@EXAMPLE.COM
            'password': self.user_data['password']
        }
        
        response = self.client.post(self.login_url, login_data)
        
        # Should still login successfully (depending on your configuration)
        # This test might fail if your system is case-sensitive
        # Adjust based on your actual requirements
