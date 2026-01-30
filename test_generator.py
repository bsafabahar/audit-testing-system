"""
ماژول تولید آزمون‌های حسابرسی با استفاده از هوش مصنوعی
Test Generator Module using AI

این ماژول از هوش مصنوعی برای تولید خودکار فایل‌های آزمون حسابرسی استفاده می‌کند.
"""

import os
import re
from typing import Optional, Dict, Any
from pathlib import Path


def save_generated_code_cache(code: str, cache_file: str = 'last_generated_test.py') -> bool:
    """
    ذخیره کد تولید شده در فایل cache
    
    Args:
        code: کد تولید شده
        cache_file: نام فایل cache
        
    Returns:
        True در صورت موفقیت
    """
    try:
        cache_path = Path(__file__).parent / cache_file
        with open(cache_path, 'w', encoding='utf-8') as f:
            f.write(code)
        print(f"[INFO] کد تولید شده در {cache_path} ذخیره شد")
        return True
    except Exception as e:
        print(f"[ERROR] خطا در ذخیره cache: {str(e)}")
        return False


def load_generated_code_cache(cache_file: str = 'last_generated_test.py') -> Optional[str]:
    """
    خواندن کد از فایل cache
    
    Args:
        cache_file: نام فایل cache
        
    Returns:
        کد ذخیره شده یا None
    """
    try:
        cache_path = Path(__file__).parent / cache_file
        if cache_path.exists():
            with open(cache_path, 'r', encoding='utf-8') as f:
                code = f.read()
            print(f"[INFO] کد از cache بارگذاری شد ({len(code)} کاراکتر)")
            return code
    except Exception as e:
        print(f"[ERROR] خطا در خواندن cache: {str(e)}")
    return None


