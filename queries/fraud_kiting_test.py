"""
آزمون Kiting
Check Kiting Test

این آزمون الگوی Kiting (جابجایی غیرقانونی چک بین حساب‌ها) را شناسایی می‌کند.
انتقالات سریع و مشکوک بین حساب‌های بانکی تشخیص داده می‌شوند.
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_number
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
from collections import defaultdict
from datetime import timedelta


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_number('maxDaysBetween', 'حداکثر روز بین انتقالات', default_value=3)
    ]
    
    result_schema = schema(
        col('AccountPair', 'جفت حساب', 'string'),
        col('TransferCount', 'تعداد انتقال', 'integer'),
        col('TotalAmount', 'کل مبلغ', 'money'),
        col('AvgTimeBetween', 'میانگین زمان بین انتقالات', 'number'),
        col('FirstDate', 'اولین تاریخ', 'date'),
        col('LastDate', 'آخرین تاریخ', 'date'),
        col('SuspicionLevel', 'سطح مشکوک', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون Kiting"""
    
    max_days = get_parameter('maxDaysBetween', 3)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # گروه‌بندی انتقالات بین حساب‌ها
    account_transfers = defaultdict(lambda: {
        'transfers': [],
        'total': 0
    })
    
    for t in results:
        if hasattr(t, 'FromAccount') and hasattr(t, 'ToAccount'):
            if t.FromAccount and t.ToAccount:
                # ایجاد کلید جفت حساب
                accounts = tuple(sorted([t.FromAccount, t.ToAccount]))
                key = f"{accounts[0]} <-> {accounts[1]}"
                
                amount = t.Debit if t.Debit else t.Credit if t.Credit else 0
                date = t.TransactionDate if hasattr(t, 'TransactionDate') else None
                
                if date:
                    account_transfers[key]['transfers'].append({
                        'date': date,
                        'amount': amount
                    })
                    account_transfers[key]['total'] += amount
    
    # تحلیل الگوی kiting
    data = []
    
    for pair, info in account_transfers.items():
        if len(info['transfers']) >= 3:
            # مرتب‌سازی بر اساس تاریخ
            sorted_transfers = sorted(info['transfers'], key=lambda x: x['date'])
            
            # محاسبه میانگین زمان بین انتقالات
            time_diffs = []
            for i in range(len(sorted_transfers) - 1):
                diff = (sorted_transfers[i + 1]['date'] - sorted_transfers[i]['date']).days
                time_diffs.append(diff)
            
            avg_time = sum(time_diffs) / len(time_diffs) if time_diffs else 0
            
            # تعیین سطح مشکوک
            suspicion = 'عادی'
            if avg_time <= max_days and len(sorted_transfers) >= 5:
                suspicion = 'بسیار مشکوک'
            elif avg_time <= max_days:
                suspicion = 'مشکوک'
            
            if suspicion != 'عادی':
                row = {
                    'AccountPair': pair,
                    'TransferCount': len(sorted_transfers),
                    'TotalAmount': round(info['total'], 2),
                    'AvgTimeBetween': round(avg_time, 2),
                    'FirstDate': sorted_transfers[0]['date'].strftime('%Y-%m-%d'),
                    'LastDate': sorted_transfers[-1]['date'].strftime('%Y-%m-%d'),
                    'SuspicionLevel': suspicion
                }
                data.append(row)
    
    # مرتب‌سازی بر اساس میانگین زمان
    data.sort(key=lambda x: x['AvgTimeBetween'])
    
    return data
