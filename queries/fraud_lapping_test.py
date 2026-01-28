"""
آزمون Lapping
Lapping Test

این آزمون الگوی Lapping (پوشش دادن اختلاس با وجوه بعدی) را شناسایی می‌کند.
الگوهای پرداخت مشکوک در حساب‌های دریافتنی تشخیص داده می‌شوند.
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_number
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
from collections import defaultdict


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_number('dayThreshold', 'آستانه روز تاخیر', default_value=30)
    ]
    
    result_schema = schema(
        col('CustomerID', 'شناسه مشتری', 'string'),
        col('InvoiceID', 'شماره فاکتور', 'string'),
        col('InvoiceDate', 'تاریخ فاکتور', 'date'),
        col('PaymentDate', 'تاریخ پرداخت', 'date'),
        col('DaysLate', 'روز تاخیر', 'integer'),
        col('InvoiceAmount', 'مبلغ فاکتور', 'money'),
        col('PaymentAmount', 'مبلغ پرداختی', 'money'),
        col('Difference', 'اختلاف', 'money'),
        col('LappingIndicator', 'نشانگر Lapping', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون Lapping"""
    
    day_threshold = get_parameter('dayThreshold', 30)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # گروه‌بندی فاکتورها و پرداخت‌ها
    invoices = {}
    payments = defaultdict(list)
    
    for t in results:
        if hasattr(t, 'TransactionType'):
            if t.TransactionType == 'Invoice':
                if hasattr(t, 'InvoiceID') and t.InvoiceID:
                    invoices[t.InvoiceID] = {
                        'customer': t.CustomerID if hasattr(t, 'CustomerID') else None,
                        'date': t.TransactionDate if hasattr(t, 'TransactionDate') else None,
                        'amount': t.Debit if t.Debit else 0
                    }
            
            elif t.TransactionType == 'Payment':
                if hasattr(t, 'CustomerID') and t.CustomerID:
                    payments[t.CustomerID].append({
                        'date': t.TransactionDate if hasattr(t, 'TransactionDate') else None,
                        'amount': t.Credit if t.Credit else 0,
                        'invoice': t.InvoiceID if hasattr(t, 'InvoiceID') else None
                    })
    
    # تحلیل الگوی lapping
    data = []
    
    for invoice_id, invoice_info in invoices.items():
        if invoice_info['customer'] and invoice_info['customer'] in payments:
            customer_payments = payments[invoice_info['customer']]
            
            # یافتن پرداخت مرتبط
            related_payment = None
            for payment in customer_payments:
                if payment['invoice'] == invoice_id:
                    related_payment = payment
                    break
            
            if related_payment and invoice_info['date'] and related_payment['date']:
                days_late = (related_payment['date'] - invoice_info['date']).days
                difference = abs(invoice_info['amount'] - related_payment['amount'])
                
                # تعیین نشانگر lapping
                indicator = 'عادی'
                if days_late > day_threshold and difference > 0:
                    indicator = 'مشکوک - تاخیر و اختلاف'
                elif days_late > day_threshold * 2:
                    indicator = 'بسیار مشکوک - تاخیر زیاد'
                elif difference > float(invoice_info['amount']) * 0.1:
                    indicator = 'مشکوک - اختلاف مبلغ'
                
                if indicator != 'عادی':
                    row = {
                        'CustomerID': str(invoice_info['customer']),
                        'InvoiceID': str(invoice_id),
                        'InvoiceDate': invoice_info['date'].strftime('%Y-%m-%d'),
                        'PaymentDate': related_payment['date'].strftime('%Y-%m-%d'),
                        'DaysLate': days_late,
                        'InvoiceAmount': round(invoice_info['amount'], 2),
                        'PaymentAmount': round(related_payment['amount'], 2),
                        'Difference': round(difference, 2),
                        'LappingIndicator': indicator
                    }
                    data.append(row)
    
    # مرتب‌سازی بر اساس روز تاخیر
    data.sort(key=lambda x: x['DaysLate'], reverse=True)
    
    return data
