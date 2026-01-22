"""
آزمون شفافیت بانکی
Banking Transparency Test

این آزمون شفافیت و کامل بودن اطلاعات تراکنش‌های بانکی را بررسی می‌کند.
تراکنش‌هایی که اطلاعات ناقص دارند، شناسایی می‌شوند.
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
        col('TransactionDate', 'تاریخ تراکنش', 'date'),
        col('Amount', 'مبلغ', 'money'),
        col('MissingFields', 'فیلدهای ناقص', 'string'),
        col('CompletenessScore', 'امتیاز کامل بودن', 'percent'),
        col('TransparencyLevel', 'سطح شفافیت', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون شفافیت بانکی"""
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # فیلدهای مورد انتظار
    required_fields = [
        'TransactionDate',
        'AccountNumber',
        'Description',
        'ReferenceNumber',
        'TransactionType'
    ]
    
    data = []
    
    for t in results:
        missing_fields = []
        fields_present = 0
        
        for field in required_fields:
            if hasattr(t, field):
                value = getattr(t, field)
                if value is not None and value != '':
                    fields_present += 1
                else:
                    missing_fields.append(field)
            else:
                missing_fields.append(field)
        
        completeness = (fields_present / len(required_fields)) * 100
        
        # تعیین سطح شفافیت
        if completeness >= 90:
            transparency = 'عالی'
        elif completeness >= 70:
            transparency = 'خوب'
        elif completeness >= 50:
            transparency = 'متوسط'
        else:
            transparency = 'ضعیف'
        
        # فقط تراکنش‌های با شفافیت ضعیف یا متوسط
        if completeness < 70:
            amount = t.Debit if t.Debit else t.Credit if t.Credit else 0
            
            row = {
                'TransactionID': str(t.TransactionID) if hasattr(t, 'TransactionID') else '',
                'TransactionDate': t.TransactionDate.strftime('%Y-%m-%d') if hasattr(t, 'TransactionDate') and t.TransactionDate else '',
                'Amount': round(amount, 2),
                'MissingFields': ', '.join(missing_fields),
                'CompletenessScore': round(completeness, 2),
                'TransparencyLevel': transparency
            }
            data.append(row)
    
    # مرتب‌سازی بر اساس امتیاز کامل بودن
    data.sort(key=lambda x: x['CompletenessScore'])
    
    return data
