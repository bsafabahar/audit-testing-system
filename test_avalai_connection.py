"""
تست اتصال به AvalAI
"""

from test_generator import generate_test_with_avalai

# تست ساده
test_description = """
یک آزمون ساده برای بررسی تراکنش‌های تکراری بسازید.
آزمون باید تراکنش‌هایی را که مبلغ یکسان و تاریخ یکسان دارند شناسایی کند.
"""

api_key = "aa-7QZl0Ab58B13JYYTG5WCeOSq8UIJh5IgwpqNa6hZLgACOACf"
base_url = "https://api.avalai.ir/v1"

print("در حال اتصال به AvalAI...")
result = generate_test_with_avalai(
    user_description=test_description,
    api_key=api_key,
    model="gpt-4o-mini",
    base_url=base_url
)

if result:
    print("✅ اتصال موفق بود!")
    print("\n" + "="*50)
    print("کد تولید شده:")
    print("="*50)
    print(result[:500])  # نمایش 500 کاراکتر اول
    print("...")
else:
    print("❌ خطا در اتصال یا تولید کد")
