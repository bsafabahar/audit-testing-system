"""
آزمون نوع داده
Data Type Test

این آزمون انطباق نوع داده‌ها را بررسی می‌کند.
داده‌هایی که با نوع مورد انتظار مطابقت ندارند، شناسایی می‌شوند.
"""
from typing import List, Dict, Any
from models import Transaction
from schema import col, schema
from types_definitions import QueryDefinition
from database import ReadOnlySession


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = []
    
    result_schema = schema(
        col('TransactionID', 'شناسه تراکنش', 'string'),
        col('Field', 'فیلد', 'string'),
        col('Value', 'مقدار', 'string'),
        col('ExpectedType', 'نوع مورد انتظار', 'string'),
        col('ActualType', 'نوع واقعی', 'string'),
        col('Issue', 'مشکل', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون نوع داده"""
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    data = []
    
    for t in results:
        issues = []
        
        # بررسی فیلدهای عددی
        numeric_fields = ['Debit', 'Credit', 'UnitPrice', 'Quantity']
        for field in numeric_fields:
            if hasattr(t, field):
                value = getattr(t, field)
                if value is not None:
                    if not isinstance(value, (int, float)):
                        issues.append({
                            'field': field,
                            'value': str(value),
                            'expected': 'number',
                            'actual': type(value).__name__,
                            'issue': 'نوع عددی مورد انتظار است'
                        })
        
        # بررسی فیلدهای تاریخ
        date_fields = ['TransactionDate']
        for field in date_fields:
            if hasattr(t, field):
                value = getattr(t, field)
                if value is not None:
                    from datetime import datetime, date
                    if not isinstance(value, (datetime, date)):
                        issues.append({
                            'field': field,
                            'value': str(value),
                            'expected': 'date',
                            'actual': type(value).__name__,
                            'issue': 'نوع تاریخ مورد انتظار است'
                        })
        
        # بررسی فیلدهای متنی
        string_fields = ['Description', 'AccountCode']
        for field in string_fields:
            if hasattr(t, field):
                value = getattr(t, field)
                if value is not None:
                    if not isinstance(value, str):
                        issues.append({
                            'field': field,
                            'value': str(value),
                            'expected': 'string',
                            'actual': type(value).__name__,
                            'issue': 'نوع متنی مورد انتظار است'
                        })
        
        # افزودن مسائل به خروجی
        for issue in issues:
            row = {
                'TransactionID': str(t.TransactionID) if hasattr(t, 'TransactionID') else '',
                'Field': issue['field'],
                'Value': issue['value'][:100],  # محدود کردن طول
                'ExpectedType': issue['expected'],
                'ActualType': issue['actual'],
                'Issue': issue['issue']
            }
            data.append(row)
    
    return data
