import sys
sys.path.insert(0, '.')
from web_ui import load_custom_tests

tests = load_custom_tests()
print(f'Found {len(tests)} tests:')
for t in tests:
    print(f'  - {t["id"]}: {t["name"]}')
