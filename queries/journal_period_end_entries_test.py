"""
آزمون ثبت‌های آخر دوره
Period End Entries Test

این آزمون ثبت‌های انجام شده در آخر دوره مالی را شناسایی می‌کند.
ثبت‌های آخر دوره ممکن است برای دستکاری سود استفاده شده باشند.
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
        param_number('lastDaysOfPeriod', 'روزهای آخر دوره', default_value=5)
    ]
    
    result_schema = schema(
        col('JournalID', 'شناسه ثبت', 'string'),
        col('EntryDate', 'تاریخ ثبت', 'date'),
        col('Amount', 'مبلغ', 'money'),
        col('Account', 'حساب', 'string'),
        col('Description', 'شرح', 'string'),
        col('EntryType', 'نوع ثبت', 'string'),
        col('ImpactOnProfit', 'تاثیر بر سود', 'string'),
        col('DaysFromPeriodEnd', 'روزها تا پایان دوره', 'integer')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون ثبت‌های آخر دوره"""
    
    last_days = get_parameter('lastDaysOfPeriod', 5)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    data = []
    
    for t in results:
        if hasattr(t, 'TransactionDate') and t.TransactionDate:
            # بررسی آخر ماه
            day = t.TransactionDate.day
            
            # محاسبه آخرین روز ماه
            if t.TransactionDate.month == 12:
                next_month = t.TransactionDate.replace(year=t.TransactionDate.year + 1, month=1, day=1)
            else:
                next_month = t.TransactionDate.replace(month=t.TransactionDate.month + 1, day=1)
            
            from datetime import timedelta
            last_day_of_month = (next_month - timedelta(days=1)).day
            days_from_end = last_day_of_month - day
            
            if days_from_end < last_days:
                amount = t.Debit if t.Debit else t.Credit if t.Credit else 0
                
                # تعیین تاثیر بر سود
                impact = 'خنثی'
                if hasattr(t, 'AccountType'):
                    if t.AccountType in ['Revenue', 'Income']:
                        impact = 'افزایش سود'
                    elif t.AccountType in ['Expense', 'Cost']:
                        impact = 'کاهش سود'
                
                row = {
                    'JournalID': str(t.TransactionID) if hasattr(t, 'TransactionID') else '',
                    'EntryDate': t.TransactionDate.strftime('%Y-%m-%d'),
                    'Amount': round(amount, 2),
                    'Account': t.AccountCode if hasattr(t, 'AccountCode') else '',
                    'Description': t.Description if hasattr(t, 'Description') else '',
                    'EntryType': t.EntryType if hasattr(t, 'EntryType') else 'عادی',
                    'ImpactOnProfit': impact,
                    'DaysFromPeriodEnd': days_from_end
                }
                data.append(row)
    
    # مرتب‌سازی بر اساس روزها تا پایان دوره
    data.sort(key=lambda x: x['DaysFromPeriodEnd'])
    
    return data
