"""
آزمون مطابقت مشتریان با کارکنان
Customer-Employee Match Test

این آزمون تراکنش‌هایی را شناسایی می‌کند که مشتری با کارمند مطابقت دارد.
فروش به کارکنان یا وابستگان ممکن است نشانه تقلب باشد.
"""
from typing import List, Dict, Any
from models import SalesTransactions, PayrollTransactions
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
    
    # دریافت شناسه‌های کارکنان از PayrollTransactions
    payroll_query = session.query(PayrollTransactions.EmployeeCode).distinct()
    employee_codes = {str(row.EmployeeCode) for row in payroll_query.all() if row.EmployeeCode}
    
    # دریافت داده‌های فروش
    sales_query = session.query(SalesTransactions)
    sales_results = sales_query.all()
    
    # یافتن تطابق‌ها
    data = []
    
    for t in sales_results:
        customer_code = str(t.CustomerCode) if t.CustomerCode else ''
        
        # بررسی تطابق مستقیم
        if customer_code and customer_code in employee_codes:
            match_type = 'مطابقت مستقیم'
            
            amount = float(t.Amount) if t.Amount else 0
            
            row = {
                'TransactionID': str(t.InvoiceNumber) if t.InvoiceNumber else '',
                'CustomerID': customer_code,
                'EmployeeID': customer_code,
                'Amount': round(amount, 2),
                'DiscountAmount': 0,  # Not available in SalesTransactions
                'DiscountPercent': 0,  # Not available in SalesTransactions
                'TransactionDate': t.InvoiceDate.strftime('%Y-%m-%d') if t.InvoiceDate else '',
                'MatchType': match_type
            }
            data.append(row)
    
    # مرتب‌سازی بر اساس مبلغ
    data.sort(key=lambda x: x['Amount'], reverse=True)
    
    return data
