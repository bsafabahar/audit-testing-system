"""
اسکریپت تست سریع template
"""
import sys
from pathlib import Path

# اضافه کردن مسیر به sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from web_ui import get_audit_tests_with_custom

tests = get_audit_tests_with_custom()

print("\n" + "="*60)
print("بررسی داده‌های ارسالی به template")
print("="*60)

# بررسی اینکه custom موجود است
has_custom = 'custom' in tests
print(f"\n✅ آیا 'custom' در audit_tests موجود است؟ {has_custom}")

if has_custom:
    print(f"✅ نام دسته: {tests['custom']['name']}")
    print(f"✅ تعداد آزمون‌ها: {len(tests['custom']['tests'])}")
    
    # بررسی Jinja2 condition
    print(f"\n✅ audit_tests.get('custom') = {tests.get('custom')}")
    print(f"✅ این در Jinja2 به True تبدیل می‌شود")
    
    print("\n📋 لیست آزمون‌ها:")
    for i, test in enumerate(tests['custom']['tests'], 1):
        print(f"  {i}. {test['name']}")
        print(f"     ID: {test['id']}")
        print(f"     Icon: {test['icon']}")
else:
    print("\n❌ دسته custom موجود نیست!")
    print("❌ شرط {% if audit_tests.get('custom') %} False می‌شود")
    print("❌ بخش else نمایش داده می‌شود")

print("\n" + "="*60)
print("نتیجه:")
print("="*60)

if has_custom and len(tests['custom']['tests']) > 0:
    print("✅ همه چیز صحیح است - آزمون‌ها باید نمایش داده شوند")
    print("\n💡 اگر در صفحه نمایش داده نمی‌شوند:")
    print("   1. Cache مرورگر را پاک کنید (Ctrl + Shift + Delete)")
    print("   2. صفحه را با Ctrl + F5 رفرش کنید")
    print("   3. Developer Console (F12) را باز کنید و پیام‌های console را ببینید")
else:
    print("❌ مشکلی در backend وجود دارد")

print("\n")
