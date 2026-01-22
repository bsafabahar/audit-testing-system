"""
آزمون ترکیب‌های حساب نامعمول
Unusual Account Combinations Test

این آزمون ترکیب‌های غیرعادی حساب‌ها در ثبت‌های دفتر روزنامه را شناسایی می‌کند.
ترکیب‌های نامعمول ممکن است نشانه خطا یا تقلب باشند.
"""
from typing import List, Dict, Any
from models import Transaction
from schema import col, schema
from types_definitions import QueryDefinition
from database import ReadOnlySession
from collections import defaultdict


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = []
    
    result_schema = schema(
        col('JournalID', 'شناسه ثبت', 'string'),
        col('EntryDate', 'تاریخ ثبت', 'date'),
        col('DebitAccount', 'حساب بدهکار', 'string'),
        col('CreditAccount', 'حساب بستانکار', 'string'),
        col('Amount', 'مبلغ', 'money'),
        col('Combination', 'ترکیب', 'string'),
        col('Frequency', 'فراوانی', 'integer'),
        col('UnusualReason', 'دلیل غیرعادی بودن', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون ترکیب‌های حساب نامعمول"""
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # شمارش فراوانی ترکیب‌ها
    combinations = defaultdict(int)
    combination_transactions = defaultdict(list)
    
    for t in results:
        if hasattr(t, 'DebitAccount') and hasattr(t, 'CreditAccount'):
            if t.DebitAccount and t.CreditAccount:
                combo = f"{t.DebitAccount}:{t.CreditAccount}"
                combinations[combo] += 1
                combination_transactions[combo].append(t)
    
    # ترکیب‌های غیرمعمول (فراوانی کم)
    unusual_combos = {k: v for k, v in combinations.items() if v <= 3}
    
    # ترکیب‌های غیرمنطقی
    illogical_patterns = [
        ('Cash', 'Cash'),
        ('Bank', 'Bank'),
        ('Revenue', 'Expense'),
        ('Asset', 'Asset'),
        ('Liability', 'Liability')
    ]
    
    data = []
    
    for combo, freq in unusual_combos.items():
        debit_acc, credit_acc = combo.split(':')
        
        # تعیین دلیل غیرعادی بودن
        reason = 'فراوانی کم'
        
        for pattern in illogical_patterns:
            if pattern[0] in debit_acc and pattern[1] in credit_acc:
                reason = 'ترکیب غیرمنطقی'
                break
        
        for t in combination_transactions[combo]:
            amount = t.Debit if t.Debit else t.Credit if t.Credit else 0
            
            row = {
                'JournalID': str(t.TransactionID) if hasattr(t, 'TransactionID') else '',
                'EntryDate': t.TransactionDate.strftime('%Y-%m-%d') if hasattr(t, 'TransactionDate') and t.TransactionDate else '',
                'DebitAccount': debit_acc,
                'CreditAccount': credit_acc,
                'Amount': round(amount, 2),
                'Combination': combo,
                'Frequency': freq,
                'UnusualReason': reason
            }
            data.append(row)
    
    # مرتب‌سازی بر اساس فراوانی
    data.sort(key=lambda x: x['Frequency'])
    
    return data
