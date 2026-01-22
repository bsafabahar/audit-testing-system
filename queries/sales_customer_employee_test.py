"""
آزمون مطابقت مشتریان با کارکنان
Customer-Employee Match Test

این آزمون تراکنش‌هایی را شناسایی می‌کند که مشتری با کارمند مطابقت دارد.
فروش به کارکنان یا وابستگان ممکن است نشانه تقلب باشد.
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
        col('CustomerID', 'شناسه مشتری', 'string'),
        col('EmployeeID', 'شناسه کارمند', 'string'),
        col('Amount', 'مبلغ', 'money'),
        col('DiscountAmount', 'مبلغ تخفیف', 'money'),
        col('DiscountPercent', 'درصد تخفیف', 'percent'),
        col('TransactionDate', 'تاریخ تراکنش', 'date'),
        col('MatchType', 'نوع تطابق', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون مطابقت مشتریان با کارکنان"""
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # جمع‌آوری شناسه‌های کارکنان
    employee_ids = set()
    
    for t in results:
        if hasattr(t, 'EmployeeID') and t.EmployeeID:
            employee_ids.add(str(t.EmployeeID))
    
    # یافتن تطابق‌ها
    data = []
    
    for t in results:
        if hasattr(t, 'CustomerID') and hasattr(t, 'EmployeeID'):
            customer_id = str(t.CustomerID) if t.CustomerID else ''
            employee_id = str(t.EmployeeID) if t.EmployeeID else ''
            
            # بررسی تطابق مستقیم
            if customer_id and customer_id in employee_ids:
                match_type = 'مطابقت مستقیم'
                
                amount = t.Debit if t.Debit else t.Credit if t.Credit else 0
                discount = t.DiscountAmount if hasattr(t, 'DiscountAmount') and t.DiscountAmount else 0
                discount_percent = 0
                
                if hasattr(t, 'OriginalAmount') and t.OriginalAmount and t.OriginalAmount > 0:
                    discount_percent = (discount / t.OriginalAmount) * 100
                
                row = {
                    'TransactionID': str(t.TransactionID) if hasattr(t, 'TransactionID') else '',
                    'CustomerID': customer_id,
                    'EmployeeID': employee_id,
                    'Amount': round(amount, 2),
                    'DiscountAmount': round(discount, 2),
                    'DiscountPercent': round(discount_percent, 2),
                    'TransactionDate': t.TransactionDate.strftime('%Y-%m-%d') if hasattr(t, 'TransactionDate') and t.TransactionDate else '',
                    'MatchType': match_type
                }
                data.append(row)
    
    # مرتب‌سازی بر اساس مبلغ
    data.sort(key=lambda x: x['Amount'], reverse=True)
    
    return data
