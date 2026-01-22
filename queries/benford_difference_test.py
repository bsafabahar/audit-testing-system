"""
آزمون تفاضل بنفورد
Benford's Law Difference Test

این آزمون تفاضل بین فراوانی مشاهده‌شده و مورد انتظار را محاسبه می‌کند.
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_string
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
from collections import Counter
import math


BENFORD_EXPECTED = {
    1: 0.301, 2: 0.176, 3: 0.125, 4: 0.097, 5: 0.079,
    6: 0.067, 7: 0.058, 8: 0.051, 9: 0.046
}


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_string('columnName', 'نام ستون برای آزمون', default_value='Debit')
    ]
    
    result_schema = schema(
        col('Metric', 'معیار', 'string'),
        col('Value', 'مقدار', 'number'),
        col('Interpretation', 'تفسیر', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def get_first_digit(value: float) -> int:
    """استخراج رقم اول"""
    if value <= 0:
        return 0
    abs_val = abs(value)
    while abs_val >= 10:
        abs_val = abs_val / 10
    return int(abs_val)


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون تفاضل بنفورد"""
    
    column_name = get_parameter('columnName', 'Debit')
    
    query = session.query(Transaction)
    results = query.all()
    
    # استخراج رقم اول
    first_digits = []
    for t in results:
        if column_name == 'Debit' and t.Debit and t.Debit > 0:
            first_digits.append(get_first_digit(t.Debit))
        elif column_name == 'Credit' and t.Credit and t.Credit > 0:
            first_digits.append(get_first_digit(t.Credit))
    
    digit_counts = Counter(first_digits)
    total_count = len(first_digits)
    
    if total_count == 0:
        return []
    
    # محاسبه MAD (Mean Absolute Deviation)
    mad_sum = 0
    squared_diff_sum = 0
    
    for digit in range(1, 10):
        actual_prop = digit_counts.get(digit, 0) / total_count
        expected_prop = BENFORD_EXPECTED[digit]
        diff = abs(actual_prop - expected_prop)
        mad_sum += diff
        squared_diff_sum += diff ** 2
    
    mad = mad_sum / 9
    rmsd = math.sqrt(squared_diff_sum / 9)
    
    # تفسیر MAD
    if mad < 0.006:
        interpretation = 'مطابقت کامل با بنفورد'
    elif mad < 0.012:
        interpretation = 'مطابقت قابل قبول'
    elif mad < 0.015:
        interpretation = 'مطابقت نزدیک به قابل قبول'
    else:
        interpretation = 'عدم مطابقت - مشکوک'
    
    data = [
        {
            'Metric': 'MAD (Mean Absolute Deviation)',
            'Value': round(mad, 6),
            'Interpretation': interpretation
        },
        {
            'Metric': 'RMSD (Root Mean Square Deviation)',
            'Value': round(rmsd, 6),
            'Interpretation': 'جذر میانگین مجذورات انحراف'
        },
        {
            'Metric': 'Total Transactions',
            'Value': total_count,
            'Interpretation': f'تعداد کل تراکنش‌های تحلیل‌شده'
        }
    ]
    
    return data
