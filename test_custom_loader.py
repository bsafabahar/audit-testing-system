from pathlib import Path
import re

queries_dir = Path('queries')
print(f"Queries dir exists: {queries_dir.exists()}")

for py_file in queries_dir.glob('*.py'):
    if py_file.name == '__init__.py':
        continue
    
    print(f"\nChecking: {py_file.name}")
    
    try:
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read(500)
        
        docstring_match = re.search(r'"""(.*?)\n(.*?)\n', content, re.DOTALL)
        
        if docstring_match:
            farsi_name = docstring_match.group(1).strip()
            english_name = docstring_match.group(2).strip()
            test_id = py_file.stem
            
            print(f"  ID: {test_id}")
            print(f"  Has Farsi: {len(farsi_name) > 0}")
            print(f"  Has English: {len(english_name) > 0}")
            
            # Check if predefined
            from web_ui import AUDIT_TESTS
            is_predefined = False
            for category in AUDIT_TESTS.values():
                if any(t['id'] == test_id for t in category.get('tests', [])):
                    is_predefined = True
                    break
            print(f"  Predefined: {is_predefined}")
        else:
            print("  No docstring found")
            
    except Exception as e:
        print(f"  Error: {e}")
