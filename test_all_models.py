"""
تست با مدل‌های مختلف برای بررسی کدام یک کار می‌کند
"""
from test_generator import generate_test_with_avalai

models_to_test = [
    "gpt-5-nano-2025-08-07",  # مدلی که خطا داد
    "gpt-4o-mini",            # مدل معتبر
    "gpt-4o",                 # مدل معتبر
    "claude-sonnet-4-5",      # مدل Claude از طریق AvalAI
]

api_key = "aa-7QZl0Ab58B13JYYTG5WCeOSq8UIJh5IgwpqNa6hZLgACOACf"
base_url = "https://api.avalai.ir/v1"
description = "تست ساده"

print("=" * 80)
print("Testing different models with AvalAI")
print("=" * 80)

for model in models_to_test:
    print(f"\n{'='*80}")
    print(f"Testing model: {model}")
    print(f"{'='*80}")
    
    try:
        result = generate_test_with_avalai(
            user_description=description,
            api_key=api_key,
            base_url=base_url,
            model=model,
            use_prompt=False  # پرامپت ساده برای سرعت
        )
        
        if result:
            print(f"✅ SUCCESS - طول: {len(result)} کاراکتر")
        else:
            print(f"❌ FAILED - result = None")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

print("\n" + "=" * 80)
print("Test completed!")
print("=" * 80)
