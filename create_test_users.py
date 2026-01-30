"""
اسکریپت تست سیستم احراز هویت
این اسکریپت برای ایجاد کاربران تستی استفاده می‌شود
"""

from auth import create_user
from database import db

def create_test_users():
    """ایجاد کاربران تستی"""
    
    # مقداردهی اولیه دیتابیس
    if not db._initialized:
        db._initialize()
    
    # لیست کاربران تستی
    test_users = [
        {
            'username': 'user1',
            'email': 'user1@test.com',
            'password': 'user123',
            'full_name': 'کاربر تستی یک',
            'is_admin': False
        },
        {
            'username': 'user2',
            'email': 'user2@test.com',
            'password': 'user123',
            'full_name': 'کاربر تستی دو',
            'is_admin': False
        },
        {
            'username': 'auditor',
            'email': 'auditor@test.com',
            'password': 'auditor123',
            'full_name': 'حسابرس ارشد',
            'is_admin': False
        },
    ]
    
    print("ایجاد کاربران تستی...")
    print("-" * 50)
    
    for user_data in test_users:
        user = create_user(**user_data)
        if user:
            print(f"✓ کاربر '{user.username}' با موفقیت ایجاد شد")
            print(f"  ایمیل: {user.email}")
            print(f"  نقش: {'مدیر' if user.is_admin else 'کاربر عادی'}")
        else:
            print(f"✗ خطا در ایجاد کاربر '{user_data['username']}' (احتمالاً قبلاً وجود دارد)")
        print("-" * 50)
    
    print("\nکاربران تستی ایجاد شدند!")
    print("\nاطلاعات ورود:")
    print("  نام کاربری: user1, user2, auditor")
    print("  رمز عبور: user123 یا auditor123")


if __name__ == '__main__':
    create_test_users()
