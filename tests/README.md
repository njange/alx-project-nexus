# Authentication Test Suite

This directory contains comprehensive automated tests for the Django authentication system including user registration, login, and Google OAuth functionality.

## Test Structure

```
tests/
├── conftest.py                 # Pytest configuration and fixtures
├── unit/                       # Unit tests
│   ├── test_registration.py    # User registration tests
│   ├── test_login.py           # User login tests
│   └── test_google_oauth.py    # Google OAuth tests
├── integration/                # Integration tests
│   └── test_auth_flows.py      # Complete authentication flow tests
└── e2e/                       # End-to-end tests
    └── test_auth_e2e.py        # Selenium-based E2E tests
```

## Running Tests

### Quick Start
```bash
# Run all authentication tests
python scripts/test_auth.py --quick

# Run specific test categories
python scripts/test_auth.py --registration
python scripts/test_auth.py --login
python scripts/test_auth.py --oauth
python scripts/test_auth.py --integration

# Run with coverage
python scripts/test_auth.py --coverage
```

### Using Django Test Runner
```bash
# Registration tests
python manage.py test tests.unit.test_registration -v 2

# Login tests  
python manage.py test tests.unit.test_login -v 2

# Google OAuth tests
python manage.py test tests.unit.test_google_oauth -v 2

# Integration tests
python manage.py test tests.integration.test_auth_flows -v 2

# E2E tests (requires Chrome)
python manage.py test tests.e2e.test_auth_e2e -v 2
```

### Using Pytest
```bash
# All tests
pytest tests/ -v

# Specific categories
pytest tests/unit/test_registration.py -v
pytest tests/unit/test_login.py -v
pytest tests/unit/test_google_oauth.py -v

# With markers
pytest tests/ -m registration -v
pytest tests/ -m login -v
pytest tests/ -m oauth -v
```

## Test Categories

### 1. Registration Tests (`test_registration.py`)
- ✅ Registration page loads correctly
- ✅ Valid user registration
- ✅ Duplicate email validation
- ✅ Password strength validation
- ✅ Form field validation
- ✅ UUID primary key generation
- ✅ User creation with correct defaults

### 2. Login Tests (`test_login.py`)
- ✅ Login page loads correctly
- ✅ Valid login with email/username
- ✅ Invalid credentials handling
- ✅ Empty fields validation
- ✅ Inactive user handling
- ✅ Session management
- ✅ Logout functionality
- ✅ Redirect to next URL

### 3. Google OAuth Tests (`test_google_oauth.py`)
- ✅ OAuth without configuration (error handling)
- ✅ OAuth with proper configuration
- ✅ Social app creation and validation
- ✅ Social account creation
- ✅ Login page OAuth integration
- ✅ Multiple provider handling

### 4. Integration Tests (`test_auth_flows.py`)
- ✅ Complete registration → login flow
- ✅ Duplicate email prevention
- ✅ Login → logout → login cycle
- ✅ Password reset initiation
- ✅ Google OAuth configuration flow
- ✅ Authentication redirects
- ✅ Session persistence
- ✅ Form validation persistence

### 5. E2E Tests (`test_auth_e2e.py`)
- ✅ Registration page UI elements
- ✅ Login page UI elements
- ✅ Complete registration workflow
- ✅ Registration form validation
- ✅ Complete login workflow
- ✅ Invalid login error display
- ✅ Google OAuth button presence
- ✅ Page navigation
- ✅ CSRF protection
- ✅ Password field security

## Prerequisites

### For Unit/Integration Tests
```bash
pip install django pytest pytest-django coverage
```

### For E2E Tests (Additional)
```bash
# Install Chrome browser
# Download ChromeDriver or use selenium-manager
pip install selenium
```

## Configuration

### Test Settings
Tests use optimized settings for speed and isolation:
- In-memory SQLite database
- Local memory email backend
- MD5 password hasher (faster)
- Disabled email verification

### Environment Variables
```bash
export DJANGO_SETTINGS_MODULE=app.settings
```

### Google OAuth Testing
For Google OAuth tests, the system creates mock Social Applications. Real OAuth testing requires:
1. Google Cloud Console project
2. OAuth 2.0 credentials
3. Proper redirect URIs configured

## Coverage

Generate coverage reports:
```bash
python scripts/test_auth.py --coverage
# Opens htmlcov/index.html
```

Expected coverage areas:
- User model custom methods
- Authentication views
- Form validation
- Social authentication integration

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Run Authentication Tests
  run: |
    python scripts/test_auth.py --quick
    python scripts/test_auth.py --coverage
```

### Pre-commit Hook
```bash
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: auth-tests
      name: Authentication Tests
      entry: python scripts/test_auth.py --quick
      language: system
      pass_filenames: false
```

## Troubleshooting

### Common Issues

1. **E2E Tests Failing**
   - Ensure Chrome browser is installed
   - Check ChromeDriver compatibility
   - Verify headless mode works

2. **Google OAuth Tests**
   - Mock configurations are used in tests
   - Real OAuth requires actual Google credentials

3. **Database Issues**
   - Tests use separate in-memory database
   - No impact on development data

4. **Import Errors**
   - Ensure Django apps are in INSTALLED_APPS
   - Check Python path configuration

### Debug Mode
```bash
# Run with verbose output
python manage.py test tests.unit.test_registration -v 3

# Run single test method
python manage.py test tests.unit.test_registration.UserRegistrationUnitTest.test_valid_user_registration -v 2
```

## Contributing

When adding new authentication features:

1. Add unit tests for individual components
2. Add integration tests for workflows
3. Add E2E tests for user interactions
4. Update this README with new test categories
5. Ensure all tests pass before submitting PRs

## Performance

Test execution times (approximate):
- Unit tests: ~10-15 seconds
- Integration tests: ~15-20 seconds  
- E2E tests: ~30-60 seconds
- Full suite: ~1-2 minutes

For faster development cycles, use `--quick` which skips E2E tests.
