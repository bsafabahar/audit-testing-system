"""
تست کامل برای تشخیص مشکل در web UI
"""
import json
from test_generator import generate_and_save_test

print("=" * 80)
print("Testing generate_and_save_test (شبیه‌سازی web UI)")
print("=" * 80)

# داده‌های ورودی (شبیه به آنچه از web UI می‌آید)
user_description = "یک آزمون ساده برای بررسی تراکنش‌های بیش از 10000 تومان"
api_key = "aa-7QZl0Ab58B13JYYTG5WCeOSq8UIJh5IgwpqNa6hZLgACOACf"
provider = "avalai"
model = "claude-sonnet-4-5"
base_url = "https://api.avalai.ir/v1"
use_prompt = True

print(f"\nپارامترها:")
print(f"  - Provider: {provider}")
print(f"  - Model: {model}")
print(f"  - Base URL: {base_url}")
print(f"  - Use Prompt: {use_prompt}")
print(f"  - Description: {user_description}")
print()

try:
    result = generate_and_save_test(
        user_description=user_description,
        api_key=api_key,
        provider=provider,
        model=model,
        filename=None,
        queries_dir="queries",
        base_url=base_url,
        use_prompt=use_prompt
    )
    
    print("\n" + "=" * 80)
    print("نتیجه:")
    print("=" * 80)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if result['success']:
        print("\n✅ موفق!")
    else:
        print("\n❌ ناموفق!")
        print(f"پیام خطا: {result['message']}")
        
except Exception as e:
    print(f"\n❌ خطا رخ داد: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
