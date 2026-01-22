"""
آزمون داده‌های غیرمعقول
Reasonableness Test

این آزمون داده‌هایی که منطقی و معقول نیستند را شناسایی می‌کند.
مقادیر غیرعادی مانند اعداد منفی یا بسیار بزرگ تشخیص داده می‌شوند.
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
        col('Field', 'فیلد', 'string'),
        col('Value', 'مقدار', 'string'),
        col('ReasonForFlag', 'دلیل علامت‌گذاری', 'string'),
        col('Severity', 'شدت', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون داده‌های غیرمعقول"""
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    data = []
    
    for t in results:
        issues = []
        
        # بررسی مبالغ منفی
        if hasattr(t, 'UnitPrice') and t.UnitPrice and t.UnitPrice < 0:
            issues.append({
                'field': 'UnitPrice',
                'value': str(t.UnitPrice),
                'reason': 'قیمت واحد منفی',
                'severity': 'بالا'
            })
        
        # بررسی تعداد منفی
        if hasattr(t, 'Quantity') and t.Quantity and t.Quantity < 0:
            issues.append({
                'field': 'Quantity',
                'value': str(t.Quantity),
                'reason': 'تعداد منفی',
                'severity': 'متوسط'
            })
        
        # بررسی مبالغ خیلی بزرگ
        amount = t.Debit if t.Debit else t.Credit if t.Credit else 0
        if amount > 1000000000000:  # 1 تریلیون
            issues.append({
                'field': 'Amount',
                'value': str(amount),
                'reason': 'مبلغ بیش از حد بزرگ',
                'severity': 'بالا'
            })
        
        # بررسی تاریخ آینده
        if hasattr(t, 'TransactionDate') and t.TransactionDate:
            from datetime import datetime
            if t.TransactionDate.date() > datetime.now().date():
                issues.append({
                    'field': 'TransactionDate',
                    'value': t.TransactionDate.strftime('%Y-%m-%d'),
                    'reason': 'تاریخ آینده',
                    'severity': 'بالا'
                })
        
        # بررسی تاریخ خیلی قدیمی
        if hasattr(t, 'TransactionDate') and t.TransactionDate:
            from datetime import datetime
            if t.TransactionDate.year < 1900:
                issues.append({
                    'field': 'TransactionDate',
                    'value': t.TransactionDate.strftime('%Y-%m-%d'),
                    'reason': 'تاریخ خیلی قدیمی',
                    'severity': 'متوسط'
                })
        
        # افزودن مسائل به خروجی
        for issue in issues:
            row = {
                'TransactionID': str(t.TransactionID) if hasattr(t, 'TransactionID') else '',
                'TransactionDate': t.TransactionDate.strftime('%Y-%m-%d') if hasattr(t, 'TransactionDate') and t.TransactionDate else '',
                'Field': issue['field'],
                'Value': issue['value'],
                'ReasonForFlag': issue['reason'],
                'Severity': issue['severity']
            }
            data.append(row)
    
    # مرتب‌سازی بر اساس شدت
    severity_order = {'بالا': 0, 'متوسط': 1, 'کم': 2}
    data.sort(key=lambda x: severity_order.get(x['Severity'], 3))
    
    return data
