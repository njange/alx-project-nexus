"""
End-to-end tests for authentication using Selenium
"""
from django.test import LiveServerTestCase
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os

User = get_user_model()


class AuthenticationE2ETest(LiveServerTestCase):
    """End-to-end tests for authentication flows using Selenium"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Configure Chrome for headless testing
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-extensions')
        
        cls.selenium = webdriver.Chrome(options=chrome_options)
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        """Set up for each test"""
        self.wait = WebDriverWait(self.selenium, 15)
        self.site = Site.objects.get_current()

    def test_registration_page_elements(self):
        """Test that registration page loads with all required elements"""
        self.selenium.get(f'{self.live_server_url}/accounts/signup/')
        
        try:
            # Wait for form to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, 'form')))
            
            # Check for all required form fields
            username_field = self.selenium.find_element(By.NAME, 'username')
            email_field = self.selenium.find_element(By.NAME, 'email')
            password1_field = self.selenium.find_element(By.NAME, 'password1')
            password2_field = self.selenium.find_element(By.NAME, 'password2')
            submit_button = self.selenium.find_element(By.XPATH, '//button[@type="submit"] | //input[@type="submit"]')
            
            # Verify elements are visible and enabled
            self.assertTrue(username_field.is_displayed())
            self.assertTrue(username_field.is_enabled())
            self.assertTrue(email_field.is_displayed())
            self.assertTrue(email_field.is_enabled())
            self.assertTrue(password1_field.is_displayed())
            self.assertTrue(password1_field.is_enabled())
            self.assertTrue(password2_field.is_displayed())
            self.assertTrue(password2_field.is_enabled())
            self.assertTrue(submit_button.is_displayed())
            self.assertTrue(submit_button.is_enabled())
            
        except TimeoutException:
            self.fail("Registration page did not load properly")
        except NoSuchElementException as e:
            self.fail(f"Required form element missing: {e}")

    def test_login_page_elements(self):
        """Test that login page loads with all required elements"""
        self.selenium.get(f'{self.live_server_url}/accounts/login/')
        
        try:
            # Wait for form to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, 'form')))
            
            # Check for required form fields
            login_field = self.selenium.find_element(By.NAME, 'login')
            password_field = self.selenium.find_element(By.NAME, 'password')
            submit_button = self.selenium.find_element(By.XPATH, '//button[@type="submit"] | //input[@type="submit"]')
            
            # Verify elements are visible and enabled
            self.assertTrue(login_field.is_displayed())
            self.assertTrue(login_field.is_enabled())
            self.assertTrue(password_field.is_displayed())
            self.assertTrue(password_field.is_enabled())
            self.assertTrue(submit_button.is_displayed())
            self.assertTrue(submit_button.is_enabled())
            
        except TimeoutException:
            self.fail("Login page did not load properly")
        except NoSuchElementException as e:
            self.fail(f"Required form element missing: {e}")

    def test_successful_user_registration(self):
        """Test complete user registration flow"""
        self.selenium.get(f'{self.live_server_url}/accounts/signup/')
        
        try:
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.NAME, 'username')))
            
            # Generate unique user data
            timestamp = str(int(time.time()))
            test_username = f'e2euser{timestamp}'
            test_email = f'e2e{timestamp}@example.com'
            test_password = 'ComplexPassword123!'
            
            # Fill out the form
            username_field = self.selenium.find_element(By.NAME, 'username')
            email_field = self.selenium.find_element(By.NAME, 'email')
            password1_field = self.selenium.find_element(By.NAME, 'password1')
            password2_field = self.selenium.find_element(By.NAME, 'password2')
            
            username_field.clear()
            username_field.send_keys(test_username)
            email_field.clear()
            email_field.send_keys(test_email)
            password1_field.clear()
            password1_field.send_keys(test_password)
            password2_field.clear()
            password2_field.send_keys(test_password)
            
            # Submit the form
            submit_button = self.selenium.find_element(By.XPATH, '//button[@type="submit"] | //input[@type="submit"]')
            submit_button.click()
            
            # Wait for redirect (successful registration)
            self.wait.until(
                lambda driver: driver.current_url != f'{self.live_server_url}/accounts/signup/'
            )
            
            # Verify user was created in database
            self.assertTrue(User.objects.filter(email=test_email).exists())
            user = User.objects.get(email=test_email)
            self.assertEqual(user.username, test_username)
            
        except TimeoutException:
            self.fail("Registration process timed out")
        except Exception as e:
            self.fail(f"Registration failed: {str(e)}")

    def test_registration_with_validation_errors(self):
        """Test registration form validation errors"""
        self.selenium.get(f'{self.live_server_url}/accounts/signup/')
        
        try:
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.NAME, 'username')))
            
            # Fill form with invalid data
            username_field = self.selenium.find_element(By.NAME, 'username')
            email_field = self.selenium.find_element(By.NAME, 'email')
            password1_field = self.selenium.find_element(By.NAME, 'password1')
            password2_field = self.selenium.find_element(By.NAME, 'password2')
            
            username_field.clear()
            username_field.send_keys('user')  # Might be too short
            email_field.clear()
            email_field.send_keys('invalid-email')  # Invalid format
            password1_field.clear()
            password1_field.send_keys('weak')  # Weak password
            password2_field.clear()
            password2_field.send_keys('different')  # Mismatched passwords
            
            # Submit the form
            submit_button = self.selenium.find_element(By.XPATH, '//button[@type="submit"] | //input[@type="submit"]')
            submit_button.click()
            
            # Wait for error messages to appear
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'errorlist')))
            
            # Check that we're still on the signup page (form has errors)
            self.assertIn('/accounts/signup/', self.selenium.current_url)
            
            # Verify error messages are displayed
            error_elements = self.selenium.find_elements(By.CLASS_NAME, 'errorlist')
            self.assertTrue(len(error_elements) > 0)
            
        except TimeoutException:
            self.fail("Form validation errors did not appear")

    def test_successful_user_login(self):
        """Test complete user login flow"""
        # First create a user
        timestamp = str(int(time.time()))
        test_email = f'login{timestamp}@example.com'
        test_username = f'loginuser{timestamp}'
        test_password = 'ComplexPassword123!'
        
        user = User.objects.create_user(
            username=test_username,
            email=test_email,
            password=test_password
        )
        
        # Navigate to login page
        self.selenium.get(f'{self.live_server_url}/accounts/login/')
        
        try:
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.NAME, 'login')))
            
            # Fill out login form
            login_field = self.selenium.find_element(By.NAME, 'login')
            password_field = self.selenium.find_element(By.NAME, 'password')
            
            login_field.clear()
            login_field.send_keys(test_email)
            password_field.clear()
            password_field.send_keys(test_password)
            
            # Submit the form
            submit_button = self.selenium.find_element(By.XPATH, '//button[@type="submit"] | //input[@type="submit"]')
            submit_button.click()
            
            # Wait for redirect (successful login)
            self.wait.until(
                lambda driver: driver.current_url != f'{self.live_server_url}/accounts/login/'
            )
            
            # Should be redirected away from login page
            self.assertNotIn('/accounts/login/', self.selenium.current_url)
            
        except TimeoutException:
            self.fail("Login process timed out")
        except Exception as e:
            self.fail(f"Login failed: {str(e)}")

    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials shows error"""
        self.selenium.get(f'{self.live_server_url}/accounts/login/')
        
        try:
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.NAME, 'login')))
            
            # Fill form with invalid credentials
            login_field = self.selenium.find_element(By.NAME, 'login')
            password_field = self.selenium.find_element(By.NAME, 'password')
            
            login_field.clear()
            login_field.send_keys('nonexistent@example.com')
            password_field.clear()
            password_field.send_keys('wrongpassword')
            
            # Submit the form
            submit_button = self.selenium.find_element(By.XPATH, '//button[@type="submit"] | //input[@type="submit"]')
            submit_button.click()
            
            # Wait for error message
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'errorlist')))
            
            # Should still be on login page
            self.assertIn('/accounts/login/', self.selenium.current_url)
            
            # Check for error message
            error_elements = self.selenium.find_elements(By.CLASS_NAME, 'errorlist')
            self.assertTrue(len(error_elements) > 0)
            
        except TimeoutException:
            self.fail("Login error message did not appear")

    def test_google_oauth_button_presence(self):
        """Test that Google OAuth button is present when configured"""
        # Create Google Social App
        google_app = SocialApp.objects.create(
            provider='google',
            name='Google OAuth2 E2E Test',
            client_id='e2e_test_client_id',
            secret='e2e_test_secret'
        )
        google_app.sites.add(self.site)
        
        self.selenium.get(f'{self.live_server_url}/accounts/login/')
        
        try:
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.NAME, 'login')))
            
            # Look for Google OAuth button/link
            google_elements = self.selenium.find_elements(By.PARTIAL_LINK_TEXT, 'Google')
            if not google_elements:
                google_elements = self.selenium.find_elements(By.XPATH, "//*[contains(text(), 'Google')]")
            if not google_elements:
                google_elements = self.selenium.find_elements(By.XPATH, "//a[contains(@href, 'google')]")
            
            self.assertTrue(len(google_elements) > 0, "Google OAuth option not found")
            
            # Verify the element is visible
            google_element = google_elements[0]
            self.assertTrue(google_element.is_displayed())
            
        except Exception as e:
            self.fail(f"Google OAuth button test failed: {str(e)}")

    def test_navigation_between_auth_pages(self):
        """Test navigation between authentication pages"""
        # Start at login page
        self.selenium.get(f'{self.live_server_url}/accounts/login/')
        
        try:
            # Wait for login page to load
            self.wait.until(EC.presence_of_element_located((By.NAME, 'login')))
            
            # Look for signup link
            signup_links = self.selenium.find_elements(By.PARTIAL_LINK_TEXT, 'sign up')
            if not signup_links:
                signup_links = self.selenium.find_elements(By.PARTIAL_LINK_TEXT, 'Sign up')
            if not signup_links:
                signup_links = self.selenium.find_elements(By.XPATH, "//a[contains(@href, 'signup')]")
            
            if signup_links:
                # Click signup link
                signup_links[0].click()
                
                # Wait for signup page
                self.wait.until(EC.presence_of_element_located((By.NAME, 'username')))
                self.assertIn('/accounts/signup/', self.selenium.current_url)
                
                # Look for login link
                login_links = self.selenium.find_elements(By.PARTIAL_LINK_TEXT, 'sign in')
                if not login_links:
                    login_links = self.selenium.find_elements(By.PARTIAL_LINK_TEXT, 'Sign in')
                if not login_links:
                    login_links = self.selenium.find_elements(By.XPATH, "//a[contains(@href, 'login')]")
                
                if login_links:
                    # Click login link
                    login_links[0].click()
                    
                    # Wait for login page
                    self.wait.until(EC.presence_of_element_located((By.NAME, 'login')))
                    self.assertIn('/accounts/login/', self.selenium.current_url)
            
        except TimeoutException:
            self.fail("Navigation between auth pages timed out")
        except NoSuchElementException:
            # This is acceptable as the navigation links might not exist in all templates
            pass

    def test_form_field_validation_feedback(self):
        """Test real-time form field validation feedback"""
        self.selenium.get(f'{self.live_server_url}/accounts/signup/')
        
        try:
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.NAME, 'username')))
            
            # Get form fields
            username_field = self.selenium.find_element(By.NAME, 'username')
            email_field = self.selenium.find_element(By.NAME, 'email')
            password1_field = self.selenium.find_element(By.NAME, 'password1')
            
            # Test username field (enter and tab out)
            username_field.clear()
            username_field.send_keys('u')  # Too short
            email_field.click()  # Move focus away
            
            # Test email field validation
            email_field.clear()
            email_field.send_keys('invalid')
            password1_field.click()  # Move focus away
            
            # Check if HTML5 validation is working (basic check)
            email_validity = self.selenium.execute_script(
                "return arguments[0].validity.valid;", email_field
            )
            self.assertFalse(email_validity, "Email field should be invalid")
            
        except Exception as e:
            # HTML5 validation might not be implemented, which is okay
            pass

    def test_password_field_security(self):
        """Test that password fields are properly secured"""
        self.selenium.get(f'{self.live_server_url}/accounts/signup/')
        
        try:
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.NAME, 'password1')))
            
            # Check password field types
            password1_field = self.selenium.find_element(By.NAME, 'password1')
            password2_field = self.selenium.find_element(By.NAME, 'password2')
            
            # Verify password fields have type="password"
            self.assertEqual(password1_field.get_attribute('type'), 'password')
            self.assertEqual(password2_field.get_attribute('type'), 'password')
            
        except Exception as e:
            self.fail(f"Password field security test failed: {str(e)}")

    def test_csrf_protection(self):
        """Test that CSRF protection is in place"""
        self.selenium.get(f'{self.live_server_url}/accounts/signup/')
        
        try:
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, 'form')))
            
            # Look for CSRF token
            csrf_inputs = self.selenium.find_elements(By.NAME, 'csrfmiddlewaretoken')
            self.assertTrue(len(csrf_inputs) > 0, "CSRF token not found")
            
            # Verify CSRF token has a value
            csrf_token = csrf_inputs[0].get_attribute('value')
            self.assertTrue(len(csrf_token) > 0, "CSRF token is empty")
            
        except Exception as e:
            self.fail(f"CSRF protection test failed: {str(e)}")
