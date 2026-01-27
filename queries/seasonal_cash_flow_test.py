"""
آزمون الگوی فصلی جریان نقدی
Seasonal Cash Flow Test

این آزمون الگوهای فصلی در جریان نقدی را تحلیل و ناهنجاری‌ها را شناسایی می‌کند.
شامل تحلیل روند، تشخیص الگوی فصلی، و تحلیل نوسانات جریان نقدی.

مرجع استانداردها:
- ISA 570: Going Concern
- CFE Cash Flow Analysis Techniques
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_select, param_number
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
from collections import defaultdict
import statistics


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_select('analysisType', 'نوع تحلیل',
                    options=['trend', 'seasonal', 'volatility'],
                    default_value='seasonal',
                    labels={'trend': 'تحلیل روند', 
                           'seasonal': 'الگوی فصلی',
                           'volatility': 'تحلیل نوسان'}),
        param_number('periodMonths', 'دوره تحلیل (ماه)', default_value=12),
        param_number('deviationThreshold', 'آستانه انحراف (%)', default_value=40.0),
        param_number('volatilityThreshold', 'آستانه نوسان (%)', default_value=50.0),
        param_number('limit', 'تعداد رکورد', default_value=100)
    ]
    
    result_schema = schema(
        col('Period', 'دوره', 'string'),
        col('CashInflow', 'ورود نقدی', 'currency'),
        col('CashOutflow', 'خروج نقدی', 'currency'),
        col('NetCashFlow', 'خالص جریان نقدی', 'currency'),
        col('SeasonalAverage', 'میانگین فصلی', 'currency'),
        col('Deviation', 'انحراف', 'percent'),
        col('PatternType', 'نوع الگو', 'string'),
        col('RiskIndicator', 'شاخص ریسک', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون الگوی فصلی جریان نقدی"""
    
    analysis_type = get_parameter('analysisType', 'seasonal')
    period_months = int(get_parameter('periodMonths', 12))
    deviation_threshold = get_parameter('deviationThreshold', 40.0)
    volatility_threshold = get_parameter('volatilityThreshold', 50.0)
    limit = get_parameter('limit', 100)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # گروه‌بندی بر اساس دوره
    period_data = defaultdict(lambda: {'inflow': 0, 'outflow': 0})
    
    for t in results:
        if t.DocumentDate:
            period = t.DocumentDate.strftime('%Y-%m')
            
            # تشخیص ورودی و خروجی نقدی
            if t.Credit and t.Credit > 0:
                period_data[period]['inflow'] += t.Credit
            if t.Debit and t.Debit > 0:
                period_data[period]['outflow'] += t.Debit
    
    if len(period_data) < 3:
        return []
    
    # مرتب‌سازی دوره‌ها
    sorted_periods = sorted(period_data.items())
    
    # تحلیل بر اساس نوع انتخابی
    data = []
    
    if analysis_type == 'trend':
        data = analyze_cash_flow_trend(sorted_periods, deviation_threshold)
    elif analysis_type == 'seasonal':
        data = analyze_seasonal_pattern(sorted_periods, period_months, deviation_threshold)
    elif analysis_type == 'volatility':
        data = analyze_cash_flow_volatility(sorted_periods, volatility_threshold)
    
    # مرتب‌سازی بر اساس انحراف
    data.sort(key=lambda x: abs(x['Deviation']), reverse=True)
    
    return data[:limit]


def analyze_cash_flow_trend(sorted_periods, threshold):
    """تحلیل روند جریان نقدی"""
    data = []
    net_flows = [flows['inflow'] - flows['outflow'] for _, flows in sorted_periods]
    
    # محاسبه میانگین کلی
    avg_net_flow = statistics.mean(net_flows) if net_flows else 0
    
    for i, (period, flows) in enumerate(sorted_periods):
        inflow = flows['inflow']
        outflow = flows['outflow']
        net_flow = inflow - outflow
        
        # محاسبه میانگین متحرک (3 دوره)
        start_idx = max(0, i - 2)
        window_flows = net_flows[start_idx:i+1]
        moving_avg = statistics.mean(window_flows) if window_flows else 0
        
        deviation = ((net_flow - moving_avg) / abs(moving_avg) * 100) if moving_avg != 0 else 0
        
        # تعیین نوع الگو و ریسک
        pattern_type = determine_cash_flow_pattern(net_flow, moving_avg, threshold)
        risk_indicator = determine_cash_flow_risk(deviation, net_flow, threshold)
        
        row = {
            'Period': period,
            'CashInflow': round(inflow, 2),
            'CashOutflow': round(outflow, 2),
            'NetCashFlow': round(net_flow, 2),
            'SeasonalAverage': round(moving_avg, 2),
            'Deviation': round(deviation, 2),
            'PatternType': pattern_type,
            'RiskIndicator': risk_indicator
        }
        data.append(row)
    
    return data


