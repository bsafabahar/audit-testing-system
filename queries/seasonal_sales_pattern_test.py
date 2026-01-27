"""
آزمون الگوی فصلی فروش
Seasonal Sales Pattern Test

این آزمون الگوهای فصلی در فروش را شناسایی و انحرافات از الگوهای طبیعی را تشخیص می‌دهد.
از روش‌های تجزیه سری زمانی، میانگین متحرک و شاخص فصلی استفاده می‌شود.

مرجع استانداردها:
- ISA 520: Analytical Procedures
- Time Series Analysis Techniques
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
    from parameters import option
    
    parameters = [
        param_select('analysisMethod', 'روش تحلیل',
                    options=[
                        option('time_series', 'تجزیه سری زمانی'),
                        option('moving_average', 'میانگین متحرک'),
                        option('seasonal_index', 'شاخص فصلی')
                    ],
                    default_value='time_series'),
        param_number('windowSize', 'اندازه پنجره (ماه)', default_value=3),
        param_number('deviationThreshold', 'آستانه انحراف (%)', default_value=30.0),
        param_number('seasonalPeriod', 'دوره فصلی (ماه)', default_value=12),
        param_number('limit', 'تعداد رکورد', default_value=100)
    ]
    
    result_schema = schema(
        col('Period', 'دوره', 'string'),
        col('SalesAmount', 'مبلغ فروش', 'currency'),
        col('SeasonalAverage', 'میانگین فصلی', 'currency'),
        col('SeasonalIndex', 'شاخص فصلی', 'decimal'),
        col('Deviation', 'انحراف', 'percent'),
        col('PatternType', 'نوع الگو', 'string'),
        col('Anomaly', 'ناهنجاری', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون الگوی فصلی فروش"""
    
    analysis_method = get_parameter('analysisMethod', 'time_series')
    window_size = int(get_parameter('windowSize', 3))
    deviation_threshold = get_parameter('deviationThreshold', 30.0)
    seasonal_period = int(get_parameter('seasonalPeriod', 12))
    limit = get_parameter('limit', 100)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # گروه‌بندی بر اساس دوره
    period_sales = defaultdict(lambda: {'amount': 0, 'count': 0})
    
    for t in results:
        if t.DocumentDate:
            period = t.DocumentDate.strftime('%Y-%m')
            
            if t.Credit and t.Credit > 0:
                period_sales[period]['amount'] += t.Credit
                period_sales[period]['count'] += 1
    
    if len(period_sales) < seasonal_period:
        return []
    
    # مرتب‌سازی دوره‌ها
    sorted_periods = sorted(period_sales.items())
    
    # تحلیل بر اساس روش انتخابی
    data = []
    
    if analysis_method == 'time_series':
        seasonal_indices = calculate_seasonal_indices(sorted_periods, seasonal_period)
        data = analyze_time_series(sorted_periods, seasonal_indices, deviation_threshold)
    elif analysis_method == 'moving_average':
        data = analyze_moving_average(sorted_periods, window_size, deviation_threshold)
    elif analysis_method == 'seasonal_index':
        seasonal_indices = calculate_seasonal_indices(sorted_periods, seasonal_period)
        data = analyze_seasonal_index(sorted_periods, seasonal_indices, seasonal_period, deviation_threshold)
    
    # مرتب‌سازی بر اساس انحراف
    data.sort(key=lambda x: abs(x['Deviation']), reverse=True)
    
    return data[:limit]


def calculate_seasonal_indices(sorted_periods, seasonal_period):
    """محاسبه شاخص‌های فصلی"""
    amounts = [d['amount'] for _, d in sorted_periods]
    
    # محاسبه میانگین هر ماه در چرخه فصلی
    monthly_data = defaultdict(list)
    for i, (period, data) in enumerate(sorted_periods):
        month_index = i % seasonal_period
        monthly_data[month_index].append(data['amount'])
    
    # محاسبه میانگین کلی
    overall_mean = statistics.mean(amounts) if amounts else 1
    
    # محاسبه شاخص فصلی برای هر ماه
    seasonal_indices = {}
    for month_index, values in monthly_data.items():
        if values:
            month_mean = statistics.mean(values)
            seasonal_indices[month_index] = month_mean / overall_mean if overall_mean > 0 else 1
        else:
            seasonal_indices[month_index] = 1
    
    return seasonal_indices


