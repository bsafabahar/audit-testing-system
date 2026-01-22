"""
آزمون الگوی سینوسی فروش
Cyclical Sales Pattern Test

این آزمون الگوهای سینوسی در فروش را شناسایی می‌کند.
الگوهای تکراری و غیرعادی در فروش تشخیص داده می‌شوند.
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
        param_number('deviationThreshold', 'آستانه انحراف (%)', default_value=50.0)
    ]
    
    result_schema = schema(
        col('Period', 'دوره', 'string'),
        col('SalesAmount', 'مبلغ فروش', 'money'),
        col('TransactionCount', 'تعداد تراکنش', 'integer'),
        col('AvgSales', 'میانگین فروش', 'money'),
        col('MovingAverage', 'میانگین متحرک', 'money'),
        col('Deviation', 'انحراف', 'percent'),
        col('PatternType', 'نوع الگو', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون الگوی سینوسی فروش"""
    
    deviation_threshold = get_parameter('deviationThreshold', 50.0)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # گروه‌بندی بر اساس دوره
    period_sales = defaultdict(lambda: {'amount': 0, 'count': 0})
    
    for t in results:
        if hasattr(t, 'TransactionDate') and t.TransactionDate:
            period = t.TransactionDate.strftime('%Y-%m')
            
            if hasattr(t, 'SaleAmount') and t.SaleAmount:
                period_sales[period]['amount'] += t.SaleAmount
                period_sales[period]['count'] += 1
            elif t.Credit:
                period_sales[period]['amount'] += t.Credit
                period_sales[period]['count'] += 1
    
    if len(period_sales) < 3:
        return []
    
    # محاسبه آمار
    sorted_periods = sorted(period_sales.items())
    sales_amounts = [d['amount'] for _, d in sorted_periods]
    avg_sales = statistics.mean(sales_amounts)
    
    # تشخیص الگوی سینوسی
    data = []
    for i, (period, sales_data) in enumerate(sorted_periods):
        amount = sales_data['amount']
        count = sales_data['count']
        
        # محاسبه میانگین متحرک (3 دوره)
        window = 3
        start_idx = max(0, i - window + 1)
        window_amounts = sales_amounts[start_idx:i+1]
        moving_avg = statistics.mean(window_amounts) if window_amounts else 0
        
        deviation = ((amount - moving_avg) / moving_avg * 100) if moving_avg != 0 else 0
        
        # تشخیص نوع الگو
        pattern = 'عادی'
        if abs(deviation) >= deviation_threshold:
            if amount > moving_avg:
                pattern = 'اوج فروش'
            else:
                pattern = 'افت فروش'
        
        if abs(deviation) >= deviation_threshold:
            row = {
                'Period': period,
                'SalesAmount': round(amount, 2),
                'TransactionCount': count,
                'AvgSales': round(avg_sales, 2),
                'MovingAverage': round(moving_avg, 2),
                'Deviation': round(deviation, 2),
                'PatternType': pattern
            }
            data.append(row)
    
    # مرتب‌سازی بر اساس انحراف
    data.sort(key=lambda x: abs(x['Deviation']), reverse=True)
    
    return data
