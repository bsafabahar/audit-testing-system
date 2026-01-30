"""
اسکریپت دیباگ برای بررسی get_audit_tests_with_custom
"""
import sys
from pathlib import Path

# اضافه کردن مسیر به sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import function
from web_ui import get_audit_tests_with_custom

print("Testing get_audit_tests_with_custom()...")
tests = get_audit_tests_with_custom()

print(f"\nتعداد کل دسته‌بندی‌ها: {len(tests)}")
print(f"\nدسته‌بندی‌ها:")
for category_id, category in tests.items():
    test_count = len(category['tests'])
    print(f"  - {category_id}: {category['name']} ({test_count} آزمون)")
    
if 'custom' in tests:
    print(f"\n✅ دسته آزمون‌های شخصی موجود است!")
    print(f"تعداد آزمون‌های شخصی: {len(tests['custom']['tests'])}")
    print("\nآزمون‌های شخصی:")
    for test in tests['custom']['tests']:
        print(f"  - {test['name']}")
else:
    print("\n❌ دسته آزمون‌های شخصی یافت نشد!")
