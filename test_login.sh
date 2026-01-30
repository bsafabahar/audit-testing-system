#!/bin/bash
# تست لاگین سیستم

echo "=== Testing Login System ==="

# Test 1: صفحه لاگین
echo -n "1. Testing login page... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/login)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ OK (200)"
else
    echo "✗ FAIL ($HTTP_CODE)"
fi

# Test 2: Redirect به لاگین
echo -n "2. Testing redirect to login... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)
if [ "$HTTP_CODE" = "302" ]; then
    echo "✓ OK (302)"
else
    echo "✗ FAIL ($HTTP_CODE)"
fi

# Test 3: لاگین واقعی
echo -n "3. Testing actual login... "
HTTP_CODE=$(curl -s -o /tmp/login_result.html -w "%{http_code}" \
    -c /tmp/test_cookies.txt \
    -d "username=admin&password=admin123" \
    -X POST \
    http://localhost:8000/login)
    
if [ "$HTTP_CODE" = "302" ]; then
    echo "✓ OK (302 - redirect after login)"
elif [ "$HTTP_CODE" = "200" ]; then
    if grep -q "خوش آمدید\|success" /tmp/login_result.html; then
        echo "✓ OK (200 - successful login)"
    else
        echo "✗ FAIL (200 but no success message)"
    fi
else
    echo "✗ FAIL ($HTTP_CODE)"
fi

# Test 4: دسترسی به صفحه اصلی با کوکی
echo -n "4. Testing access with cookie... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -b /tmp/test_cookies.txt \
    http://localhost:8000/)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ OK (200)"
else
    echo "✗ FAIL ($HTTP_CODE)"
fi

echo ""
echo "=== Test Complete ==="

# Cleanup
rm -f /tmp/test_cookies.txt /tmp/login_result.html
