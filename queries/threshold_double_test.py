"""
آزمون دو برابر
Double Test / Two Times Multiplier

شناسایی موارد بیش از ۲ برابر میانگین.
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_string, param_number
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
import statistics


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_string('columnName', 'نام ستون برای آزمون', default_value='Debit'),
        param_number('limit', 'تعداد رکورد', default_value=100)
    ]
    
    result_schema = schema(
        col('Id', 'شناسه', 'integer'),
        col('DocumentDate', 'تاریخ سند', 'date'),
        col('DocumentNumber', 'شماره سند', 'integer'),
        col('AccountCode', 'کد حساب', 'string'),
        col('Amount', 'مبلغ', 'currency'),
        col('Average', 'میانگین', 'currency'),
        col('DoubleThreshold', 'آستانه دو برابر', 'currency'),
        col('ExcessFactor', 'ضریب اضافی', 'number'),
        col('RiskLevel', 'سطح ریسک', 'string'),
        col('Description', 'شرح', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون دو برابر"""
    
    column_name = get_parameter('columnName', 'Debit')
    limit = get_parameter('limit', 100)
    
    query = session.query(Transaction)
    results = query.all()
    
    # استخراج مبالغ
    amounts = []
    for t in results:
        if column_name == 'Debit' and t.Debit and t.Debit > 0:
            amounts.append(t.Debit)
        elif column_name == 'Credit' and t.Credit and t.Credit > 0:
            amounts.append(t.Credit)
    
    if not amounts:
        return []
    
    # محاسبه میانگین و آستانه
    average = statistics.mean(amounts)
    double_threshold = average * 2
    
    # یافتن موارد بیش از دو برابر
    data = []
    for t in results:
        amount = 0
        if column_name == 'Debit' and t.Debit:
            amount = t.Debit
        elif column_name == 'Credit' and t.Credit:
            amount = t.Credit
        
        if amount > double_threshold:
            excess_factor = amount / average if average > 0 else 0
            
            # تعیین سطح ریسک
            if excess_factor > 5:
                risk_level = 'بسیار بالا'
            elif excess_factor > 3:
                risk_level = 'بالا'
            else:
                risk_level = 'متوسط'
            
            row = {
                'Id': t.Id,
                'DocumentDate': t.DocumentDate.strftime('%Y-%m-%d') if t.DocumentDate else '',
                'DocumentNumber': t.DocumentNumber,
                'AccountCode': t.AccountCode,
                'Amount': float(amount),
                'Average': round(average, 2),
                'DoubleThreshold': round(double_threshold, 2),
                'ExcessFactor': round(excess_factor, 2),
                'RiskLevel': risk_level,
                'Description': t.Description[:50] if t.Description else ''
            }
            data.append(row)
    
    # مرتب‌سازی بر اساس ضریب اضافی
    data.sort(key=lambda x: x['ExcessFactor'], reverse=True)
    
    return data[:limit]