def analyze_time_series(sorted_periods, seasonal_indices, threshold):
    """تجزیه سری زمانی"""
    data = []
    amounts = [d['amount'] for _, d in sorted_periods]
    overall_mean = statistics.mean(amounts) if amounts else 0
    
    for i, (period, sales_data) in enumerate(sorted_periods):
        month_index = i % len(seasonal_indices)
        seasonal_index = seasonal_indices.get(month_index, 1)
        seasonal_avg = overall_mean * seasonal_index
        
        amount = sales_data['amount']
        deviation = ((amount - seasonal_avg) / seasonal_avg * 100) if seasonal_avg > 0 else 0
        
        # تعیین نوع الگو
        pattern_type = determine_pattern_type(deviation, threshold)
        anomaly = determine_anomaly(deviation, threshold)
        
        row = {
            'Period': period,
            'SalesAmount': round(amount, 2),
            'SeasonalAverage': round(seasonal_avg, 2),
            'SeasonalIndex': round(seasonal_index, 2),
            'Deviation': round(deviation, 2),
            'PatternType': pattern_type,
            'Anomaly': anomaly
        }
        data.append(row)
    
    return data


def analyze_moving_average(sorted_periods, window_size, threshold):
    """تحلیل میانگین متحرک"""
    data = []
    amounts = [d['amount'] for _, d in sorted_periods]
    
    for i, (period, sales_data) in enumerate(sorted_periods):
        amount = sales_data['amount']
        
        # محاسبه میانگین متحرک
        start_idx = max(0, i - window_size + 1)
        window_amounts = amounts[start_idx:i+1]
        moving_avg = statistics.mean(window_amounts) if window_amounts else 0
        
        # محاسبه شاخص فصلی (نسبت به میانگین متحرک)
        seasonal_index = amount / moving_avg if moving_avg > 0 else 1
        
        deviation = ((amount - moving_avg) / moving_avg * 100) if moving_avg > 0 else 0
        
        # تعیین نوع الگو
        pattern_type = determine_pattern_type(deviation, threshold)
        anomaly = determine_anomaly(deviation, threshold)
        
        row = {
            'Period': period,
            'SalesAmount': round(amount, 2),
            'SeasonalAverage': round(moving_avg, 2),
            'SeasonalIndex': round(seasonal_index, 2),
            'Deviation': round(deviation, 2),
            'PatternType': pattern_type,
            'Anomaly': anomaly
        }
        data.append(row)
    
    return data


def analyze_seasonal_index(sorted_periods, seasonal_indices, seasonal_period, threshold):
    """تحلیل شاخص فصلی"""
    data = []
    amounts = [d['amount'] for _, d in sorted_periods]
    overall_mean = statistics.mean(amounts) if amounts else 0
    
    for i, (period, sales_data) in enumerate(sorted_periods):
        amount = sales_data['amount']
        month_index = i % seasonal_period
        
        expected_index = seasonal_indices.get(month_index, 1)
        actual_index = amount / overall_mean if overall_mean > 0 else 1
        
        seasonal_avg = overall_mean * expected_index
        deviation = ((actual_index - expected_index) / expected_index * 100) if expected_index > 0 else 0
        
        # تعیین نوع الگو
        pattern_type = determine_pattern_type(deviation, threshold)
        anomaly = determine_anomaly(deviation, threshold)
        
        row = {
            'Period': period,
            'SalesAmount': round(amount, 2),
            'SeasonalAverage': round(seasonal_avg, 2),
            'SeasonalIndex': round(actual_index, 2),
            'Deviation': round(deviation, 2),
            'PatternType': pattern_type,
            'Anomaly': anomaly
        }
        data.append(row)
    
    return data


def determine_pattern_type(deviation, threshold):
    """تعیین نوع الگو"""
    if abs(deviation) < threshold:
        return 'عادی'
    elif deviation > threshold * 2:
        return 'اوج فصلی شدید'
    elif deviation > threshold:
        return 'اوج فصلی'
    elif deviation < -threshold * 2:
        return 'فرود فصلی شدید'
    else:
        return 'فرود فصلی'


def determine_anomaly(deviation, threshold):
    """تعیین ناهنجاری"""
    if abs(deviation) < threshold:
        return 'خیر'
    elif abs(deviation) >= threshold * 2:
        return 'بحرانی'
    else:
        return 'بله'
