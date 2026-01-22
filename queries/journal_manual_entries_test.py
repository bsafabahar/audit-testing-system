"""
آزمون ثبت‌های دستی
Manual Journal Entries Test

این آزمون ثبت‌های دستی دفتر روزنامه را شناسایی می‌کند.
ثبت‌های دستی ممکن است نیاز به بررسی دقیق‌تر داشته باشند.
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_number
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_number('minAmount', 'حداقل مبلغ', default_value=1000000.0)
    ]
    
    result_schema = schema(
        col('JournalID', 'شناسه ثبت', 'string'),
        col('EntryDate', 'تاریخ ثبت', 'date'),
        col('Amount', 'مبلغ', 'money'),
        col('Account', 'حساب', 'string'),
        col('Description', 'شرح', 'string'),
        col('EnteredBy', 'ثبت‌کننده', 'string'),
        col('EntryTime', 'زمان ثبت', 'string'),
        col('IsAfterHours', 'خارج از ساعت کاری', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون ثبت‌های دستی"""
    
    min_amount = get_parameter('minAmount', 1000000.0)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    data = []
    
    for t in results:
        if hasattr(t, 'EntryType') and t.EntryType == 'Manual':
            amount = t.Debit if t.Debit else t.Credit if t.Credit else 0
            
            if amount >= min_amount:
                # بررسی زمان ثبت
                entry_time = ''
                is_after_hours = 'خیر'
                
                if hasattr(t, 'EntryTime') and t.EntryTime:
                    entry_time = str(t.EntryTime)
                    # بررسی ساعات کاری (8 تا 18)
                    hour = t.EntryTime.hour if hasattr(t.EntryTime, 'hour') else 12
                    if hour < 8 or hour > 18:
                        is_after_hours = 'بله'
                
                row = {
                    'JournalID': str(t.TransactionID) if hasattr(t, 'TransactionID') else '',
                    'EntryDate': t.TransactionDate.strftime('%Y-%m-%d') if hasattr(t, 'TransactionDate') and t.TransactionDate else '',
                    'Amount': round(amount, 2),
                    'Account': t.AccountCode if hasattr(t, 'AccountCode') else '',
                    'Description': t.Description if hasattr(t, 'Description') else '',
                    'EnteredBy': t.EnteredBy if hasattr(t, 'EnteredBy') else '',
                    'EntryTime': entry_time,
                    'IsAfterHours': is_after_hours
                }
                data.append(row)
    
    # مرتب‌سازی بر اساس مبلغ
    data.sort(key=lambda x: x['Amount'], reverse=True)
    
    return data
