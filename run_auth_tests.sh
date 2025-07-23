#!/bin/bash
# Quick test runner for authentication tests

echo "🧪 Quick Authentication Test Runner"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Run the tests
python scripts/test_auth.py --quick

echo "Done!"
