import sys
from pathlib import Path

# بارگذاری web_ui
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from web_ui import load_custom_tests, AUDIT_TESTS

print("=== بررسی فایل‌های موجود در queries/custom_tests ===")
custom_tests_dir = Path(__file__).parent / 'queries' / 'custom_tests'
if custom_tests_dir.exists():
    for py_file in custom_tests_dir.glob('*.py'):
        if py_file.name != '__init__.py':
            print(f"فایل: {py_file.name}")
            
            # خواندن docstring
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read(500)
                
                import re
                docstring_match = re.search(r'"""\s*\n(.*?)\n(.*?)\n', content, re.DOTALL)
                
                if docstring_match:
                    farsi_name = docstring_match.group(1).strip()
                    english_name = docstring_match.group(2).strip()
                    test_id = f"custom_tests_{py_file.stem}"
                    
                    print(f"  - نام فارسی: {farsi_name}")
                    print(f"  - نام انگلیسی: {english_name}")
                    print(f"  - شناسه: {test_id}")
                    print()
                else:
                    print(f"  - docstring پیدا نشد")
                    print()
            except Exception as e:
                print(f"  - خطا: {str(e)}")
                print()
else:
    print("پوشه custom_tests وجود ندارد!")

print("\n=== نتیجه load_custom_tests ===")
custom_tests = load_custom_tests()
print(f"تعداد: {len(custom_tests)}")
for test in custom_tests:
    print(f"  - {test['id']}: {test['name']}")
