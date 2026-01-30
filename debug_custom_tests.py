"""
اسکریپت دیباگ برای بررسی مشکل بارگذاری آزمون‌های شخصی
"""
from pathlib import Path
import re

custom_tests_dir = Path(__file__).parent / 'queries' / 'custom_tests'

print(f"پوشه custom_tests: {custom_tests_dir}")
print(f"آیا وجود دارد؟ {custom_tests_dir.exists()}\n")

for py_file in custom_tests_dir.glob('*.py'):
    if py_file.name == '__init__.py':
        continue
        
    print(f"\n{'='*60}")
    print(f"فایل: {py_file.name}")
    print(f"{'='*60}")
    
    try:
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read(500)
            
        print("محتوای 500 کاراکتر اول:")
        print(content)
        print("\n" + "-"*60)
        
        # استخراج docstring
        docstring_match = re.search(r'"""\s*\n(.*?)\n(.*?)\n', content, re.DOTALL)
        
        if docstring_match:
            farsi_name = docstring_match.group(1).strip()
            english_name = docstring_match.group(2).strip()
            
            print(f"نام فارسی: {farsi_name}")
            print(f"نام انگلیسی: {english_name}")
            
            test_id = f"custom_tests_{py_file.stem}"
            print(f"ID آزمون: {test_id}")
        else:
            print("❌ regex مچ نشد!")
            
    except Exception as e:
        print(f"❌ خطا: {str(e)}")
