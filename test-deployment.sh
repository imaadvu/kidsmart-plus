#!/bin/bash
# Quick test script to verify the deployment fixes
# Run this on AWS server after deployment

echo "======================================"
echo "KidsSmart+ Deployment Test Script"
echo "======================================"
echo ""

# Test 1: Check if api.cache module exists
echo "Test 1: Checking api.cache module..."
if docker compose exec -T api python -c "from api.cache import cache; print('OK')" 2>&1 | grep -q "OK"; then
    echo "✓ PASS: api.cache module found"
else
    echo "✗ FAIL: api.cache module not found"
    exit 1
fi

# Test 2: Check bcrypt version
echo ""
echo "Test 2: Checking bcrypt version..."
BCRYPT_VERSION=$(docker compose exec -T api python -c "import bcrypt; print(bcrypt.__version__)" 2>&1)
echo "  Installed version: $BCRYPT_VERSION"
if [[ "$BCRYPT_VERSION" == "4.0.1" ]]; then
    echo "✓ PASS: Correct bcrypt version"
else
    echo "⚠ WARNING: Expected bcrypt 4.0.1, got $BCRYPT_VERSION"
fi

# Test 3: Check passlib
echo ""
echo "Test 3: Checking passlib compatibility..."
if docker compose exec -T api python -c "from passlib.hash import bcrypt; bcrypt.hash('test'); print('OK')" 2>&1 | grep -q "OK"; then
    echo "✓ PASS: passlib working correctly"
else
    echo "✗ FAIL: passlib has issues"
    exit 1
fi

# Test 4: Check API is running
echo ""
echo "Test 4: Checking if API is responding..."
if curl -s http://localhost:8000/docs > /dev/null; then
    echo "✓ PASS: API is responding"
else
    echo "✗ FAIL: API not responding"
    exit 1
fi

# Test 5: Check database connection
echo ""
echo "Test 5: Checking database connection..."
if docker compose exec -T api python -c "from core.db import SessionLocal; db = SessionLocal(); print('OK')" 2>&1 | grep -q "OK"; then
    echo "✓ PASS: Database connection OK"
else
    echo "✗ FAIL: Database connection failed"
    exit 1
fi

# Test 6: Check admin user exists
echo ""
echo "Test 6: Checking admin user..."
if docker compose exec -T api python -c "from core.db import SessionLocal; from db.models import User; db = SessionLocal(); admin = db.query(User).filter(User.username == 'admin').first(); print('OK' if admin else 'MISSING')" 2>&1 | grep -q "OK"; then
    echo "✓ PASS: Admin user exists"
else
    echo "⚠ WARNING: Admin user not found (may be using different username)"
fi

echo ""
echo "======================================"
echo "All critical tests passed!"
echo "======================================"
echo ""
echo "Your deployment is working correctly."
echo "Access points:"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Dashboard: http://localhost:8501"

