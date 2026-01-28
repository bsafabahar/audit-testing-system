"""
آزمون دو رقم اول بنفورد
First Two Digits Test - Benford's Law

این آزمون دو رقم اول هر عدد را استخراج کرده و با توزیع بنفورد مقایسه می‌کند.
مفید برای تشخیص شرکت‌های کاغذی و حسابات ساختگی.
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_string, param_number
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
from collections import Counter
import math


def benford_two_digit_expected(d: int) -> float:
    """محاسبه احتمال مورد انتظار برای دو رقم اول در قانون بنفورد"""
    if d < 10 or d > 99:
        return 0
    return math.log10(1 + 1/d)


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_string('columnName', 'نام ستون برای آزمون', default_value='Debit'),
        param_number('topN', 'تعداد رکوردهای برتر', default_value=20)
    ]
    
    result_schema = schema(
        col('TwoDigits', 'دو رقم', 'integer'),
        col('ActualCount', 'تعداد واقعی', 'integer'),
        col('ExpectedCount', 'تعداد مورد انتظار', 'number'),
        col('ActualPercent', 'درصد واقعی', 'percent'),
        col('ExpectedPercent', 'درصد مورد انتظار', 'percent'),
        col('Deviation', 'انحراف', 'percent'),
        col('IsSuspicious', 'مشکوک', 'boolean')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def get_first_two_digits(value: float) -> int:
    """استخراج دو رقم اول یک عدد"""
    if value <= 0:
        return 0
    
    abs_val = abs(value)
    
    # یافتن دو رقم اول
    while abs_val >= 100:
        abs_val = abs_val / 10
    
    while abs_val < 10:
        abs_val = abs_val * 10
    
    return int(abs_val)


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون دو رقم اول بنفورد"""
    
    column_name = get_parameter('columnName', 'Debit')
    top_n = get_parameter('topN', 20)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # استخراج دو رقم اول
    two_digits = []
    for t in results:
        if column_name == 'Debit' and t.Debit and t.Debit > 0:
            two_digits.append(get_first_two_digits(t.Debit))
        elif column_name == 'Credit' and t.Credit and t.Credit > 0:
            two_digits.append(get_first_two_digits(t.Credit))
    
    # شمارش فراوانی
    digit_counts = Counter(two_digits)
    total_count = len(two_digits)
    
    if total_count == 0:
        return []
    
    # محاسبه آمار برای هر ترکیب
    data = []
    for digits in range(10, 100):
        actual_count = digit_counts.get(digits, 0)
        expected_prob = benford_two_digit_expected(digits)
        expected_count = total_count * expected_prob
        
        if actual_count > 0 or expected_count > 1:  # فقط موارد مهم
            actual_percent = (actual_count / total_count) * 100
            expected_percent = expected_prob * 100
            deviation = actual_percent - expected_percent
            
            # مشکوک اگر انحراف بیش از 50% باشد
            is_suspicious = abs(deviation) > (expected_percent * 0.5)
            
            row = {
                'TwoDigits': digits,
                'ActualCount': actual_count,
                'ExpectedCount': round(expected_count, 2),
                'ActualPercent': round(actual_percent, 3),
                'ExpectedPercent': round(expected_percent, 3),
                'Deviation': round(deviation, 3),
                'IsSuspicious': is_suspicious
            }
            data.append(row)
    
    # مرتب‌سازی بر اساس انحراف
    data.sort(key=lambda x: abs(x['Deviation']), reverse=True)
    
    return data[:top_n]
