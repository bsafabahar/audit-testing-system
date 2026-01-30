import re

with open('queries/automated_test_example.py', 'r', encoding='utf-8') as f:
    content = f.read(500)

print("Content (first 200 chars):")
print(repr(content[:200]))

docstring_match = re.search(r'"""(.*?)\n(.*?)\n', content, re.DOTALL)

if docstring_match:
    print("\nMatch found!")
    print(f"Group 1 (Farsi): '{docstring_match.group(1)}'")
    print(f"Group 2 (English): '{docstring_match.group(2)}'")
else:
    print("\nNo match!")
