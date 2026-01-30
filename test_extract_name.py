"""
تست تابع extract_test_name
"""
import sys
from pathlib import Path

# اضافه کردن مسیر به sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from test_generator import extract_test_name

# تست با کد نمونه
test_code_1 = '''"""
آزمون تشخیص موجودی منفی
Negative Inventory Detection

این آزمون موجودی منفی را شناسایی می‌کند.
"""

from typing import List, Dict, Any
'''

test_code_2 = '''"""
تحلیل روند فروش ماهانه
Monthly Sales Trend Analysis

این آزمون روند فروش را بررسی می‌کند.
"""

from typing import List, Dict, Any
'''

test_code_3 = '''"""
تست شخصی
Custom Test

This is a test.
"""

from typing import List, Dict, Any
'''

print("="*60)
print("تست 1: آزمون موجودی منفی")
print("="*60)
result1 = extract_test_name(test_code_1)
print(f"نتیجه: {result1}")
print(f"انتظار: negative_inventory_detection_test")
print(f"✅ موفق" if result1 == "negative_inventory_detection_test" else "❌ ناموفق")

print("\n" + "="*60)
print("تست 2: تحلیل روند فروش")
print("="*60)
result2 = extract_test_name(test_code_2)
print(f"نتیجه: {result2}")
print(f"انتظار: monthly_sales_trend_analysis_test")
print(f"✅ موفق" if result2 == "monthly_sales_trend_analysis_test" else "❌ ناموفق")

print("\n" + "="*60)
print("تست 3: Custom Test (باید رد شود)")
print("="*60)
result3 = extract_test_name(test_code_3)
print(f"نتیجه: {result3}")
print(f"این نام قابل قبول نیست و باید از timestamp استفاده شود")
