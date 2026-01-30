#!/bin/bash
# تست کامل قابلیت‌های کاربری

echo "=== Testing User Management Features ==="
echo ""

# Test 1: لاگین و دریافت کوکی
echo -n "1. Login as admin... "
curl -s -c /tmp/admin_cookies.txt \
    -d "username=admin&password=admin123" \
    -X POST \
    http://localhost:8000/login > /dev/null

if [ -f /tmp/admin_cookies.txt ]; then
    echo "✓ OK"
else
    echo "✗ FAIL"
    exit 1
fi

# Test 2: دسترسی به صفحه افزودن کاربر
echo -n "2. Access add-user page... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -b /tmp/admin_cookies.txt \
    http://localhost:8000/add-user)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ OK (200)"
else
    echo "✗ FAIL ($HTTP_CODE)"
fi

# Test 3: افزودن کاربر جدید
echo -n "3. Create new user... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -b /tmp/admin_cookies.txt \
    -d "username=newuser2&email=newuser2@test.com&password=pass123&confirm_password=pass123&full_name=New User 2" \
    -X POST \
    http://localhost:8000/add-user)
if [ "$HTTP_CODE" = "302" ]; then
    echo "✓ OK (302 - redirect after creation)"
else
    echo "✗ FAIL ($HTTP_CODE)"
fi

# Test 4: دسترسی به صفحه تغییر رمز
echo -n "4. Access change-password page... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -b /tmp/admin_cookies.txt \
    http://localhost:8000/change-password)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ OK (200)"
else
    echo "✗ FAIL ($HTTP_CODE)"
fi

# Test 5: تغییر رمز عبور
echo -n "5. Change password... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -b /tmp/admin_cookies.txt \
    -d "old_password=admin123&new_password=admin123&confirm_password=admin123" \
    -X POST \
    http://localhost:8000/change-password)
if [ "$HTTP_CODE" = "302" ]; then
    echo "✓ OK (302 - password changed)"
else
    echo "✗ FAIL ($HTTP_CODE)"
fi

# Cleanup
rm -f /tmp/admin_cookies.txt

echo ""
echo "=== All Tests Complete ==="
