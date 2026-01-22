"""
آزمون Skimming
Skimming Test

این آزمون الگوی Skimming (برداشت نقدی قبل از ثبت) را شناسایی می‌کند.
فروش‌های ثبت نشده و اختلاف در مقادیر نقدی تشخیص داده می‌شوند.
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
        param_number('varianceThreshold', 'آستانه واریانس (%)', default_value=5.0)
    ]
    
    result_schema = schema(
        col('Period', 'دوره', 'string'),
        col('ExpectedCash', 'نقد مورد انتظار', 'money'),
        col('ActualCash', 'نقد واقعی', 'money'),
        col('Variance', 'واریانس', 'money'),
        col('VariancePercent', 'درصد واریانس', 'percent'),
        col('SalesCount', 'تعداد فروش', 'integer'),
        col('AvgSale', 'میانگین فروش', 'money'),
        col('SkimmingRisk', 'ریسک Skimming', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون Skimming"""
    
    variance_threshold = get_parameter('varianceThreshold', 5.0)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # گروه‌بندی بر اساس دوره
    period_data = defaultdict(lambda: {
        'sales': 0,
        'cash': 0,
        'count': 0
    })
    
    for t in results:
        if hasattr(t, 'TransactionDate') and t.TransactionDate:
            period = t.TransactionDate.strftime('%Y-%m')
            
            # فروش
            if hasattr(t, 'TransactionType') and t.TransactionType == 'Sale':
                amount = t.Credit if t.Credit else 0
                period_data[period]['sales'] += amount
                period_data[period]['count'] += 1
            
            # نقد دریافتی
            if hasattr(t, 'PaymentMethod') and t.PaymentMethod == 'Cash':
                amount = t.Credit if t.Credit else 0
                period_data[period]['cash'] += amount
    
    # تحلیل واریانس
    data = []
    
    for period, info in period_data.items():
        if info['count'] > 0:
            expected_cash = info['sales']
            actual_cash = info['cash']
            variance = expected_cash - actual_cash
            
            if expected_cash > 0:
                variance_percent = (variance / expected_cash) * 100
            else:
                variance_percent = 0
            
            if abs(variance_percent) >= variance_threshold:
                avg_sale = info['sales'] / info['count']
                
                # تعیین ریسک
                risk = 'متوسط'
                if variance > 0 and variance_percent > 10:
                    risk = 'بالا'
                elif variance > 0 and variance_percent > 5:
                    risk = 'متوسط'
                else:
                    risk = 'کم'
                
                row = {
                    'Period': period,
                    'ExpectedCash': round(expected_cash, 2),
                    'ActualCash': round(actual_cash, 2),
                    'Variance': round(variance, 2),
                    'VariancePercent': round(variance_percent, 2),
                    'SalesCount': info['count'],
                    'AvgSale': round(avg_sale, 2),
                    'SkimmingRisk': risk
                }
                data.append(row)
    
    # مرتب‌سازی بر اساس درصد واریانس
    data.sort(key=lambda x: abs(x['VariancePercent']), reverse=True)
    
    return data
