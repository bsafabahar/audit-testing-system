"""
آزمون تحلیل فاصله‌ها
Gap Analysis Test

این آزمون فاصله‌ها و شکاف‌های غیرعادی در داده‌ها را شناسایی می‌کند.
شکاف‌های زمانی یا عددی مشکوک تشخیص داده می‌شوند.
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_number
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
from datetime import timedelta


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_number('minGapDays', 'حداقل روز فاصله', default_value=7)
    ]
    
    result_schema = schema(
        col('GapStartDate', 'تاریخ شروع فاصله', 'date'),
        col('GapEndDate', 'تاریخ پایان فاصله', 'date'),
        col('GapDays', 'روزهای فاصله', 'integer'),
        col('TransactionsBefore', 'تراکنش‌های قبل', 'integer'),
        col('TransactionsAfter', 'تراکنش‌های بعد', 'integer'),
        col('AvgDailyBefore', 'میانگین روزانه قبل', 'number'),
        col('AvgDailyAfter', 'میانگین روزانه بعد', 'number'),
        col('GapType', 'نوع فاصله', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون تحلیل فاصله‌ها"""
    
    min_gap_days = get_parameter('minGapDays', 7)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # استخراج تاریخ‌ها
    dates = []
    
    for t in results:
        if hasattr(t, 'TransactionDate') and t.TransactionDate:
            dates.append(t.TransactionDate.date())
    
    if len(dates) < 2:
        return []
    
    # مرتب‌سازی و حذف تکراری
    unique_dates = sorted(set(dates))
    
    # یافتن فاصله‌ها
    data = []
    
    for i in range(len(unique_dates) - 1):
        current_date = unique_dates[i]
        next_date = unique_dates[i + 1]
        gap_days = (next_date - current_date).days
        
        if gap_days >= min_gap_days:
            # شمارش تراکنش‌ها قبل و بعد
            trans_before = dates.count(current_date)
            trans_after = dates.count(next_date)
            
            # محاسبه میانگین روزانه
            window = 7
            before_start = current_date - timedelta(days=window)
            after_end = next_date + timedelta(days=window)
            
            trans_in_window_before = sum(1 for d in dates if before_start <= d <= current_date)
            trans_in_window_after = sum(1 for d in dates if next_date <= d <= after_end)
            
            avg_daily_before = trans_in_window_before / window if window > 0 else 0
            avg_daily_after = trans_in_window_after / window if window > 0 else 0
            
            # تعیین نوع فاصله
            if gap_days >= 30:
                gap_type = 'فاصله طولانی'
            elif gap_days >= 14:
                gap_type = 'فاصله متوسط'
            else:
                gap_type = 'فاصله کوتاه'
            
            # بررسی آخر هفته
            if gap_days <= 3 and current_date.weekday() >= 4:
                gap_type = 'آخر هفته'
            
            row = {
                'GapStartDate': current_date.strftime('%Y-%m-%d'),
                'GapEndDate': next_date.strftime('%Y-%m-%d'),
                'GapDays': gap_days,
                'TransactionsBefore': trans_before,
                'TransactionsAfter': trans_after,
                'AvgDailyBefore': round(avg_daily_before, 2),
                'AvgDailyAfter': round(avg_daily_after, 2),
                'GapType': gap_type
            }
            data.append(row)
    
    # مرتب‌سازی بر اساس روزهای فاصله
    data.sort(key=lambda x: x['GapDays'], reverse=True)
    
    return data
