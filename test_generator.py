"""
ماژول تولید آزمون‌های حسابرسی با استفاده از هوش مصنوعی
Test Generator Module using AI

این ماژول از هوش مصنوعی برای تولید خودکار فایل‌های آزمون حسابرسی استفاده می‌کند.
"""

import os
import re
from typing import Optional, Dict, Any
from pathlib import Path


# قالب پرامپت برای تولید آزمون
TEST_GENERATION_PROMPT_TEMPLATE = """
شما باید یک فایل پایتون برای آزمون حسابرسی بسازید که دقیقا از ساختار زیر پیروی کند:

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


def generate_test_with_openai(user_description: str, api_key: str, model: str = "gpt-4") -> Optional[str]:
    """
    تولید کد آزمون با استفاده از OpenAI API
    
    Args:
        user_description: توضیحات آزمون از کاربر
        api_key: کلید API OpenAI
        model: مدل OpenAI (پیشفرض: gpt-4)
        
    Returns:
        کد پایتون تولید شده یا None در صورت خطا
    """
    try:
        import openai
        
        # تنظیم کلید API
        openai.api_key = api_key
        
        # ساخت پرامپت کامل
        full_prompt = TEST_GENERATION_PROMPT_TEMPLATE.format(user_description=user_description)
        
        # ارسال درخواست به OpenAI
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "شما یک متخصص برنامه‌نویسی پایتون و حسابرسی هستید که کدهای با کیفیت بالا تولید می‌کنید."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        
        # استخراج کد تولید شده
        generated_code = response.choices[0].message.content.strip()
        
        # حذف markdown code blocks اگر وجود دارد
        if generated_code.startswith("```python"):
            generated_code = generated_code[9:]  # حذف ```python
        if generated_code.startswith("```"):
            generated_code = generated_code[3:]  # حذف ```
        if generated_code.endswith("```"):
            generated_code = generated_code[:-3]  # حذف ```
            
        return generated_code.strip()
        
    except Exception as e:
        print(f"خطا در تولید آزمون با OpenAI: {str(e)}")
        return None


def generate_test_with_anthropic(user_description: str, api_key: str, model: str = "claude-3-sonnet-20240229") -> Optional[str]:
    """
    تولید کد آزمون با استفاده از Anthropic Claude API
    
    Args:
        user_description: توضیحات آزمون از کاربر
        api_key: کلید API Anthropic
        model: مدل Claude (پیشفرض: claude-3-sonnet)
        
    Returns:
        کد پایتون تولید شده یا None در صورت خطا
    """
    try:
        import anthropic
        
        # ساخت کلاینت
        client = anthropic.Anthropic(api_key=api_key)
        
        # ساخت پرامپت کامل
        full_prompt = TEST_GENERATION_PROMPT_TEMPLATE.format(user_description=user_description)
        
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
        generated_code = message.content[0].text.strip()
        
        # حذف markdown code blocks اگر وجود دارد
        if generated_code.startswith("```python"):
            generated_code = generated_code[9:]
        if generated_code.startswith("```"):
            generated_code = generated_code[3:]
        if generated_code.endswith("```"):
            generated_code = generated_code[:-3]
            
        return generated_code.strip()
        
    except Exception as e:
        print(f"خطا در تولید آزمون با Claude: {str(e)}")
        return None


def extract_test_name(code: str) -> Optional[str]:
    """
    استخراج نام آزمون از docstring یا محتوای کد
    
    Args:
        code: کد پایتون تولید شده
        
    Returns:
        نام پیشنهادی فایل یا None
    """
    # تلاش برای استخراج نام از docstring
    docstring_match = re.search(r'"""([^"]+)', code)
    if docstring_match:
        first_line = docstring_match.group(1).strip()
        # تبدیل به snake_case
        name = re.sub(r'[^\w\s-]', '', first_line)
        name = re.sub(r'[\s-]+', '_', name)
        name = name.lower()
        if name and not name.endswith('_test'):
            name += '_test'
        return name
    
    return None


def save_generated_test(code: str, filename: str, queries_dir: str = "queries") -> bool:
    """
    ذخیره کد تولید شده در پوشه queries
    
    Args:
        code: کد پایتون تولید شده
        filename: نام فایل (بدون پسوند)
        queries_dir: مسیر پوشه queries
        
    Returns:
        True در صورت موفقیت، False در صورت خطا
    """
    try:
        # اطمینان از وجود پوشه queries
        queries_path = Path(queries_dir)
        queries_path.mkdir(exist_ok=True)
        
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
    provider: str = "openai",
    model: Optional[str] = None,
    filename: Optional[str] = None,
    queries_dir: str = "queries"
) -> Dict[str, Any]:
    """
    تولید و ذخیره یک آزمون حسابرسی جدید
    
    Args:
        user_description: توضیحات آزمون از کاربر
        api_key: کلید API
        provider: ارائه‌دهنده AI (openai یا anthropic)
        model: مدل مورد استفاده (اختیاری)
        filename: نام فایل (اختیاری - در صورت نبودن از کد استخراج می‌شود)
        queries_dir: مسیر پوشه queries
        
    Returns:
        دیکشنری شامل نتیجه: {'success': bool, 'message': str, 'filename': str, 'code': str}
    """
    # تولید کد با AI
    if provider.lower() == "openai":
        model = model or "gpt-4"
        generated_code = generate_test_with_openai(user_description, api_key, model)
    elif provider.lower() == "anthropic":
        model = model or "claude-3-sonnet-20240229"
        generated_code = generate_test_with_anthropic(user_description, api_key, model)
    else:
        return {
            'success': False,
            'message': f'ارائه‌دهنده نامعتبر: {provider}',
            'filename': None,
            'code': None
        }
    
    if not generated_code:
        return {
            'success': False,
            'message': 'خطا در تولید کد از AI',
            'filename': None,
            'code': None
        }
    
    # استخراج نام فایل اگر مشخص نشده
    if not filename:
        filename = extract_test_name(generated_code)
        if not filename:
            filename = 'custom_test'
    
    # ذخیره فایل
    success = save_generated_test(generated_code, filename, queries_dir)
    
    if success:
        return {
            'success': True,
            'message': 'آزمون با موفقیت تولید و ذخیره شد',
            'filename': filename if filename.endswith('.py') else f'{filename}.py',
            'code': generated_code
        }
    else:
        return {
            'success': False,
            'message': 'خطا در ذخیره فایل',
            'filename': filename,
            'code': generated_code
        }
