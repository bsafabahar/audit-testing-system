"""
آزمون تراکنش‌های آخر هفته
Weekend Transactions Test

این آزمون تراکنش‌های بانکی که در آخر هفته یا تعطیلات انجام شده‌اند را شناسایی می‌کند.
تراکنش‌های آخر هفته ممکن است مشکوک باشند.
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
        col('DayOfWeek', 'روز هفته', 'string'),
        col('Amount', 'مبلغ', 'money'),
        col('TransactionType', 'نوع تراکنش', 'string'),
        col('AccountNumber', 'شماره حساب', 'string'),
        col('Description', 'شرح', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون تراکنش‌های آخر هفته"""
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # نام روزهای هفته به فارسی
    day_names = {
        0: 'دوشنبه',
        1: 'سه‌شنبه',
        2: 'چهارشنبه',
        3: 'پنج‌شنبه',
        4: 'جمعه',
        5: 'شنبه',
        6: 'یکشنبه'
    }
    
    data = []
    
    for t in results:
        if hasattr(t, 'TransactionDate') and t.TransactionDate:
            day_of_week = t.TransactionDate.weekday()
            
            # جمعه (4) و شنبه (5)
            if day_of_week in [4, 5]:
                amount = t.Debit if t.Debit else t.Credit if t.Credit else 0
                
                row = {
                    'TransactionID': str(t.TransactionID) if hasattr(t, 'TransactionID') else '',
                    'TransactionDate': t.TransactionDate.strftime('%Y-%m-%d'),
                    'DayOfWeek': day_names.get(day_of_week, 'نامشخص'),
                    'Amount': round(amount, 2),
                    'TransactionType': t.TransactionType if hasattr(t, 'TransactionType') else '',
                    'AccountNumber': t.AccountNumber if hasattr(t, 'AccountNumber') else '',
                    'Description': t.Description if hasattr(t, 'Description') else ''
                }
                data.append(row)
    
    # مرتب‌سازی بر اساس تاریخ
    data.sort(key=lambda x: x['TransactionDate'], reverse=True)
    
    return data
