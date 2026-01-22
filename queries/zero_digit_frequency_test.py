"""
آزمون فراوانی ارقام صفر
Zero Digit Frequency Test

این آزمون فراوانی رقم صفر در اعداد را تحلیل می‌کند.
فراوانی غیرعادی رقم صفر ممکن است نشانه دستکاری باشد.
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
        param_number('expectedPercent', 'درصد مورد انتظار صفر', default_value=10.0)
    ]
    
    result_schema = schema(
        col('DigitPosition', 'موقعیت رقم', 'string'),
        col('ZeroCount', 'تعداد صفر', 'integer'),
        col('TotalCount', 'تعداد کل', 'integer'),
        col('ActualPercent', 'درصد واقعی', 'percent'),
        col('ExpectedPercent', 'درصد مورد انتظار', 'percent'),
        col('Difference', 'تفاضل', 'percent'),
        col('Status', 'وضعیت', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون فراوانی ارقام صفر"""
    
    column_name = get_parameter('columnName', 'Debit')
    expected_percent = get_parameter('expectedPercent', 10.0)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # جمع‌آوری ارقام
    digit_positions = {
        'ones': [],
        'tens': [],
        'hundreds': [],
        'thousands': []
    }
    
    for t in results:
        amount = t.Debit if column_name == 'Debit' else t.Credit
        
        if amount and amount > 0:
            amount_str = str(int(amount))
            length = len(amount_str)
            
            if length >= 1:
                digit_positions['ones'].append(amount_str[-1])
            if length >= 2:
                digit_positions['tens'].append(amount_str[-2])
            if length >= 3:
                digit_positions['hundreds'].append(amount_str[-3])
            if length >= 4:
                digit_positions['thousands'].append(amount_str[-4])
    
    # تحلیل فراوانی
    data = []
    position_names = {
        'ones': 'یکان',
        'tens': 'دهگان',
        'hundreds': 'صدگان',
        'thousands': 'هزارگان'
    }
    
    for position, digits in digit_positions.items():
        if digits:
            zero_count = digits.count('0')
            total_count = len(digits)
            actual_percent = (zero_count / total_count) * 100
            difference = actual_percent - expected_percent
            
            status = 'عادی'
            if difference > 10:
                status = 'صفر بیش از حد'
            elif difference < -10:
                status = 'صفر کمتر از حد'
            
            row = {
                'DigitPosition': position_names[position],
                'ZeroCount': zero_count,
                'TotalCount': total_count,
                'ActualPercent': round(actual_percent, 2),
                'ExpectedPercent': round(expected_percent, 2),
                'Difference': round(difference, 2),
                'Status': status
            }
            data.append(row)
    
    return data
