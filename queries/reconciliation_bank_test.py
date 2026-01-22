"""
آزمون تطبیق بانکی
Bank Reconciliation Test

این آزمون تطابق تراکنش‌های بانکی با دفاتر حسابداری را بررسی می‌کند.
تراکنش‌های بدون تطبیق و اختلافات شناسایی می‌شوند.
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
        param_number('toleranceAmount', 'مبلغ تلورانس', default_value=10.0)
    ]
    
    result_schema = schema(
        col('TransactionID', 'شناسه تراکنش', 'string'),
        col('TransactionDate', 'تاریخ تراکنش', 'date'),
        col('BookAmount', 'مبلغ دفتری', 'money'),
        col('BankAmount', 'مبلغ بانکی', 'money'),
        col('Difference', 'اختلاف', 'money'),
        col('ReconciliationStatus', 'وضعیت تطبیق', 'string'),
        col('DaysOutstanding', 'روزهای معلق', 'integer')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون تطبیق بانکی"""
    
    tolerance = get_parameter('toleranceAmount', 10.0)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # تفکیک تراکنش‌های دفتری و بانکی
    book_transactions = {}
    bank_transactions = {}
    
    for t in results:
        if hasattr(t, 'TransactionType') and hasattr(t, 'ReferenceNumber'):
            ref_num = t.ReferenceNumber if hasattr(t, 'ReferenceNumber') else None
            
            if ref_num:
                amount = t.Debit if t.Debit else t.Credit
                
                if t.TransactionType == 'Book':
                    book_transactions[ref_num] = {
                        'transaction': t,
                        'amount': amount
                    }
                elif t.TransactionType == 'Bank':
                    bank_transactions[ref_num] = {
                        'transaction': t,
                        'amount': amount
                    }
    
    # یافتن اختلافات
    data = []
    
    # بررسی تراکنش‌های دفتری
    for ref_num, book_data in book_transactions.items():
        t = book_data['transaction']
        book_amount = book_data['amount']
        
        if ref_num in bank_transactions:
            bank_amount = bank_transactions[ref_num]['amount']
            difference = abs(book_amount - bank_amount)
            
            if difference > tolerance:
                status = 'اختلاف مبلغ'
            else:
                continue
        else:
            bank_amount = 0
            difference = book_amount
            status = 'بدون تطبیق بانکی'
        
        days_outstanding = 0
        if hasattr(t, 'TransactionDate') and t.TransactionDate:
            from datetime import datetime
            days_outstanding = (datetime.now().date() - t.TransactionDate.date()).days
        
        row = {
            'TransactionID': str(t.TransactionID) if hasattr(t, 'TransactionID') else '',
            'TransactionDate': t.TransactionDate.strftime('%Y-%m-%d') if hasattr(t, 'TransactionDate') and t.TransactionDate else '',
            'BookAmount': round(book_amount, 2),
            'BankAmount': round(bank_amount, 2),
            'Difference': round(difference, 2),
            'ReconciliationStatus': status,
            'DaysOutstanding': days_outstanding
        }
        data.append(row)
    
    # مرتب‌سازی بر اساس اختلاف
    data.sort(key=lambda x: x['Difference'], reverse=True)
    
    return data