def analyze_seasonal_pattern(sorted_periods, period_months, threshold):
    """تحلیل الگوی فصلی جریان نقدی"""
    data = []
    net_flows = [flows['inflow'] - flows['outflow'] for _, flows in sorted_periods]
    
    # محاسبه شاخص‌های فصلی
    monthly_flows = defaultdict(list)
    for i, (period, flows) in enumerate(sorted_periods):
        month_index = i % period_months
        net_flow = flows['inflow'] - flows['outflow']
        monthly_flows[month_index].append(net_flow)
    
    # محاسبه میانگین هر ماه
    monthly_averages = {}
    for month_index, values in monthly_flows.items():
        monthly_averages[month_index] = statistics.mean(values) if values else 0
    
    # تحلیل هر دوره
    for i, (period, flows) in enumerate(sorted_periods):
        inflow = flows['inflow']
        outflow = flows['outflow']
        net_flow = inflow - outflow
        
        month_index = i % period_months
        seasonal_avg = monthly_averages.get(month_index, 0)
        
        deviation = ((net_flow - seasonal_avg) / abs(seasonal_avg) * 100) if seasonal_avg != 0 else 0
        
        # تعیین نوع الگو و ریسک
        pattern_type = determine_cash_flow_pattern(net_flow, seasonal_avg, threshold)
        risk_indicator = determine_cash_flow_risk(deviation, net_flow, threshold)
        
        row = {
            'Period': period,
            'CashInflow': round(inflow, 2),
            'CashOutflow': round(outflow, 2),
            'NetCashFlow': round(net_flow, 2),
            'SeasonalAverage': round(seasonal_avg, 2),
            'Deviation': round(deviation, 2),
            'PatternType': pattern_type,
            'RiskIndicator': risk_indicator
        }
        data.append(row)
    
    return data


def analyze_cash_flow_volatility(sorted_periods, threshold):
    """تحلیل نوسانات جریان نقدی"""
    data = []
    net_flows = [flows['inflow'] - flows['outflow'] for _, flows in sorted_periods]
    
    # محاسبه آمار کلی
    if len(net_flows) > 1:
        avg_net_flow = statistics.mean(net_flows)
        stdev_net_flow = statistics.stdev(net_flows)
        volatility = (stdev_net_flow / abs(avg_net_flow) * 100) if avg_net_flow != 0 else 0
    else:
        avg_net_flow = net_flows[0] if net_flows else 0
        volatility = 0
    
    for i, (period, flows) in enumerate(sorted_periods):
        inflow = flows['inflow']
        outflow = flows['outflow']
        net_flow = inflow - outflow
        
        # محاسبه نوسان محلی (5 دوره)
        start_idx = max(0, i - 4)
        window_flows = net_flows[start_idx:i+1]
        
        if len(window_flows) > 1:
            window_avg = statistics.mean(window_flows)
            window_stdev = statistics.stdev(window_flows)
            local_volatility = (window_stdev / abs(window_avg) * 100) if window_avg != 0 else 0
        else:
            window_avg = window_flows[0] if window_flows else 0
            local_volatility = 0
        
        deviation = local_volatility
        
        # تعیین نوع الگو و ریسک
        if local_volatility >= threshold * 1.5:
            pattern_type = 'نوسان بسیار بالا'
            risk_indicator = 'بحرانی'
        elif local_volatility >= threshold:
            pattern_type = 'نوسان بالا'
            risk_indicator = 'بالا'
        elif net_flow < 0:
            pattern_type = 'جریان نقدی منفی'
            risk_indicator = 'متوسط'
        else:
            pattern_type = 'پایدار'
            risk_indicator = 'پایین'
        
        row = {
            'Period': period,
            'CashInflow': round(inflow, 2),
            'CashOutflow': round(outflow, 2),
            'NetCashFlow': round(net_flow, 2),
            'SeasonalAverage': round(window_avg, 2),
            'Deviation': round(deviation, 2),
            'PatternType': pattern_type,
            'RiskIndicator': risk_indicator
        }
        data.append(row)
    
    return data


def determine_cash_flow_pattern(net_flow, average, threshold):
    """تعیین نوع الگوی جریان نقدی"""
    if average == 0:
        if net_flow < 0:
            return 'جریان نقدی منفی'
        else:
            return 'جریان نقدی مثبت'
    
    deviation = ((net_flow - average) / abs(average) * 100)
    
    if net_flow < 0 and average >= 0:
        return 'تغییر به منفی'
    elif net_flow >= 0 and average < 0:
        return 'بهبود به مثبت'
    elif abs(deviation) < threshold:
        return 'پایدار'
    elif deviation > threshold * 1.5:
        return 'رشد بسیار بالا'
    elif deviation > threshold:
        return 'رشد قابل توجه'
    elif deviation < -threshold * 1.5:
        return 'کاهش شدید'
    else:
        return 'کاهش قابل توجه'


def determine_cash_flow_risk(deviation, net_flow, threshold):
    """تعیین شاخص ریسک جریان نقدی"""
    if net_flow < 0:
        if abs(deviation) >= threshold * 1.5:
            return 'بحرانی'
        else:
            return 'بالا'
    elif abs(deviation) >= threshold * 1.5:
        return 'بالا'
    elif abs(deviation) >= threshold:
        return 'متوسط'
    else:
        return 'پایین'
