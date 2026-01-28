"""
آزمون تشخیص رشد ناگهانی
Spike Detection Test

این آزمون رشد ناگهانی و غیرعادی در مقادیر را شناسایی می‌کند.
افزایش یا کاهش ناگهانی که از الگوی عادی خارج است، تشخیص داده می‌شود.
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_number
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
from collections import defaultdict
import statistics


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_number('spikeThreshold', 'آستانه رشد ناگهانی (%)', default_value=200.0)
    ]
    
    result_schema = schema(
        col('Period', 'دوره', 'string'),
        col('Amount', 'مبلغ', 'money'),
        col('PreviousPeriod', 'دوره قبل', 'string'),
        col('PreviousAmount', 'مبلغ قبل', 'money'),
        col('Change', 'تغییر', 'money'),
        col('ChangePercent', 'درصد تغییر', 'percent'),
        col('AvgAmount', 'میانگین', 'money'),
        col('SpikeType', 'نوع رشد', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون تشخیص رشد ناگهانی"""
    
    spike_threshold = get_parameter('spikeThreshold', 200.0)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # گروه‌بندی بر اساس دوره
    period_amounts = defaultdict(float)
    
    for t in results:
        if hasattr(t, 'TransactionDate') and t.TransactionDate:
            period = t.TransactionDate.strftime('%Y-%m')
            amount = t.Debit if t.Debit else t.Credit if t.Credit else 0
            period_amounts[period] += amount
    
    if len(period_amounts) < 2:
        return []
    
    # مرتب‌سازی دوره‌ها
    sorted_periods = sorted(period_amounts.items())
    
    # محاسبه میانگین
    all_amounts = [amount for _, amount in sorted_periods]
    avg_amount = float(statistics.mean(all_amounts))
    
    # تشخیص رشد ناگهانی
    data = []
    
    for i in range(1, len(sorted_periods)):
        current_period, current_amount = sorted_periods[i]
        prev_period, prev_amount = sorted_periods[i - 1]
        
        current_float = float(current_amount)
        prev_float = float(prev_amount)
        change = current_float - prev_float
        
        if prev_float > 0:
            change_percent = (change / prev_float) * 100
        else:
            change_percent = 0
        
        if abs(change_percent) >= spike_threshold:
            # تعیین نوع رشد
            if change_percent > 0:
                spike_type = 'رشد ناگهانی'
            else:
                spike_type = 'افت ناگهانی'
            
            row = {
                'Period': current_period,
                'Amount': round(current_amount, 2),
                'PreviousPeriod': prev_period,
                'PreviousAmount': round(prev_amount, 2),
                'Change': round(change, 2),
                'ChangePercent': round(change_percent, 2),
                'AvgAmount': round(avg_amount, 2),
                'SpikeType': spike_type
            }
            data.append(row)
    
    # مرتب‌سازی بر اساس درصد تغییر
    data.sort(key=lambda x: abs(x['ChangePercent']), reverse=True)
    
    return data
