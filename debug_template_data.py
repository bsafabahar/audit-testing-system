"""
تست template rendering برای آزمون‌های شخصی
"""
import sys
from pathlib import Path

# اضافه کردن مسیر به sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from web_ui import get_audit_tests_with_custom

tests = get_audit_tests_with_custom()

print("=== Debug Template Data ===\n")
print(f"audit_tests.get('custom') = {tests.get('custom')}\n")

if tests.get('custom'):
    print("✅ custom دسته موجود است")
    print(f"نام: {tests['custom']['name']}")
    print(f"تعداد آزمون‌ها: {len(tests['custom']['tests'])}")
    print("\nآزمون‌ها:")
    for test in tests['custom']['tests']:
        print(f"  - id: {test['id']}")
        print(f"    name: {test['name']}")
        print(f"    icon: {test['icon']}")
else:
    print("❌ custom دسته موجود نیست")
