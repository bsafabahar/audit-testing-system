#!/usr/bin/env python
"""
تست ساده برای ماژول test_generator
Simple test for test_generator module
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_generator import extract_test_name, TEST_GENERATION_PROMPT_TEMPLATE


def test_extract_test_name():
    """تست استخراج نام آزمون از کد"""
    
    # کد نمونه
    sample_code = '''"""
آزمون تراکنش‌های مشکوک
Suspicious Transactions Test

این آزمون تراکنش‌های مشکوک را شناسایی می‌کند.
"""
from typing import List, Dict, Any
'''
    
    name = extract_test_name(sample_code)
    print(f"✓ نام استخراج شده: {name}")
    assert name is not None
    assert name.endswith("_test")
    print("✓ تست استخراج نام موفق بود")


def test_prompt_template():
    """تست قالب پرامپت"""
    
    user_desc = "یک آزمون ساده برای تست"
    prompt = TEST_GENERATION_PROMPT_TEMPLATE.format(user_description=user_desc)
    
    # بررسی اینکه توضیح کاربر در پرامپت قرار گرفته
    assert user_desc in prompt
    print("✓ قالب پرامپت به درستی کار می‌کند")
    
    # بررسی وجود بخش‌های کلیدی
    assert "بخش 1: METADATA و NAMING" in prompt
    assert "بخش 2: DOCSTRING هدر" in prompt
    assert "بخش 3: IMPORTS" in prompt
    assert "define()" in prompt
    assert "execute()" in prompt
    print("✓ تمام بخش‌های کلیدی در پرامپت موجود است")


if __name__ == "__main__":
    print("🧪 شروع تست‌های ماژول test_generator...\n")
    
    try:
        test_extract_test_name()
        print()
        test_prompt_template()
        print("\n✅ همه تست‌ها با موفقیت انجام شد!")
    except AssertionError as e:
        print(f"\n❌ خطا در تست: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ خطای غیرمنتظره: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
