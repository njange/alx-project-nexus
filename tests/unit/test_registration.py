"""
Unit tests for user registration functionality
"""
import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import time

User = get_user_model()


class UserRegistrationUnitTest(TestCase):
    """Unit tests for user registration"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.registration_url = reverse('account_signup')
        self.valid_user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPassword123!',
            'password2': 'ComplexPassword123!'
        }

    def test_registration_page_loads(self):
        """Test that registration page loads correctly"""
        response = self.client.get(self.registration_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="email"')
        self.assertContains(response, 'name="password1"')
        self.assertContains(response, 'name="password2"')

    def test_valid_user_registration(self):
        """Test registration with valid data"""
        initial_user_count = User.objects.count()
        
        response = self.client.post(self.registration_url, self.valid_user_data)
        
        # Should redirect after successful registration
        self.assertEqual(response.status_code, 302)
        
        # Check user was created
        self.assertEqual(User.objects.count(), initial_user_count + 1)
        
        # Verify user details
        user = User.objects.get(email=self.valid_user_data['email'])
        self.assertEqual(user.username, self.valid_user_data['username'])
        self.assertEqual(user.email, self.valid_user_data['email'])
        self.assertTrue(user.check_password(self.valid_user_data['password1']))

    def test_registration_with_duplicate_email(self):
        """Test registration with already existing email"""
        # Create a user first
        User.objects.create_user(
            username='existinguser',
            email=self.valid_user_data['email'],
            password='ExistingPassword123!'
        )
        
        # Try to register with same email
        duplicate_data = self.valid_user_data.copy()
        duplicate_data['username'] = 'differentusername'
        
        response = self.client.post(self.registration_url, duplicate_data)
        
        # Should return form with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already exists')

    def test_registration_with_weak_password(self):
        """Test registration with weak password"""
        weak_password_data = self.valid_user_data.copy()
        weak_password_data['password1'] = 'weak'
        weak_password_data['password2'] = 'weak'
        
        response = self.client.post(self.registration_url, weak_password_data)
        
        # Should return form with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'password')

    def test_registration_with_mismatched_passwords(self):
        """Test registration with mismatched passwords"""
        mismatched_data = self.valid_user_data.copy()
        mismatched_data['password2'] = 'DifferentPassword123!'
        
        response = self.client.post(self.registration_url, mismatched_data)
        
        # Should return form with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'password')

    def test_registration_with_invalid_email(self):
        """Test registration with invalid email format"""
        invalid_email_data = self.valid_user_data.copy()
        invalid_email_data['email'] = 'invalid-email-format'
        
        response = self.client.post(self.registration_url, invalid_email_data)
        
        # Should return form with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'valid email')

    def test_registration_with_empty_fields(self):
        """Test registration with empty required fields"""
        empty_data = {
            'username': '',
            'email': '',
            'password1': '',
            'password2': ''
        }
        
        response = self.client.post(self.registration_url, empty_data)
        
        # Should return form with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'required')

    def test_registration_creates_user_with_uuid_id(self):
        """Test that registered user has UUID as primary key"""
        response = self.client.post(self.registration_url, self.valid_user_data)
        
        user = User.objects.get(email=self.valid_user_data['email'])
        
        # Check that ID is a UUID
        self.assertEqual(len(str(user.id)), 36)  # UUID length
        self.assertIn('-', str(user.id))  # UUID contains hyphens

    def test_registration_sets_correct_user_fields(self):
        """Test that registration sets correct user fields"""
        response = self.client.post(self.registration_url, self.valid_user_data)
        
        user = User.objects.get(email=self.valid_user_data['email'])
        
        # Check default field values
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertIsNotNone(user.date_created)

    def test_unique_username_registration(self):
        """Test registration with unique usernames"""
        timestamp = str(int(time.time()))
        
        # Register first user
        user_data_1 = self.valid_user_data.copy()
        user_data_1['username'] = f'user{timestamp}_1'
        user_data_1['email'] = f'user{timestamp}_1@example.com'
        
        response1 = self.client.post(self.registration_url, user_data_1)
        self.assertEqual(response1.status_code, 302)
        
        # Register second user with different username/email
        user_data_2 = self.valid_user_data.copy()
        user_data_2['username'] = f'user{timestamp}_2'
        user_data_2['email'] = f'user{timestamp}_2@example.com'
        
        response2 = self.client.post(self.registration_url, user_data_2)
        self.assertEqual(response2.status_code, 302)
        
        # Both users should exist
        self.assertTrue(User.objects.filter(username=user_data_1['username']).exists())
        self.assertTrue(User.objects.filter(username=user_data_2['username']).exists())
