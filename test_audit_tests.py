import sys
from pathlib import Path

# بارگذاری web_ui
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from web_ui import get_audit_tests_with_custom

print("=== تست get_audit_tests_with_custom ===")
audit_tests = get_audit_tests_with_custom()

print(f"\nتعداد دسته‌ها: {len(audit_tests)}")
print("\nنام دسته‌ها:")
for category_id, category_info in audit_tests.items():
    test_count = len(category_info.get('tests', []))
    print(f"  - {category_id}: {category_info.get('name', 'N/A')} ({test_count} آزمون)")

if 'custom' in audit_tests:
    print("\n=== آزمون‌های شخصی ===")
    for test in audit_tests['custom']['tests']:
        print(f"  - {test['id']}: {test['name']}")
else:
    print("\n❌ دسته custom وجود ندارد!")