def load_prompt_template() -> str:
    """
    بارگذاری قالب پرامپت از فایل
    
    Returns:
        متن پرامپت یا پرامپت ساده در صورت خطا
    """
    try:
        prompt_file = Path(__file__).parent / 'test_generation_prompt.txt'
        if prompt_file.exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        print(f"خطا در خواندن فایل پرامپت: {str(e)}")
    
    # پرامپت ساده برای زمانی که فایل در دسترس نیست
    return """
یک فایل پایتون برای آزمون حسابرسی بساز که دقیقا از ساختار زیر پیروی کند:

***

## بخش 1: METADATA و NAMING
نام فایل: `{{test_name}}.py` (با snake_case)

***

## بخش 2: DOCSTRING هدر
ابتدای فایل یک docstring سهخطی با این ساختار:

```python
\"\"\"
{{عنوان فارسی آزمون}}
{{English Test Title}}

{{توضیح فارسی آزمون - حداقل یک جمله}}
{{توضیح تکمیلی - اختیاری}}
\"\"\"
```

**الزامات:**
- دقیقا با سه علامت نقل قول شروع و پایان
- خط اول: عنوان فارسی
- خط دوم: عنوان انگلیسی
- خط سوم: خالی
- خطوط بعدی: توضیح فارسی کامل

***

## بخش 3: IMPORTS

### 3.1 Imports استاندارد (الزامی - دقیقا به این ترتیب):
```python
from typing import List, Dict, Any
from models import Transaction
from parameters import param_string, param_number
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
```

**نکات:**
- `param_string` و `param_number` را فقط آنهایی import کن که استفاده میشوند
- اگر آزمون param_boolean یا param_date نیاز دارد، آنها را هم اضافه کن

### 3.2 Imports کتابخانههای پایتون (بر اساس نیاز):
مثالها:
```python
from collections import Counter
from datetime import datetime
import math
import warnings
```

### 3.3 Imports کتابخانههای خارجی با مدیریت خطا (اگر نیاز است):
**الگوی استاندارد:**
```python
import warnings
warnings.filterwarnings('ignore')

try:
    from {{library_name}} import {{modules}}
    {{LIBRARY}}_AVAILABLE = True
except ImportError:
    {{LIBRARY}}_AVAILABLE = False
```

**مثال واقعی:**
```python
try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
```

***

## بخش 4: CONSTANTS (اختیاری)
اگر آزمون به ثابتهایی مثل آرایه، دیکشنری یا مقادیر از پیش تعریف شده نیاز دارد:

```python
# {{کامنت فارسی توضیح ثابت}}
CONSTANT_NAME = {{
    # مقادیر
}}
```

**مثال:**
```python
# توزیع بنفورد مورد انتظار
BENFORD_EXPECTED = {{
    1: 0.301,
    2: 0.176,
    ...
}}
```

***

## بخش 5: تابع define() (الزامی)

```python
def define() -> QueryDefinition:
    \"\"\"تعریف پارامترها و اسکیما\"\"\"
    
    parameters = [
        param_string('{{param1_name}}', '{{توضیح فارسی پارامتر}}', default_value='{{default}}'),
        param_number('{{param2_name}}', '{{توضیح فارسی پارامتر}}', default_value={{number}}),
        # سایر پارامترها
    ]
    
    result_schema = schema(
        col('{{Column1Name}}', '{{توضیح فارسی ستون}}', '{{data_type}}'),
        col('{{Column2Name}}', '{{توضیح فارسی ستون}}', '{{data_type}}'),
        # سایر ستونها
    )
    
    return {{
        'parameters': parameters,
        'schema': result_schema
    }}
```

### قوانین parameters:
- هر پارامتر روی یک خط جداگانه
- نام پارامترها: camelCase (حرف اول کوچک)
- انواع param: `param_string`, `param_number`, `param_boolean`, `param_date`
- default_value الزامی است
- توضیحات به فارسی

### قوانین schema (result_schema):
- نام ستونها: PascalCase (حرف اول بزرگ)
- توضیحات ستونها: فارسی
- انواع داده مجاز:
  - `'string'`: متن
  - `'integer'`: عدد صحیح
  - `'number'`: عدد اعشاری
  - `'currency'`: مبلغ پولی
  - `'percent'`: درصد
  - `'date'`: تاریخ
  - `'boolean'`: بله/خیر

### ستونهای رایج در Transaction:
- TransactionID یا Id
- DocumentDate
- AccountCode
- Debit (بدهکار)
- Credit (بستانکار)
- Description
- TransactionDate

***

## بخش 6: توابع کمکی (اختیاری)

```python
def helper_function_name(param1: type, param2: type) -> return_type:
    \"\"\"توضیح فارسی تابع\"\"\"
    # کامنت فارسی
    # منطق تابع
    return result
```

**الزامات:**
- Type hints برای پارامترها و return
- Docstring فارسی
- کامنتهای فارسی برای بخشهای کلیدی

***

## بخش 7: تابع execute() (الزامی)

```python
def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    \"\"\"اجرای آزمون {{نام آزمون}}\"\"\"
```

### ساختار استاندارد execute:

#### 7.1 بررسی وابستگیهای خارجی (اگر دارد):
```python
    if not {{LIBRARY}}_AVAILABLE:
        return [{{
            '{{FirstColumn}}': 'ERROR',
            # سایر ستونها با مقادیر پیشفرض
            '{{MessageColumn}}': 'Library not installed',
        }}]
```

#### 7.2 دریافت پارامترها:
```python
    # دریافت پارامترها
    param1 = get_parameter('{{param1Name}}', '{{default_value}}')
    param2 = get_parameter('{{param2Name}}', {{default_number}})
```

**نکات:**
- کامنت فارسی "# دریافت پارامترها"
- نام متغیرها: snake_case
- مقادیر پیشفرض باید با define() یکسان باشند

#### 7.3 دریافت دادهها از دیتابیس:
```python
    # دریافت دادهها
    query = session.query(Transaction)
    results = query.all()
```

#### 7.4 پردازش دادهها:
با کامنتهای فارسی مناسب:
```python
    # {{شرح مرحله پردازش}}
    data_list = []
    
    for t in results:
        # منطق پردازش
        # بررسی شرایط
        # محاسبات
```

**الگوهای رایج:**
- استفاده از Counter برای شمارش
- حلقههای for روی results
- شرطهای if برای فیلتر کردن
- محاسبات آماری

#### 7.5 بررسی حداقل داده:
اگر آزمون به حداقل تعداد رکورد نیاز دارد:
```python
    if len(data_list) < {{minimum_required}}:
        return [{{
            '{{Column1}}': 'ERROR',
            '{{MessageColumn}}': 'Not enough transactions (minimum {{number}})',
            # سایر ستونها
        }}]
```

#### 7.6 ساخت خروجی:
```python
    # {{توضیح فارسی}}
    data = []
    
    for item in items:
        row = {{
            '{{Column1Name}}': value1,
            '{{Column2Name}}': value2,
            '{{Column3Name}}': round(value3, {{decimals}}),
            # سایر ستونها
        }}
        data.append(row)
```

**قوانین row dictionary:**
- کلیدها: دقیقا همان نامهای ستونها در schema
- مقادیر عددی: از round() برای اعشار استفاده کن
- تاریخ: به صورت string با format مناسب
- null values: از None یا '' استفاده کن

#### 7.7 مرتبسازی (اختیاری):
```python
    # مرتبسازی بر اساس {{معیار}}
    data.sort(key=lambda x: x['{{ColumnName}}'], reverse={{True/False}})
```

#### 7.8 اضافه کردن ردیف خلاصه (اختیاری):
اگر آزمون نیاز به ردیف جمع یا خلاصه دارد:
```python
    # افزودن ردیف خلاصه
    data.append({{
        '{{Column1}}': {{summary_value}},
        '{{Column2}}': {{total_value}},
        # سایر ستونها
    }})
```

#### 7.9 بازگشت نتیجه:
```python
    return data
```

***

## بخش 8: قوانین FORMATTING

### فاصلهگذاری:
- دو خط خالی بین توابع سطح بالا
- یک خط خالی بین بخشهای منطقی داخل توابع
- بدون فضای خالی اضافی در انتهای خطوط

### کامنتها:
- همه کامنتها به فارسی
- کامنتهای بخش با # در ابتدای خط
- کامنتهای inline در صورت نیاز

### نامگذاری:
- توابع: snake_case
- متغیرها: snake_case  
- ثابتها: UPPER_SNAKE_CASE
- پارامترها: camelCase
- ستونهای schema: PascalCase

### Type hints:
- همیشه برای پارامترهای توابع
- همیشه برای return type
- برای متغیرهای مهم

***

## بخش 9: الگوهای رایج در execute()

### 9.1 کار با ستونهای Debit/Credit:
```python
column_name = get_parameter('columnName', 'Debit')
amount = t.Debit if column_name == 'Debit' else t.Credit
if not amount or amount <= 0:
    continue
```

### 9.2 کار با تاریخ:
```python
if hasattr(t, 'TransactionDate') and t.TransactionDate:
    trans_date = t.TransactionDate
elif hasattr(t, 'DocumentDate') and t.DocumentDate:
    if isinstance(t.DocumentDate, datetime):
        trans_date = t.DocumentDate
    else:
        trans_date = datetime.combine(t.DocumentDate, datetime.min.time())
```

### 9.3 مدیریت TransactionID:
```python
trans_id = str(t.TransactionID) if hasattr(t, 'TransactionID') and t.TransactionID else str(t.Id)
```

### 9.4 Format کردن تاریخ برای خروجی:
```python
'DocumentDate': trans_date.strftime('%Y-%m-%d') if trans_date else ''
```

### 9.5 مدیریت None values:
```python
'AccountCode': t.AccountCode or ''
'Description': t.Description if t.Description else 'N/A'
```

***

## بخش 10: TEMPLATE نهایی استفاده

حالا با استفاده از تمام بخشهای بالا، آزمون زیر را تولید کن:

**[در اینجا تعریف آزمون کاربر قرار میگیرد]**

{user_description}

***

## دستورالعملهای اجرایی:
1. نام فایل را مناسب انتخاب کن (snake_case)
2. Docstring را با توضیحات کامل فارسی و انگلیسی بنویس
3. Imports لازم را شناسایی و به ترتیب صحیح import کن
4. اگر کتابخانه خارجی نیاز است، try-except بگذار
5. اگر ثابتهایی نیاز است، تعریف کن
6. تابع define() را با پارامترها و schema دقیق بنویس
7. توابع کمکی مورد نیاز را بنویس
8. تابع execute() را با تمام مراحل استاندارد بنویس
9. همه کامنتها و docstring ها فارسی باشند
10. خروجی باید List[Dict[str, Any]] باشد
11. کلیدهای dict باید دقیقا همان نام ستونهای schema باشند
12. از round() برای اعداد اعشاری استفاده کن

فقط کد پایتون را بدون توضیحات اضافی برگردان. کد باید آماده اجرا باشد.
"""


