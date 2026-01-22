"""
آزمون تراکنش‌های کاملاً تکراری
Duplicate Transaction Detection

شناسایی تراکنش‌های کاملاً یکسان (تاریخ + فروشنده + مبلغ + شرح).
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
        param_number('limit', 'تعداد رکورد', default_value=200)
    ]
    
    result_schema = schema(
        col('Id', 'شناسه', 'integer'),
        col('DocumentDate', 'تاریخ سند', 'date'),
        col('DocumentNumber', 'شماره سند', 'integer'),
        col('AccountCode', 'کد حساب', 'string'),
        col('Debit', 'بدهکار', 'currency'),
        col('Credit', 'بستانکار', 'currency'),
        col('Description', 'شرح', 'string'),
        col('DuplicateCount', 'تعداد تکرار', 'integer'),
        col('DuplicateGroupId', 'شناسه گروه', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون تراکنش‌های تکراری"""
    
    limit = get_parameter('limit', 200)
    
    query = session.query(Transaction)
    results = query.all()
    
    # گروه‌بندی بر اساس کلید ترکیبی
    groups = defaultdict(list)
    
    for t in results:
        # ایجاد کلید یکتا
        date_str = t.DocumentDate.strftime('%Y-%m-%d') if t.DocumentDate else 'NULL'
        account = t.AccountCode or 'NULL'
        debit = f"{t.Debit:.2f}" if t.Debit else '0.00'
        credit = f"{t.Credit:.2f}" if t.Credit else '0.00'
        desc = (t.Description or '')[:50]
        
        key = f"{date_str}|{account}|{debit}|{credit}|{desc}"
        groups[key].append(t)
    
    # یافتن گروه‌های تکراری
    data = []
    group_counter = 1
    
    for key, transactions in groups.items():
        if len(transactions) > 1:  # فقط موارد تکراری
            for t in transactions:
                row = {
                    'Id': t.Id,
                    'DocumentDate': t.DocumentDate.strftime('%Y-%m-%d') if t.DocumentDate else '',
                    'DocumentNumber': t.DocumentNumber,
                    'AccountCode': t.AccountCode,
                    'Debit': float(t.Debit) if t.Debit else 0.0,
                    'Credit': float(t.Credit) if t.Credit else 0.0,
                    'Description': t.Description[:50] if t.Description else '',
                    'DuplicateCount': len(transactions),
                    'DuplicateGroupId': f'DUP-{group_counter:04d}'
                }
                data.append(row)
            
            group_counter += 1
    
    # مرتب‌سازی بر اساس تعداد تکرار
    data.sort(key=lambda x: x['DuplicateCount'], reverse=True)
    
    return data[:limit]
