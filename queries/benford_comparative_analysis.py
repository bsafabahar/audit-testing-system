"""
آزمون مقایسه دوره‌های زمانی بنفورد
Benford's Law Comparative Analysis

این آزمون قانون بنفورد را برای دو سال متوالی مقایسه می‌کند.
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_number
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
from collections import Counter
from datetime import datetime


BENFORD_EXPECTED = {
    1: 0.301, 2: 0.176, 3: 0.125, 4: 0.097, 5: 0.079,
    6: 0.067, 7: 0.058, 8: 0.051, 9: 0.046
}


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_number('year1', 'سال اول', default_value=2024),
        param_number('year2', 'سال دوم', default_value=2025)
    ]
    
    result_schema = schema(
        col('Digit', 'رقم', 'integer'),
        col('Year1Percent', 'درصد سال اول', 'percent'),
        col('Year2Percent', 'درصد سال دوم', 'percent'),
        col('ExpectedPercent', 'درصد مورد انتظار', 'percent'),
        col('Year1Deviation', 'انحراف سال اول', 'percent'),
        col('Year2Deviation', 'انحراف سال دوم', 'percent'),
        col('ChangeInDeviation', 'تغییر در انحراف', 'percent')
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
    """اجرای آزمون مقایسه دوره‌های زمانی"""
    
    year1 = get_parameter('year1', 2024)
    year2 = get_parameter('year2', 2025)
    
    query = session.query(Transaction)
    results = query.all()
    
    # تفکیک داده‌ها بر اساس سال
    year1_digits = []
    year2_digits = []
    
    for t in results:
        if t.DocumentDate:
            year = t.DocumentDate.year
            amount = t.Debit if t.Debit and t.Debit > 0 else 0
            
            if year == year1 and amount > 0:
                year1_digits.append(get_first_digit(amount))
            elif year == year2 and amount > 0:
                year2_digits.append(get_first_digit(amount))
    
    year1_counts = Counter(year1_digits)
    year2_counts = Counter(year2_digits)
    
    year1_total = len(year1_digits)
    year2_total = len(year2_digits)
    
    if year1_total == 0 or year2_total == 0:
        return []
    
    # تحلیل مقایسه‌ای
    data = []
    for digit in range(1, 10):
        year1_percent = (year1_counts.get(digit, 0) / year1_total) * 100
        year2_percent = (year2_counts.get(digit, 0) / year2_total) * 100
        expected_percent = BENFORD_EXPECTED[digit] * 100
        
        year1_deviation = year1_percent - expected_percent
        year2_deviation = year2_percent - expected_percent
        change_in_deviation = year2_deviation - year1_deviation
        
        row = {
            'Digit': digit,
            'Year1Percent': round(year1_percent, 2),
            'Year2Percent': round(year2_percent, 2),
            'ExpectedPercent': round(expected_percent, 2),
            'Year1Deviation': round(year1_deviation, 2),
            'Year2Deviation': round(year2_deviation, 2),
            'ChangeInDeviation': round(change_in_deviation, 2)
        }
        data.append(row)
    
    return data
