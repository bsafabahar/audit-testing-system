"""
ایجاد یک کاربر تستی - مثال
"""
from auth import create_user

# ایجاد کاربر
user = create_user(
    username='test_user',
    email='test@example.com', 
    password='test123',
    full_name='کاربر تستی',
    is_admin=False
)

if user:
    print('✅ کاربر با موفقیت ایجاد شد!')
    print(f'نام کاربری: {user.username}')
    print(f'ایمیل: {user.email}')
    print(f'رمز عبور: test123')
    print(f'نقش: {"مدیر" if user.is_admin else "کاربر عادی"}')
else:
    print('❌ خطا: نام کاربری یا ایمیل قبلاً وجود دارد')
