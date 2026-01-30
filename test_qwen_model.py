"""
تست مدل cf.qwen2.5-coder-32b-instruct
"""
from test_generator import generate_test_with_avalai

print("=" * 80)
print("Testing cf.qwen2.5-coder-32b-instruct")
print("=" * 80)

api_key = "aa-7QZl0Ab58B13JYYTG5WCeOSq8UIJh5IgwpqNa6hZLgACOACf"
base_url = "https://api.avalai.ir/v1"
model = "cf.qwen2.5-coder-32b-instruct"
description = "یک آزمون ساده برای بررسی تراکنش‌های بیش از 10000 تومان"

print(f"\nپارامترها:")
print(f"  - Model: {model}")
print(f"  - Description: {description}")
print(f"  - Use Prompt: True (پرامپت کامل)")
print()

try:
    result = generate_test_with_avalai(
        user_description=description,
        api_key=api_key,
        base_url=base_url,
        model=model,
        use_prompt=True
    )
    
    if result:
        print("\n✅ تولید کد موفق بود!")
        print(f"طول کد: {len(result)} کاراکتر")
        print(f"\n200 کاراکتر اول:")
        print("=" * 80)
        print(result[:200])
        print("=" * 80)
    else:
        print("\n❌ تولید کد ناموفق بود!")
        
except Exception as e:
    print(f"\n❌ خطا: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
