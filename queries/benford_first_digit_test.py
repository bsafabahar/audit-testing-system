"""
آزمون رقم اول بنفورد
First Digit Test - Benford's Law

این آزمون رقم اول هر عدد را استخراج کرده و با توزیع بنفورد مقایسه می‌کند.
برای تشخیص دستکاری در اعداد مالی استفاده می‌شود.
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


# توزیع بنفورد مورد انتظار
BENFORD_EXPECTED = {
    1: 0.301,
    2: 0.176,
    3: 0.125,
    4: 0.097,
    5: 0.079,
    6: 0.067,
    7: 0.058,
    8: 0.051,
    9: 0.046
}


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_string('columnName', 'نام ستون برای آزمون', default_value='Debit'),
        param_number('chiSquareThreshold', 'آستانه Chi-Square', default_value=15.51)
    ]
    
    result_schema = schema(
        col('Digit', 'رقم', 'integer'),
        col('ActualCount', 'تعداد واقعی', 'integer'),
        col('ExpectedCount', 'تعداد مورد انتظار', 'number'),
        col('ActualPercent', 'درصد واقعی', 'percent'),
        col('ExpectedPercent', 'درصد مورد انتظار', 'percent'),
        col('Difference', 'تفاضل', 'percent'),
        col('ChiSquareContribution', 'سهم Chi-Square', 'number')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def get_first_digit(value: float) -> int:
    """استخراج رقم اول یک عدد"""
    if value <= 0:
        return 0
    
    # حذف قسمت اعشار و علامت
    abs_val = abs(value)
    
    # یافتن رقم اول
    while abs_val >= 10:
        abs_val = abs_val / 10
    
    return int(abs_val)


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون بنفورد رقم اول"""
    
    column_name = get_parameter('columnName', 'Debit')
    chi_threshold = get_parameter('chiSquareThreshold', 15.51)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # استخراج رقم اول
    first_digits = []
    for t in results:
        if column_name == 'Debit' and t.Debit and t.Debit > 0:
            first_digits.append(get_first_digit(t.Debit))
        elif column_name == 'Credit' and t.Credit and t.Credit > 0:
            first_digits.append(get_first_digit(t.Credit))
    
    # شمارش فراوانی
    digit_counts = Counter(first_digits)
    total_count = len(first_digits)
    
    if total_count == 0:
        return []
    
    # محاسبه Chi-Square
    chi_square_total = 0
    data = []
    
    for digit in range(1, 10):
        actual_count = digit_counts.get(digit, 0)
        expected_count = total_count * BENFORD_EXPECTED[digit]
        actual_percent = (actual_count / total_count) * 100
        expected_percent = BENFORD_EXPECTED[digit] * 100
        difference = actual_percent - expected_percent
        
        # محاسبه سهم Chi-Square
        if expected_count > 0:
            chi_contribution = ((actual_count - expected_count) ** 2) / expected_count
        else:
            chi_contribution = 0
        
        chi_square_total += chi_contribution
        
        row = {
            'Digit': digit,
            'ActualCount': actual_count,
            'ExpectedCount': round(expected_count, 2),
            'ActualPercent': round(actual_percent, 2),
            'ExpectedPercent': round(expected_percent, 2),
            'Difference': round(difference, 2),
            'ChiSquareContribution': round(chi_contribution, 4)
        }
        data.append(row)
    
    # افزودن ردیف خلاصه
    data.append({
        'Digit': 0,
        'ActualCount': total_count,
        'ExpectedCount': total_count,
        'ActualPercent': 100.0,
        'ExpectedPercent': 100.0,
        'Difference': 0.0,
        'ChiSquareContribution': round(chi_square_total, 4)
    })
    
    return data
