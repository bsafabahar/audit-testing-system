from test_generator import generate_test_with_avalai

api_key = "aa-7QZl0Ab58B13JYYTG5WCeOSq8UIJh5IgwpqNa6hZLgACOACf"
base_url = "https://api.avalai.ir/v1"

print("تست با پرامپت کامل...")
result = generate_test_with_avalai(
    user_description="یک تست ساده برای شناسایی تراکنش‌های تکراری",
    api_key=api_key,
    model="gpt-4o-mini",
    base_url=base_url,
    use_prompt=True
)

if result:
    print(f"✅ موفق: {len(result)} کاراکتر")
    print(result[:200])
else:
    print("❌ خطا در تولید")

print("\n" + "="*50)
print("تست بدون پرامپت...")
result2 = generate_test_with_avalai(
    user_description="یک تست ساده برای شناسایی تراکنش‌های تکراری",
    api_key=api_key,
    model="gpt-4o-mini",
    base_url=base_url,
    use_prompt=False
)

if result2:
    print(f"✅ موفق: {len(result2)} کاراکتر")
    print(result2[:200])
else:
    print("❌ خطا در تولید")
