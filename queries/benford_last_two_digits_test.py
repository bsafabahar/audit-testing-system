"""
آزمون رقم آخر بنفورد
Last Two Digits Test - Benford's Law

این آزمون دو رقم آخر اعداد را تحلیل می‌کند.
در حالت طبیعی، دو رقم آخر باید توزیع یکنواخت داشته باشند.
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_string, param_number
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
from collections import Counter


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_string('columnName', 'نام ستون برای آزمون', default_value='Debit'),
        param_number('deviationThreshold', 'آستانه انحراف (درصد)', default_value=50)
    ]
    
    result_schema = schema(
        col('LastTwoDigits', 'دو رقم آخر', 'string'),
        col('ActualCount', 'تعداد واقعی', 'integer'),
        col('ExpectedCount', 'تعداد مورد انتظار', 'number'),
        col('ActualPercent', 'درصد واقعی', 'percent'),
        col('Deviation', 'انحراف از میانگین', 'percent'),
        col('IsSuspicious', 'مشکوک', 'boolean')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def get_last_two_digits(value: float) -> str:
    """استخراج دو رقم آخر یک عدد"""
    if value <= 0:
        return '00'
    
    # تبدیل به عدد صحیح
    int_val = int(abs(value))
    
    # گرفتن دو رقم آخر
    last_two = int_val % 100
    
    return f'{last_two:02d}'


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون دو رقم آخر"""
    
    column_name = get_parameter('columnName', 'Debit')
    deviation_threshold = get_parameter('deviationThreshold', 50)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # استخراج دو رقم آخر
    last_digits = []
    for t in results:
        if column_name == 'Debit' and t.Debit and t.Debit > 0:
            last_digits.append(get_last_two_digits(t.Debit))
        elif column_name == 'Credit' and t.Credit and t.Credit > 0:
            last_digits.append(get_last_two_digits(t.Credit))
    
    # شمارش فراوانی
    digit_counts = Counter(last_digits)
    total_count = len(last_digits)
    
    if total_count == 0:
        return []
    
    # توزیع یکنواخت: هر ترکیب باید 1% باشد
    expected_count = total_count / 100
    expected_percent = 1.0
    
    # تحلیل
    data = []
    for digits, actual_count in digit_counts.most_common():
        actual_percent = (actual_count / total_count) * 100
        deviation = ((actual_percent - expected_percent) / expected_percent) * 100
        
        is_suspicious = abs(deviation) > deviation_threshold
        
        row = {
            'LastTwoDigits': digits,
            'ActualCount': actual_count,
            'ExpectedCount': round(expected_count, 2),
            'ActualPercent': round(actual_percent, 2),
            'Deviation': round(deviation, 2),
            'IsSuspicious': is_suspicious
        }
        data.append(row)
    
    # مرتب‌سازی بر اساس انحراف
    data.sort(key=lambda x: abs(x['Deviation']), reverse=True)
    
    return data
