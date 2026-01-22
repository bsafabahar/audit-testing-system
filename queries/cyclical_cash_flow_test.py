"""
آزمون الگوی سینوسی جریان نقدی
Cyclical Cash Flow Pattern Test

این آزمون الگوهای سینوسی (دوره‌ای) در جریان نقدی را شناسایی می‌کند.
الگوهای تکراری و غیرعادی در جریان ورودی و خروجی نقدی تشخیص داده می‌شوند.
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_number
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
from collections import defaultdict
from datetime import datetime
import statistics


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_number('periodDays', 'دوره زمانی (روز)', default_value=30),
        param_number('correlationThreshold', 'آستانه همبستگی', default_value=0.7)
    ]
    
    result_schema = schema(
        col('Period', 'دوره', 'string'),
        col('CashInflow', 'ورود نقدی', 'money'),
        col('CashOutflow', 'خروج نقدی', 'money'),
        col('NetCashFlow', 'خالص جریان نقدی', 'money'),
        col('MovingAverage', 'میانگین متحرک', 'money'),
        col('Deviation', 'انحراف از میانگین', 'percent'),
        col('CyclicalPattern', 'الگوی دوره‌ای', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون الگوی سینوسی جریان نقدی"""
    
    period_days = get_parameter('periodDays', 30)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # گروه‌بندی بر اساس دوره
    period_data = defaultdict(lambda: {'inflow': 0, 'outflow': 0})
    
    for t in results:
        if hasattr(t, 'TransactionDate'):
            if t.TransactionDate:
                period_key = t.TransactionDate.strftime('%Y-%m')
                
                if t.Debit:
                    period_data[period_key]['outflow'] += t.Debit
                if t.Credit:
                    period_data[period_key]['inflow'] += t.Credit
    
    if len(period_data) < 3:
        return []
    
    # محاسبه آمار
    sorted_periods = sorted(period_data.items())
    net_flows = [d['inflow'] - d['outflow'] for _, d in sorted_periods]
    
    if len(net_flows) > 0:
        avg_net_flow = statistics.mean(net_flows)
    else:
        return []
    
    # تشخیص الگوی سینوسی
    data = []
    for i, (period, flows) in enumerate(sorted_periods):
        net_flow = flows['inflow'] - flows['outflow']
        
        # محاسبه میانگین متحرک
        window = 3
        start_idx = max(0, i - window + 1)
        window_flows = net_flows[start_idx:i+1]
        moving_avg = statistics.mean(window_flows) if window_flows else 0
        
        deviation = ((net_flow - moving_avg) / moving_avg * 100) if moving_avg != 0 else 0
        
        # تشخیص الگو
        pattern = 'عادی'
        if abs(deviation) > 50:
            if net_flow > moving_avg:
                pattern = 'اوج دوره‌ای'
            else:
                pattern = 'فرود دوره‌ای'
        
        row = {
            'Period': period,
            'CashInflow': round(flows['inflow'], 2),
            'CashOutflow': round(flows['outflow'], 2),
            'NetCashFlow': round(net_flow, 2),
            'MovingAverage': round(moving_avg, 2),
            'Deviation': round(deviation, 2),
            'CyclicalPattern': pattern
        }
        data.append(row)
    
    return data
