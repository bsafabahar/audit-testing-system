"""
تست مستقیم با مدل gpt-5-nano-2025-08-07
"""
from test_generator import generate_test_with_avalai

print("=" * 80)
print("Testing with gpt-5-nano-2025-08-07")
print("=" * 80)

api_key = "aa-7QZl0Ab58B13JYYTG5WCeOSq8UIJh5IgwpqNa6hZLgACOACf"
base_url = "https://api.avalai.ir/v1"
model = "gpt-5-nano-2025-08-07"  # مدلی که خطا داد
description = "یک آزمون ساده برای بررسی تراکنش‌های بیش از 10000 تومان"

print(f"\nپارامترها:")
print(f"  - Model: {model}")
print(f"  - Base URL: {base_url}")
print(f"  - Description: {description}")
print(f"  - Use Prompt: True")
print()

try:
    result = generate_test_with_avalai(
        user_description=description,
        api_key=api_key,
        base_url=base_url,
        model=model,
        use_prompt=True  # با پرامپت کامل
    )
    
    if result:
        print("\n✅ تولید کد موفق بود!")
        print(f"طول کد: {len(result)} کاراکتر")
        print(f"100 کاراکتر اول:\n{result[:100]}")
    else:
        print("\n❌ تولید کد ناموفق بود! (result = None)")
        print("این یعنی یکی از بررسی‌های زیر False برگرداند:")
        print("  1. response.choices خالی بود")
        print("  2. response.choices[0].message خالی بود")
        print("  3. response.choices[0].message.content خالی بود")
        print("  4. generated_content بعد از strip خالی بود")
        
except Exception as e:
    print(f"\n❌ خطا رخ داد: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
