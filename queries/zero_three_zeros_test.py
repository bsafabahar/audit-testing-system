"""
آزمون سه رقم صفر
Three Zeros Test

این آزمون تراکنش‌هایی را شناسایی می‌کند که دارای سه رقم صفر متوالی هستند.
این الگو ممکن است نشانه‌ای از تراکنش‌های دستی یا ساختگی باشد.
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_string
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_string('columnName', 'نام ستون برای آزمون', default_value='Debit')
    ]
    
    result_schema = schema(
        col('TransactionID', 'شناسه تراکنش', 'string'),
        col('Amount', 'مبلغ', 'money'),
        col('AmountString', 'مبلغ به صورت متن', 'string'),
        col('ZeroCount', 'تعداد صفر', 'integer'),
        col('TransactionDate', 'تاریخ تراکنش', 'date')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون سه رقم صفر"""
    
    column_name = get_parameter('columnName', 'Debit')
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    data = []
    for t in results:
        amount = t.Debit if column_name == 'Debit' else t.Credit
        
        if amount and amount > 0:
            amount_str = str(int(amount))
            
            # بررسی وجود سه صفر متوالی
            if '000' in amount_str:
                zero_count = amount_str.count('0')
                
                row = {
                    'TransactionID': str(t.TransactionID) if hasattr(t, 'TransactionID') else '',
                    'Amount': round(amount, 2),
                    'AmountString': amount_str,
                    'ZeroCount': zero_count,
                    'TransactionDate': t.TransactionDate.strftime('%Y-%m-%d') if hasattr(t, 'TransactionDate') and t.TransactionDate else ''
                }
                data.append(row)
    
    # مرتب‌سازی بر اساس تعداد صفر
    data.sort(key=lambda x: x['ZeroCount'], reverse=True)
    
    return data
