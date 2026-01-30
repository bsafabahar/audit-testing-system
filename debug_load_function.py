"""
اسکریپت دیباگ برای بررسی load_custom_tests
"""
import sys
from pathlib import Path

# اضافه کردن مسیر به sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import function
from web_ui import load_custom_tests

print("Testing load_custom_tests()...")
custom_tests = load_custom_tests()

print(f"\nتعداد آزمون‌های یافت شده: {len(custom_tests)}")
print(f"\nآزمون‌ها:")
for test in custom_tests:
    print(f"  - ID: {test['id']}")
    print(f"    نام: {test['name']}")
    print(f"    آیکون: {test['icon']}")
    print()