def generate_test_with_avalai(user_description: str, api_key: str, model: str = "gpt-4o-mini", base_url: str = "https://api.avalai.ir/v1", use_prompt: bool = True) -> Optional[str]:
    """
    تولید کد آزمون با استفاده از AvalAI API
    
    Args:
        user_description: توضیحات آزمون از کاربر
        api_key: کلید API AvalAI
        model: مدل AvalAI (پیشفرض: gpt-4o-mini)
        base_url: آدرس پایه API AvalAI
        use_prompt: استفاده از پرامپت کامل (True) یا فقط توضیحات کاربر (False)
        
    Returns:
        کد پایتون تولید شده یا None در صورت خطا
    """
    try:
        print(f"[DEBUG] Starting generate_test_with_avalai...")
        print(f"[DEBUG] Model: {model}, Use Prompt: {use_prompt}")
        
        from openai import OpenAI
        
        # ساخت کلاینت با آدرس پایه AvalAI
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        print(f"[DEBUG] OpenAI client created")
        
        # ساخت پرامپت کامل
        if use_prompt:
            prompt_template = load_prompt_template()
            full_prompt = prompt_template.format(user_description=user_description)
            print(f"[DEBUG] Using full prompt, length: {len(full_prompt)}")
        else:
            full_prompt = user_description
            print(f"[DEBUG] Using simple prompt, length: {len(full_prompt)}")
        
        print(f"[DEBUG] Sending request to AvalAI...")
        # ارسال درخواست به AvalAI
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "شما یک متخصص برنامه‌نویسی پایتون و حسابرسی هستید که کدهای با کیفیت بالا تولید می‌کنید."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        
        print(f"[DEBUG] Response received")
        print(f"[DEBUG] Response type: {type(response)}")
        print(f"[DEBUG] Response has choices: {hasattr(response, 'choices')}")
        
        # استخراج کد تولید شده
        if not response.choices:
            print(f"[ERROR] No choices in response")
            return None
        
        print(f"[DEBUG] Number of choices: {len(response.choices)}")
        
        if not response.choices[0].message:
            print(f"[ERROR] No message in first choice")
            return None
            
        if not response.choices[0].message.content:
            print(f"[ERROR] Empty content in message")
            print(f"[DEBUG] Message object: {response.choices[0].message}")
            print(f"[DEBUG] Finish reason: {response.choices[0].finish_reason}")
            print(f"[ERROR] احتمالاً مدل '{model}' برای این نوع درخواست مناسب نیست")
            print(f"[ERROR] یا پرامپت بیش از حد طولانی است (طول: {len(full_prompt) if use_prompt else 'N/A'})")
            return None
            
        generated_content = response.choices[0].message.content.strip()
        print(f"[DEBUG] Content extracted successfully")
        
        if not generated_content:
            print(f"[ERROR] Generated content is empty after strip")
            return None
            
        print(f"[DEBUG] Generated content length: {len(generated_content)}")
        
        # حذف markdown code blocks فقط از ابتدا و انتهای کد پایتون (قبل از ---MARKDOWN_FILE---)
        # اگر کل محتوا با ```python شروع شود
        if generated_content.startswith("```python"):
            # پیدا کردن اولین خط بعد از ```python
            lines = generated_content.split('\n')
            if len(lines) > 1:
                generated_content = '\n'.join(lines[1:])
        elif generated_content.startswith("```"):
            # پیدا کردن اولین خط بعد از ```
            lines = generated_content.split('\n')
            if len(lines) > 1:
                generated_content = '\n'.join(lines[1:])
        
        # حذف ``` از انتهای کد قبل از ---MARKDOWN_FILE--- (اگر وجود دارد)
        # ابتدا بررسی می‌کنیم که آیا ---MARKDOWN_FILE--- وجود دارد
        if '---MARKDOWN_FILE---' in generated_content:
            parts = generated_content.split('---MARKDOWN_FILE---')
            python_part = parts[0].strip()
            # حذف ``` از انتهای بخش پایتون
            if python_part.endswith('```'):
                python_part = python_part[:-3].strip()
            # ترکیب دوباره
            generated_content = python_part + '\n\n---MARKDOWN_FILE---\n\n' + parts[1]
        else:
            # اگر separator نداریم، فقط ``` آخر را حذف کنیم
            if generated_content.endswith('```'):
                generated_content = generated_content[:-3].strip()
        
        print(f"[DEBUG] Content cleaned, final length: {len(generated_content)}")
        
        # ذخیره در cache (کل محتوا شامل کد و md)
        save_generated_code_cache(generated_content)
        
        return generated_content
        
    except Exception as e:
        print(f"[ERROR] خطا در تولید آزمون با AvalAI: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def generate_test_with_anthropic(user_description: str, api_key: str, model: str = "claude-3-sonnet-20240229", use_prompt: bool = True) -> Optional[str]:
    """
    تولید کد آزمون با استفاده از Anthropic Claude API
    
    Args:
        user_description: توضیحات آزمون از کاربر
        api_key: کلید API Anthropic
        model: مدل Claude (پیشفرض: claude-3-sonnet)
        use_prompt: استفاده از پرامپت کامل (True) یا فقط توضیحات کاربر (False)
        
    Returns:
        کد پایتون تولید شده یا None در صورت خطا
    """
    try:
        import anthropic
        
        # ساخت کلاینت
        client = anthropic.Anthropic(api_key=api_key)
        
        # ساخت پرامپت کامل
        if use_prompt:
            prompt_template = load_prompt_template()
            full_prompt = prompt_template.format(user_description=user_description)
        else:
            full_prompt = user_description
        
        # ارسال درخواست به Claude
        message = client.messages.create(
            model=model,
            max_tokens=4000,
            temperature=0.3,
            messages=[
                {"role": "user", "content": full_prompt}
            ]
        )
        
        # استخراج کد تولید شده
        print(f"[DEBUG] Message type: {type(message)}")
        print(f"[DEBUG] Message has content: {hasattr(message, 'content')}")
        
        if not message.content:
            print(f"[ERROR] Empty content from Claude API")
            return None
        
        print(f"[DEBUG] Content length: {len(message.content)}")
        
        if not message.content[0].text:
            print(f"[ERROR] Empty text in first content block")
            print(f"[DEBUG] Content[0]: {message.content[0]}")
            print(f"[DEBUG] Stop reason: {message.stop_reason}")
            print(f"[ERROR] احتمالاً مدل '{model}' برای این نوع درخواست مناسب نیست")
            return None
            
        generated_content = message.content[0].text.strip()
        print(f"[DEBUG] Content extracted successfully")
        
        if not generated_content:
            print(f"[ERROR] Generated content is empty after strip")
            return None
        
        # حذف markdown code blocks فقط از ابتدا و انتهای کد پایتون (قبل از ---MARKDOWN_FILE---)
        if generated_content.startswith("```python"):
            lines = generated_content.split('\n')
            if len(lines) > 1:
                generated_content = '\n'.join(lines[1:])
        elif generated_content.startswith("```"):
            lines = generated_content.split('\n')
            if len(lines) > 1:
                generated_content = '\n'.join(lines[1:])
        
        # حذف ``` از انتهای کد قبل از ---MARKDOWN_FILE---
        if '---MARKDOWN_FILE---' in generated_content:
            parts = generated_content.split('---MARKDOWN_FILE---')
            python_part = parts[0].strip()
            if python_part.endswith('```'):
                python_part = python_part[:-3].strip()
            generated_content = python_part + '\n\n---MARKDOWN_FILE---\n\n' + parts[1]
        else:
            if generated_content.endswith('```'):
                generated_content = generated_content[:-3].strip()
        
        # ذخیره در cache
        save_generated_code_cache(generated_content)
            
        return generated_content
        
    except Exception as e:
        print(f"[ERROR] خطا در تولید آزمون با Claude: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def extract_test_name(code: str) -> Optional[str]:
    """
    استخراج نام آزمون از docstring یا محتوای کد
    
    Args:
        code: کد پایتون تولید شده
        
    Returns:
        نام پیشنهادی فایل یا None
    """
    try:
        # تلاش برای استخراج نام انگلیسی از خط دوم docstring
        # الگو: """ + خط اول (فارسی) + newline + خط دوم (انگلیسی)
        docstring_pattern = r'"""\s*\n([^\n]+)\n([^\n]+)'
        match = re.search(docstring_pattern, code)
        
        if match:
            farsi_line = match.group(1).strip()
            english_line = match.group(2).strip()
            
            print(f"[DEBUG] Docstring line 1 (Farsi): '{farsi_line}'")
            print(f"[DEBUG] Docstring line 2 (English): '{english_line}'")
            
            # فقط کاراکترهای انگلیسی، اعداد، فاصله و خط تیره را نگه دار
            name = re.sub(r'[^a-zA-Z0-9\s-]', '', english_line)
            # تبدیل فاصله‌ها به underscore
            name = re.sub(r'[\s-]+', '_', name)
            name = name.lower()
            
            print(f"[DEBUG] After cleaning: '{name}'")
            
            # محدود کردن طول به 50 کاراکتر
            if len(name) > 50:
                name = name[:50]
            
            # حذف underscore های اضافی از ابتدا و انتها
            name = name.strip('_')
            
            # اضافه کردن _test اگر ندارد
            if name and not name.endswith('_test'):
                name += '_test'
            
            print(f"[DEBUG] Final extracted name: '{name}'")
            return name if name else None
        else:
            print(f"[WARNING] Docstring pattern not matched!")
            print(f"[DEBUG] First 200 chars of code: {code[:200]}")
    except Exception as e:
        print(f"خطا در استخراج نام: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return None


def separate_code_and_markdown(generated_content: str) -> tuple[str, Optional[str]]:
    """
    جدا کردن کد پایتون و فایل markdown از خروجی AI
    
    Args:
        generated_content: محتوای تولید شده شامل کد و md
        
    Returns:
        tuple از (کد پایتون، محتوای markdown یا None)
    """
    try:
        # جستجوی علامت جداکننده
        separator = '---MARKDOWN_FILE---'
        
        if separator in generated_content:
            parts = generated_content.split(separator)
            python_code = parts[0].strip()
            markdown_content = parts[1].strip()
            
            # حذف markdown code blocks اگر وجود دارد
            if markdown_content.startswith('```markdown'):
                markdown_content = markdown_content[11:]
            elif markdown_content.startswith('```md'):
                markdown_content = markdown_content[5:]
            elif markdown_content.startswith('```'):
                markdown_content = markdown_content[3:]
            
            if markdown_content.endswith('```'):
                markdown_content = markdown_content[:-3]
            
            print(f"[INFO] کد و markdown جدا شدند (Python: {len(python_code)} chars, MD: {len(markdown_content)} chars)")
            return python_code.strip(), markdown_content.strip()
        else:
            print(f"[WARNING] علامت جداکننده {separator} پیدا نشد، فقط کد پایتون برگشت داده می‌شود")
            return generated_content.strip(), None
            
    except Exception as e:
        print(f"[ERROR] خطا در جدا کردن کد و markdown: {str(e)}")
        return generated_content.strip(), None


def save_markdown_file(markdown_content: str, filename: str, queries_dir: str = "queries") -> bool:
    """
    ذخیره فایل راهنمای markdown در پوشه queries/custom_tests
    
    Args:
        markdown_content: محتوای markdown
        filename: نام فایل (بدون پسوند)
        queries_dir: مسیر پوشه queries
        
    Returns:
        True در صورت موفقیت، False در صورت خطا
    """
    try:
        # اطمینان از وجود پوشه queries/custom_tests
        queries_path = Path(queries_dir) / 'custom_tests'
        queries_path.mkdir(parents=True, exist_ok=True)
        
        # اضافه کردن پسوند .md اگر ندارد
        if not filename.endswith('.md'):
            filename = filename.replace('.py', '') + '.md'
        
        # مسیر کامل فایل
        file_path = queries_path / filename
        
        # ذخیره فایل
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"فایل راهنما با موفقیت در {file_path} ذخیره شد")
        return True
        
    except Exception as e:
        print(f"خطا در ذخیره فایل markdown: {str(e)}")
        return False


def save_generated_test(code: str, filename: str, queries_dir: str = "queries") -> bool:
    """
    ذخیره کد تولید شده در پوشه queries/custom_tests
    
    Args:
        code: کد پایتون تولید شده
        filename: نام فایل (بدون پسوند)
        queries_dir: مسیر پوشه queries
        
    Returns:
        True در صورت موفقیت، False در صورت خطا
    """
    try:
        # اطمینان از وجود پوشه queries/custom_tests
        queries_path = Path(queries_dir) / 'custom_tests'
        queries_path.mkdir(parents=True, exist_ok=True)
        
        # اضافه کردن پسوند .py اگر ندارد
        if not filename.endswith('.py'):
            filename += '.py'
        
        # مسیر کامل فایل
        file_path = queries_path / filename
        
        # ذخیره فایل
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        print(f"آزمون با موفقیت در {file_path} ذخیره شد")
        return True
        
    except Exception as e:
        print(f"خطا در ذخیره فایل: {str(e)}")
        return False


def generate_and_save_test(
    user_description: str,
    api_key: str,
    provider: str = "avalai",
    model: Optional[str] = None,
    filename: Optional[str] = None,
    queries_dir: str = "queries",
    base_url: str = "https://api.avalai.ir/v1",
    use_prompt: bool = True
) -> Dict[str, Any]:
    """
    تولید و ذخیره یک آزمون حسابرسی جدید
    
    Args:
        user_description: توضیحات آزمون از کاربر
        api_key: کلید API
        provider: ارائه‌دهنده AI (avalai یا anthropic)
        model: مدل مورد استفاده (اختیاری)
        filename: نام فایل (اختیاری - در صورت نبودن از کد استخراج می‌شود)
        queries_dir: مسیر پوشه queries
        base_url: آدرس پایه API (فقط برای avalai)
        use_prompt: استفاده از پرامپت کامل (گران‌تر اما بهتر) یا ساده (ارزان‌تر)
        
    Returns:
        دیکشنری شامل نتیجه: {'success': bool, 'message': str, 'filename': str, 'code': str}
    """
    # تولید کد با AI
    print(f"[DEBUG] generate_and_save_test called")
    print(f"[DEBUG] Provider: {provider}, Model: {model}, Use Prompt: {use_prompt}")
    
    if provider.lower() == "avalai":
        model = model or "gpt-4o-mini"
        print(f"[DEBUG] Calling generate_test_with_avalai...")
        generated_code = generate_test_with_avalai(user_description, api_key, model, base_url, use_prompt)
        print(f"[DEBUG] generate_test_with_avalai returned: {type(generated_code)}, Length: {len(generated_code) if generated_code else 0}")
    elif provider.lower() == "anthropic":
        model = model or "claude-3-sonnet-20240229"
        generated_code = generate_test_with_anthropic(user_description, api_key, model, use_prompt)
    else:
        return {
            'success': False,
            'message': f'ارائه‌دهنده نامعتبر: {provider}',
            'filename': None,
            'code': None
        }
    
    print(f"[DEBUG] Generated code: {generated_code is not None}")
    
    if not generated_code:
        print(f"[ERROR] No code generated!")
        print(f"[ERROR] Provider used: {provider}")
        print(f"[ERROR] Model used: {model}")
        print(f"[ERROR] Description length: {len(user_description)}")
        print(f"[ERROR] Use prompt: {use_prompt}")
        
        # پیشنهادات رفع مشکل
        suggestions = []
        if 'nano' in model.lower():
            suggestions.append('مدل Nano برای پرامپت‌های پیچیده مناسب نیست. از gpt-4o-mini یا claude استفاده کنید')
        if use_prompt:
            suggestions.append('می‌توانید use_prompt=False را امتحان کنید (پرامپت ساده‌تر)')
        
        error_message = f'خطا در تولید کد از AI (Provider: {provider}, Model: {model})'
        if suggestions:
            error_message += '\n\n💡 پیشنهادات:\n' + '\n'.join(f'  • {s}' for s in suggestions)
        
        return {
            'success': False,
            'message': error_message,
            'filename': None,
            'code': None
        }
    
    print(f"[DEBUG] Code generated successfully, separating code and markdown...")
    
    # جدا کردن کد پایتون و markdown
    python_code, markdown_content = separate_code_and_markdown(generated_code)
    
    # استخراج نام فایل اگر مشخص نشده
    if not filename:
        filename = extract_test_name(python_code)
        print(f"[DEBUG] Extracted filename: {filename}")
        
        # بررسی نام‌های نامعتبر
        invalid_names = ['custom_test', 'test', 'my_test', 'audit_test', 'unnamed_test']
        if not filename or filename in invalid_names:
            # اگر نتوانستیم نام را استخراج کنیم یا نام عمومی است، از timestamp استفاده می‌کنیم
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'unnamed_test_{timestamp}'
            print(f"[WARNING] Could not extract valid filename from docstring or name is generic!")
            print(f"[DEBUG] Using timestamped filename: {filename}")
    
    print(f"[DEBUG] Saving test to file: {filename}")
    
    # ذخیره فایل پایتون
    success_py = save_generated_test(python_code, filename, queries_dir)
    
    # ذخیره فایل markdown اگر وجود دارد
    success_md = True
    if markdown_content:
        success_md = save_markdown_file(markdown_content, filename, queries_dir)
        print(f"[DEBUG] Markdown save result: {success_md}")
    else:
        print(f"[WARNING] فایل markdown تولید نشد")
    
    print(f"[DEBUG] Python save result: {success_py}")
    
    if success_py:
        message = 'آزمون با موفقیت تولید و ذخیره شد'
        if markdown_content and success_md:
            message += ' (شامل فایل راهنما)'
        elif markdown_content and not success_md:
            message += ' (خطا در ذخیره فایل راهنما)'
        
        return {
            'success': True,
            'message': message,
            'filename': filename if filename.endswith('.py') else f'{filename}.py',
            'code': python_code,
            'markdown': markdown_content if markdown_content else None
        }
    else:
        return {
            'success': False,
            'message': 'خطا در ذخیره فایل',
            'filename': filename,
            'code': python_code,
            'markdown': markdown_content if markdown_content else None
        }
