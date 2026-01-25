"""
آزمون پیشرفته بنفورد با تحلیل AI
Advanced Benford Analysis with AI

این آزمون علاوه بر تست سنتی بنفورد، تحلیل انحراف از توزیع نرمال برای ارقام مرتبه دوم و سوم
تراکنش‌های مبالغ بالا را انجام می‌دهد.
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_number, param_string
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
from collections import Counter
import math


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_string('columnName', 'نام ستون مبلغ', default_value='Debit'),
        param_number('topPercentile', 'صدک بالای مبالغ', default_value=90),
        param_number('chiSquareThreshold', 'آستانه Chi-Square', default_value=15.51)
    ]
    
    result_schema = schema(
        col('DigitPosition', 'موقعیت رقم', 'string'),
        col('Digit', 'رقم', 'string'),
        col('ActualCount', 'تعداد واقعی', 'integer'),
        col('ExpectedCount', 'تعداد مورد انتظار', 'number'),
        col('ActualPercent', 'درصد واقعی', 'number'),
        col('ExpectedPercent', 'درصد مورد انتظار', 'number'),
        col('Difference', 'تفاضل', 'number'),
        col('ChiSquareContribution', 'سهم Chi-Square', 'number'),
        col('DeviationSeverity', 'شدت انحراف', 'string'),
        col('AnalysisType', 'نوع تحلیل', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


# توزیع بنفورد برای رقم اول
BENFORD_FIRST = {str(i): math.log10(1 + 1/i) for i in range(1, 10)}

# توزیع یکنواخت برای رقم دوم و سوم (0-9)
UNIFORM_PROBABILITY = 1.0 / 10
UNIFORM_DIST = {str(i): UNIFORM_PROBABILITY for i in range(0, 10)}


def get_digit_at_position(value: float, position: int) -> str:
    """
    استخراج رقم در موقعیت مشخص
    position 0 = رقم اول, 1 = رقم دوم, 2 = رقم سوم
    """
    if value <= 0:
        return None
    
    # حذف قسمت اعشار و گرفتن قدر مطلق
    abs_val = int(abs(value))
    str_val = str(abs_val)
    
    if position >= len(str_val):
        return None
    
    return str_val[position]


def calculate_chi_square(actual_counts: Dict[str, int], expected_dist: Dict[str, float], total: int) -> float:
    """محاسبه Chi-Square"""
    chi_square = 0.0
    for digit, expected_prob in expected_dist.items():
        actual_count = actual_counts.get(digit, 0)
        expected_count = total * expected_prob
        
        if expected_count > 0:
            chi_square += ((actual_count - expected_count) ** 2) / expected_count
    
    return chi_square


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون پیشرفته بنفورد"""
    
    column_name = get_parameter('columnName', 'Debit')
    top_percentile = get_parameter('topPercentile', 90)
    chi_threshold = get_parameter('chiSquareThreshold', 15.51)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # استخراج مبالغ
    amounts = []
    for t in results:
        amount = t.Debit if column_name == 'Debit' else t.Credit
        if amount and amount > 0:
            amounts.append(amount)
    
    if len(amounts) < 30:
        return [{
            'DigitPosition': 'ERROR',
            'Digit': '-',
            'ActualCount': 0,
            'ExpectedCount': 0,
            'ActualPercent': 0,
            'ExpectedPercent': 0,
            'Difference': 0,
            'ChiSquareContribution': 0,
            'DeviationSeverity': 'N/A',
            'AnalysisType': 'Not enough transactions (minimum 30)'
        }]
    
    # محاسبه آستانه مبالغ بالا
    amounts_sorted = sorted(amounts)
    threshold_index = int(len(amounts_sorted) * (top_percentile / 100))
    high_amount_threshold = amounts_sorted[threshold_index] if threshold_index < len(amounts_sorted) else amounts_sorted[-1]
    
    # فیلتر مبالغ بالا
    high_amounts = [a for a in amounts if a >= high_amount_threshold]
    
    if len(high_amounts) < 10:
        high_amounts = amounts  # اگر تراکنش کافی نداریم، از همه استفاده کن
    
    data = []
    
    # تحلیل رقم اول (تمام داده‌ها) - تست سنتی بنفورد
    first_digits = []
    for amount in amounts:
        digit = get_digit_at_position(amount, 0)
        if digit and digit != '0':
            first_digits.append(digit)
    
    if first_digits:
        digit_counts_first = Counter(first_digits)
        total_first = len(first_digits)
        
        for digit in range(1, 10):
            digit_str = str(digit)
            actual_count = digit_counts_first.get(digit_str, 0)
            expected_prob = BENFORD_FIRST[digit_str]
            expected_count = total_first * expected_prob
            actual_percent = (actual_count / total_first) * 100 if total_first > 0 else 0
            expected_percent = expected_prob * 100
            difference = actual_percent - expected_percent
            
            chi_contribution = 0
            if expected_count > 0:
                chi_contribution = ((actual_count - expected_count) ** 2) / expected_count
            
            # تعیین شدت انحراف
            abs_diff = abs(difference)
            if abs_diff < 2:
                severity = 'طبیعی'
            elif abs_diff < 5:
                severity = 'متوسط'
            elif abs_diff < 10:
                severity = 'بالا'
            else:
                severity = 'بسیار بالا'
            
            row = {
                'DigitPosition': 'رقم اول',
                'Digit': digit_str,
                'ActualCount': actual_count,
                'ExpectedCount': round(expected_count, 2),
                'ActualPercent': round(actual_percent, 2),
                'ExpectedPercent': round(expected_percent, 2),
                'Difference': round(difference, 2),
                'ChiSquareContribution': round(chi_contribution, 4),
                'DeviationSeverity': severity,
                'AnalysisType': 'بنفورد سنتی'
            }
            data.append(row)
    
    # تحلیل رقم دوم (مبالغ بالا) - تحلیل پیشرفته
    second_digits = []
    for amount in high_amounts:
        digit = get_digit_at_position(amount, 1)
        if digit is not None:
            second_digits.append(digit)
    
    if second_digits:
        digit_counts_second = Counter(second_digits)
        total_second = len(second_digits)
        
        for digit in range(0, 10):
            digit_str = str(digit)
            actual_count = digit_counts_second.get(digit_str, 0)
            expected_prob = UNIFORM_DIST[digit_str]
            expected_count = total_second * expected_prob
            actual_percent = (actual_count / total_second) * 100 if total_second > 0 else 0
            expected_percent = expected_prob * 100
            difference = actual_percent - expected_percent
            
            chi_contribution = 0
            if expected_count > 0:
                chi_contribution = ((actual_count - expected_count) ** 2) / expected_count
            
            # تعیین شدت انحراف (برای توزیع یکنواخت)
            abs_diff = abs(difference)
            if abs_diff < 3:
                severity = 'طبیعی'
            elif abs_diff < 6:
                severity = 'متوسط'
            elif abs_diff < 10:
                severity = 'بالا'
            else:
                severity = 'بسیار بالا'
            
            row = {
                'DigitPosition': 'رقم دوم',
                'Digit': digit_str,
                'ActualCount': actual_count,
                'ExpectedCount': round(expected_count, 2),
                'ActualPercent': round(actual_percent, 2),
                'ExpectedPercent': round(expected_percent, 2),
                'Difference': round(difference, 2),
                'ChiSquareContribution': round(chi_contribution, 4),
                'DeviationSeverity': severity,
                'AnalysisType': f'مبالغ بالا (>{int(high_amount_threshold)})'
            }
            data.append(row)
    
    # تحلیل رقم سوم (مبالغ بالا) - تحلیل پیشرفته
    third_digits = []
    for amount in high_amounts:
        digit = get_digit_at_position(amount, 2)
        if digit is not None:
            third_digits.append(digit)
    
    if third_digits:
        digit_counts_third = Counter(third_digits)
        total_third = len(third_digits)
        
        for digit in range(0, 10):
            digit_str = str(digit)
            actual_count = digit_counts_third.get(digit_str, 0)
            expected_prob = UNIFORM_DIST[digit_str]
            expected_count = total_third * expected_prob
            actual_percent = (actual_count / total_third) * 100 if total_third > 0 else 0
            expected_percent = expected_prob * 100
            difference = actual_percent - expected_percent
            
            chi_contribution = 0
            if expected_count > 0:
                chi_contribution = ((actual_count - expected_count) ** 2) / expected_count
            
            # تعیین شدت انحراف
            abs_diff = abs(difference)
            if abs_diff < 3:
                severity = 'طبیعی'
            elif abs_diff < 6:
                severity = 'متوسط'
            elif abs_diff < 10:
                severity = 'بالا'
            else:
                severity = 'بسیار بالا'
            
            row = {
                'DigitPosition': 'رقم سوم',
                'Digit': digit_str,
                'ActualCount': actual_count,
                'ExpectedCount': round(expected_count, 2),
                'ActualPercent': round(actual_percent, 2),
                'ExpectedPercent': round(expected_percent, 2),
                'Difference': round(difference, 2),
                'ChiSquareContribution': round(chi_contribution, 4),
                'DeviationSeverity': severity,
                'AnalysisType': f'مبالغ بالا (>{int(high_amount_threshold)})'
            }
            data.append(row)
    
    return data
