"""
آزمون ۵۰ درصد
Fifty Percent Rule / Threshold Test (50%)

شناسایی موارد که ۵۰ درصد بیشتر یا کمتر از میانگین هستند.
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
        col('DeviationPercent', 'درصد انحراف', 'percent'),
        col('Description', 'شرح', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون ۵۰ درصد"""
    
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
    
    # محاسبه میانگین
    average = statistics.mean(amounts)
    threshold_upper = average * 1.5
    threshold_lower = average * 0.5
    
    # یافتن موارد غیرعادی
    data = []
    for t in results:
        amount = 0
        if column_name == 'Debit' and t.Debit:
            amount = t.Debit
        elif column_name == 'Credit' and t.Credit:
            amount = t.Credit
        
        if amount > 0 and (amount > threshold_upper or amount < threshold_lower):
            deviation_percent = ((amount - average) / average) * 100
            
            row = {
                'Id': t.Id,
                'DocumentDate': t.DocumentDate.strftime('%Y-%m-%d') if t.DocumentDate else '',
                'DocumentNumber': t.DocumentNumber,
                'AccountCode': t.AccountCode,
                'Amount': float(amount),
                'Average': round(average, 2),
                'DeviationPercent': round(deviation_percent, 2),
                'Description': t.Description[:50] if t.Description else ''
            }
            data.append(row)
    
    # مرتب‌سازی بر اساس مبلغ
    data.sort(key=lambda x: abs(x['DeviationPercent']), reverse=True)
    
    return data[:limit]
