"""
اسکریپت دیباگ برای تست تولید کد از AI
"""
import sys
from test_generator import generate_test_with_avalai, generate_test_with_anthropic

# تست با AvalAI
print("=" * 80)
print("Testing AvalAI...")
print("=" * 80)

api_key = "aa-7QZl0Ab58B13JYYTG5WCeOSq8UIJh5IgwpqNa6hZLgACOACf"
base_url = "https://api.avalai.ir/v1"
model = "claude-sonnet-4-5"
description = "یک آزمون ساده برای بررسی تراکنش‌های بیش از 10000 تومان"

try:
    result = generate_test_with_avalai(
        user_description=description,
        api_key=api_key,
        base_url=base_url,
        model=model,
        use_prompt=True  # استفاده از پرامپت کامل
    )
    
    if result:
        print("\n✅ تولید کد موفق بود!")
        print(f"طول کد: {len(result)} کاراکتر")
        print(f"100 کاراکتر اول:\n{result[:100]}")
    else:
        print("\n❌ تولید کد ناموفق بود!")
        
except Exception as e:
    print(f"\n❌ خطا رخ داد: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
