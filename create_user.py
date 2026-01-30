"""
اسکریپت ایجاد کاربر جدید
برای ایجاد کاربران به صورت دستی استفاده کنید
"""

from auth import create_user
from database import db

def create_new_user():
    """ایجاد کاربر جدید با دریافت اطلاعات از کاربر"""
    
    # مقداردهی اولیه دیتابیس
    if not db._initialized:
        db._initialize()
    
    print("=" * 50)
    print("ایجاد کاربر جدید")
    print("=" * 50)
    
    # دریافت اطلاعات
    username = input("\nنام کاربری (انگلیسی، بدون فاصله): ")
    email = input("ایمیل: ")
    full_name = input("نام کامل (اختیاری): ")
    password = input("رمز عبور (حداقل 6 کاراکتر): ")
    
    # تایید رمز عبور
    password_confirm = input("تکرار رمز عبور: ")
    
    if password != password_confirm:
        print("\n❌ خطا: رمز عبور و تکرار آن یکسان نیستند!")
        return
    
    if len(password) < 6:
        print("\n❌ خطا: رمز عبور باید حداقل 6 کاراکتر باشد!")
        return
    
    # سوال برای دسترسی ادمین
    is_admin_input = input("\nآیا این کاربر مدیر سیستم باشد؟ (y/n) [n]: ").lower()
    is_admin = is_admin_input == 'y' or is_admin_input == 'yes'
    
    # ایجاد کاربر
    print("\nدر حال ایجاد کاربر...")
    user = create_user(
        username=username,
        email=email,
        password=password,
        full_name=full_name,
        is_admin=is_admin
    )
    
    if user:
        print("\n" + "=" * 50)
        print("✅ کاربر با موفقیت ایجاد شد!")
        print("=" * 50)
        print(f"\nنام کاربری: {user.username}")
        print(f"ایمیل: {user.email}")
        print(f"نام کامل: {user.full_name or '-'}")
        print(f"نقش: {'مدیر سیستم' if user.is_admin else 'کاربر عادی'}")
        print(f"\n🔑 اکنون می‌توانید با این اطلاعات وارد شوید:")
        print(f"   نام کاربری: {username}")
        print(f"   رمز عبور: {password}")
    else:
        print("\n❌ خطا: نام کاربری یا ایمیل قبلاً استفاده شده است!")


if __name__ == '__main__':
    try:
        create_new_user()
    except KeyboardInterrupt:
        print("\n\n❌ عملیات لغو شد.")
    except Exception as e:
        print(f"\n❌ خطا: {e}")
