"""
تحلیل رقم دوم بنفورد
Benford Second Digit Analysis

این آزمون توزیع رقم دوم (از سمت چپ) اعداد را با قانون بنفورد مقایسه می‌کند.
قانون بنفورد نشان می‌دهد که در داده‌های طبیعی، رقم دوم نیز توزیع خاصی دارد.
این آزمون برای تشخیص ناهنجاری‌ها و احتمال تقلب در داده‌های مالی استفاده می‌شود.
"""

from typing import List, Dict, Any
from collections import Counter
from models import Transaction
from parameters import param_string, param_number
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession


# توزیع بنفورد مورد انتظار برای رقم دوم
BENFORD_SECOND_DIGIT = {
    0: 0.1197,
    1: 0.1139,
    2: 0.1088,
    3: 0.1054,
    4: 0.1025,
    5: 0.1002,
    6: 0.0978,
    7: 0.0957,
    8: 0.0940,
    9: 0.0926,
}


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    
    parameters = [
        param_string('columnName', 'نام ستون مبلغ (Debit یا Credit)', default_value='Debit'),
        param_number('minimumAmount', 'حداقل مبلغ برای شمول در آزمون', default_value=10),
        param_number('significanceLevel', 'سطح معنی‌داری برای تشخیص انحراف (0-1)', default_value=0.05),
    ]
    
    result_schema = schema(
        col('SecondDigit', 'رقم دوم (0-9)', 'integer'),
        col('ObservedCount', 'تعداد مشاهده شده', 'integer'),
        col('ObservedPercent', 'درصد مشاهده شده', 'percent'),
        col('ExpectedPercent', 'درصد مورد انتظار (بنفورد)', 'percent'),
        col('Difference', 'اختلاف درصدی', 'percent'),
        col('ChiSquareComponent', 'مؤلفه کای‌اسکوئر', 'number'),
        col('Status', 'وضعیت انحراف', 'string'),
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def extract_second_digit(amount: float) -> int:
    """استخراج رقم دوم از یک عدد"""
    # تبدیل به رشته و حذف نقاط اعشار
    amount_str = str(abs(int(amount))).lstrip('0')
    
    # اگر عدد کمتر از 10 است، رقم دوم 0 است
    if len(amount_str) < 2:
        return 0
    
    # بازگشت رقم دوم
    return int(amount_str[1])


def calculate_chi_square_component(observed: int, expected_percent: float, total: int) -> float:
    """محاسبه مؤلفه کای‌اسکوئر"""
    expected_count = expected_percent * total
    
    if expected_count == 0:
        return 0
    
    chi_component = ((observed - expected_count) ** 2) / expected_count
    return round(chi_component, 6)


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون تحلیل رقم دوم بنفورد"""
    
    # دریافت پارامترها
    column_name = get_parameter('columnName', 'Debit')
    minimum_amount = get_parameter('minimumAmount', 10)
    significance_level = get_parameter('significanceLevel', 0.05)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    if not results:
        return [{
            'SecondDigit': 0,
            'ObservedCount': 0,
            'ObservedPercent': 0.0,
            'ExpectedPercent': 0.0,
            'Difference': 0.0,
            'ChiSquareComponent': 0.0,
            'Status': 'ERROR: No transactions found',
        }]
    
    # استخراج مبالغ و رقم دوم
    second_digits = []
    
    for t in results:
        # انتخاب ستون مبلغ
        if column_name == 'Debit':
            amount = t.Debit if hasattr(t, 'Debit') else None
        else:
            amount = t.Credit if hasattr(t, 'Credit') else None
        
        # بررسی معتبر بودن مبلغ
        if not amount or amount < minimum_amount:
            continue
        
        # استخراج رقم دوم
        second_digit = extract_second_digit(amount)
        second_digits.append(second_digit)
    
    # بررسی حداقل داده
    if len(second_digits) < 30:
        return [{
            'SecondDigit': 0,
            'ObservedCount': 0,
            'ObservedPercent': 0.0,
            'ExpectedPercent': 0.0,
            'Difference': 0.0,
            'ChiSquareComponent': 0.0,
            'Status': f'ERROR: Not enough transactions (minimum 30, found {len(second_digits)})',
        }]
    
    # شمارش فراوانی رقم دوم
    digit_counter = Counter(second_digits)
    total_count = len(second_digits)
    
    # ساخت خروجی
    data = []
    total_chi_square = 0
    
    for digit in range(10):
        observed_count = digit_counter.get(digit, 0)
        observed_percent = (observed_count / total_count) if total_count > 0 else 0
        expected_percent = BENFORD_SECOND_DIGIT[digit]
        difference = observed_percent - expected_percent
        chi_component = calculate_chi_square_component(observed_count, expected_percent, total_count)
        total_chi_square += chi_component
        
        # تعیین وضعیت انحراف
        if abs(difference) > significance_level:
            status = 'DEVIATION'
        else:
            status = 'NORMAL'
        
        row = {
            'SecondDigit': digit,
            'ObservedCount': observed_count,
            'ObservedPercent': round(observed_percent * 100, 2),
            'ExpectedPercent': round(expected_percent * 100, 2),
            'Difference': round(difference * 100, 2),
            'ChiSquareComponent': chi_component,
            'Status': status,
        }
        data.append(row)
    
    # افزودن ردیف خلاصه
    data.append({
        'SecondDigit': -1,
        'ObservedCount': total_count,
        'ObservedPercent': 100.0,
        'ExpectedPercent': 100.0,
        'Difference': 0.0,
        'ChiSquareComponent': round(total_chi_square, 6),
        'Status': 'SUMMARY',
    })
    
    return data

---MARKDOWN_FILE---



```markdown
# تحلیل رقم دوم بنفورد

## 🎯 هدف آزمون

این آزمون توزیع رقم دوم (رقم سمت چپ دوم) اعداد مالی را با الگوی مورد انتظار قانون بنفورد مقایسه می‌کند. هدف شناسایی انحرافات غیرعادی در داده‌های مالی است که می‌تواند نشانه‌ای از تقلب، خطا یا ناهنجاری‌های سیستمی باشد. این آزمون بر اساس مشاهده تجربی است که در داده‌های طبیعی و غیرتقلبی، رقم دوم نیز توزیع خاصی دارد.

## 💡 چرا از این آزمون در حسابرسی استفاده می‌شود؟

### کاربردهای حسابرسی:

1. **تشخیص تقلب مالی**: انحرافات از الگوی بنفورد می‌تواند نشانه‌ای از دستکاری داده‌های مالی باشد
2. **کنترل کیفیت داده‌ها**: بررسی اینکه داده‌های وارد شده به سیستم طبیعی و معقول هستند
3. **شناسایی خطاهای ورود داده**: خطاهای سیستمی در ورود اعداد اغلب الگوی متفاوتی ایجاد می‌کنند
4. **بررسی صحت تخصیص هزینه‌ها**: مبالغ تخصیص شده باید از الگوی طبیعی پیروی کنند
5. **تحلیل معاملات مشکوک**: معاملات غیرعادی اغلب رقم دوم غیرعادی دارند

### مثال‌های کاربردی:

- بررسی صحت مبالغ فاکتورهای فروش و خریداری
- تحلیل مبالغ حقوق و دستمزد کارکنان
- کنترل مبالغ هزینه‌های سفر و جابجایی
- بررسی صحت مبالغ بدهی‌ها و طلب‌ها
- تحلیل معاملات بانکی و انتقالات پول

## 📥 پارامترهای ورودی

### 1. columnName (نام ستون مبلغ)
- **نوع**: رشته (String)
- **الزامی**: خیر
- **توضیحات**: نام ستونی که حاوی مبالغ مورد تحلیل است
- **مقدار پیش‌فرض**: `Debit` (بدهکار)
- **مقادیر مجاز**:
  - `Debit`: ستون بدهکار
  - `Credit`: ستون بستانکار
- **راهنما**: بسته به نوع تحلیل، می‌توانید بدهکار یا بستانکار را انتخاب کنید
- **نکته**: اگر ستون دیگری دارید، نام آن را وارد کنید

### 2. minimumAmount (حداقل مبلغ)
- **نوع**: عدد (Number)
- **الزامی**: خیر
- **توضیحات**: حداقل مبلغی که در آزمون شامل می‌شود (مبالغ کمتر نادیده گرفته می‌شوند)
- **مقدار پیش‌فرض**: `10`
- **راهنما**: مبالغ خیلی کوچک اغلب الگوی متفاوتی دارند، بنابراین آنها را حذف کنید
- **نکته**: مقدار بیشتر = نتایج دقیق‌تر اما نمونه کوچک‌تر

### 3. significanceLevel (سطح معنی‌داری)
- **نوع**: عدد (Number)
- **الزامی**: خیر
- **توضیحات**: آستانه انحراف برای تشخیص ناهنجاری (بین 0 و 1)
- **مقدار پیش‌فرض**: `0.05` (5%)
- **مقادیر مجاز**:
  - `0.01`: سخت‌گیرانه (1%)
  - `0.05`: متعادل (5%)
  - `0.10`: متساهل (10%)
- **راهنما**: مقدار کمتر = حساسیت بیشتر به انحرافات

## 📤 پارامترهای خروجی

### ستون‌های خروجی:

1. **SecondDigit (رقم دوم)**
   - رقم دوم از سمت چپ (0 تا 9)
   - برای اعدادی که کمتر از 10 هستند، رقم دوم برابر 0 است
   - مثال: در عدد 1234، رقم دوم = 2

2. **ObservedCount (تعداد مشاهده شده)**
   - تعداد مواردی که رقم دوم آنها برابر این رقم است
   - نشان می‌دهد این رقم چند بار در داده‌ها ظاهر شده است

3. **ObservedPercent (درصد مشاهده شده)**
   - درصد فراوانی این رقم دوم در داده‌های واقعی
   - محاسبه: (تعداد مشاهده شده / کل معاملات) × 100

4. **ExpectedPercent (درصد مورد انتظار)**
   - درصد فراوانی مورد انتظار بر اساس قانون بنفورد
   - این مقادیر ثابت و از قبل تعریف شده‌اند
   - مثال: رقم 0 باید 11.97% ظاهر شود

5. **Difference (اختلاف درصدی)**
   - تفاوت بین درصد مشاهده شده و مورد انتظار
   - محاسبه: ObservedPercent - ExpectedPercent
   - مقادیر منفی = کمتر از انتظار
   - مق