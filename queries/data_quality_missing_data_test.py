"""
آزمون داده‌های خالی
Missing Data Test

این آزمون فیلدهای خالی و ناقص در داده‌ها را شناسایی می‌کند.
داده‌های ناقص ممکن است باعث خطا در تحلیل‌ها شوند.
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
        col('MissingFieldCount', 'تعداد فیلد خالی', 'integer'),
        col('MissingFields', 'فیلدهای خالی', 'string'),
        col('DataQualityScore', 'امتیاز کیفیت', 'percent'),
        col('Severity', 'شدت', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون داده‌های خالی"""
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # فیلدهای مهم
    important_fields = [
        'TransactionDate',
        'Description',
        'AccountCode',
        'ReferenceNumber'
    ]
    
    data = []
    
    for t in results:
        missing = []
        
        # بررسی فیلدهای اصلی
        for field in important_fields:
            if hasattr(t, field):
                value = getattr(t, field)
                if value is None or (isinstance(value, str) and value.strip() == ''):
                    missing.append(field)
            else:
                missing.append(field)
        
        # بررسی مبلغ
        if not t.Debit and not t.Credit:
            missing.append('Amount')
        
        missing_count = len(missing)
        
        if missing_count > 0:
            total_fields = len(important_fields) + 1
            quality_score = ((total_fields - missing_count) / total_fields) * 100
            
            # تعیین شدت
            if missing_count >= 4:
                severity = 'بحرانی'
            elif missing_count >= 2:
                severity = 'متوسط'
            else:
                severity = 'کم'
            
            row = {
                'TransactionID': str(t.TransactionID) if hasattr(t, 'TransactionID') else '',
                'TransactionDate': t.TransactionDate.strftime('%Y-%m-%d') if hasattr(t, 'TransactionDate') and t.TransactionDate else '',
                'MissingFieldCount': missing_count,
                'MissingFields': ', '.join(missing),
                'DataQualityScore': round(quality_score, 2),
                'Severity': severity
            }
            data.append(row)
    
    # مرتب‌سازی بر اساس تعداد فیلد خالی
    data.sort(key=lambda x: x['MissingFieldCount'], reverse=True)
    
    return data
