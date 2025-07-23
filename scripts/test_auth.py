"""
Test runner script for authentication tests
"""
#!/usr/bin/env python
import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*50}")
    print(f"🚀 {description}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(command, shell=True, check=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False


def setup_test_environment():
    """Set up test environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
    
    print("🔧 Setting up test environment...")
    
    # Create test database
    if run_command('python manage.py migrate --run-syncdb', 'Database Migration'):
        print("✅ Test database ready")
    
    return True


def run_registration_tests():
    """Run registration-specific tests"""
    return run_command(
        'python manage.py test tests.unit.test_registration -v 2',
        'User Registration Tests'
    )


def run_login_tests():
    """Run login-specific tests"""
    return run_command(
        'python manage.py test tests.unit.test_login -v 2',
        'User Login Tests'
    )


def run_google_oauth_tests():
    """Run Google OAuth tests"""
    return run_command(
        'python manage.py test tests.unit.test_google_oauth -v 2',
        'Google OAuth Tests'
    )


def run_integration_tests():
    """Run integration tests"""
    return run_command(
        'python manage.py test tests.integration.test_auth_flows -v 2',
        'Authentication Integration Tests'
    )


def run_e2e_tests():
    """Run end-to-end tests"""
    print("⚠️  E2E tests require Chrome browser to be installed")
    return run_command(
        'python manage.py test tests.e2e.test_auth_e2e -v 2',
        'End-to-End Authentication Tests'
    )


def run_all_auth_tests():
    """Run all authentication tests"""
    return run_command(
        'python manage.py test tests.unit tests.integration -v 2',
        'All Authentication Tests (Unit + Integration)'
    )


def run_coverage_tests():
    """Run tests with coverage"""
    commands = [
        'coverage erase',
        'coverage run --source=. manage.py test tests.unit tests.integration',
        'coverage report --include="users/*,app/*" --omit="*/migrations/*,*/tests/*"',
        'coverage html --include="users/*,app/*" --omit="*/migrations/*,*/tests/*"'
    ]
    
    for cmd in commands:
        if not run_command(cmd, f'Coverage: {cmd}'):
            return False
    
    print("\n📊 Coverage report generated in htmlcov/index.html")
    return True


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description='Authentication Test Runner')
    parser.add_argument('--registration', action='store_true', help='Run registration tests only')
    parser.add_argument('--login', action='store_true', help='Run login tests only')
    parser.add_argument('--oauth', action='store_true', help='Run Google OAuth tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--e2e', action='store_true', help='Run E2E tests only')
    parser.add_argument('--all', action='store_true', help='Run all authentication tests')
    parser.add_argument('--coverage', action='store_true', help='Run tests with coverage')
    parser.add_argument('--quick', action='store_true', help='Run quick tests (unit + integration)')
    
    args = parser.parse_args()
    
    print("🧪 Authentication Test Suite")
    print("=" * 50)
    
    # Setup environment
    if not setup_test_environment():
        print("❌ Environment setup failed")
        sys.exit(1)
    
    results = {}
    
    # Run specific test types based on arguments
    if args.registration:
        results['registration'] = run_registration_tests()
    
    if args.login:
        results['login'] = run_login_tests()
    
    if args.oauth:
        results['oauth'] = run_google_oauth_tests()
    
    if args.integration:
        results['integration'] = run_integration_tests()
    
    if args.e2e:
        results['e2e'] = run_e2e_tests()
    
    if args.all:
        results['registration'] = run_registration_tests()
        results['login'] = run_login_tests()
        results['oauth'] = run_google_oauth_tests()
        results['integration'] = run_integration_tests()
        results['e2e'] = run_e2e_tests()
    
    if args.coverage:
        results['coverage'] = run_coverage_tests()
    
    if args.quick or not any([args.registration, args.login, args.oauth, args.integration, args.e2e, args.all, args.coverage]):
        # Default: run quick tests
        results['registration'] = run_registration_tests()
        results['login'] = run_login_tests()
        results['oauth'] = run_google_oauth_tests()
        results['integration'] = run_integration_tests()
    
    # Print summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    if not results:
        print("No tests were run")
        return
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    for test_type, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_type.upper()}: {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} test suites passed")
    
    if passed_tests == total_tests:
        print("🎉 All authentication tests passed!")
        sys.exit(0)
    else:
        print("💥 Some authentication tests failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()
