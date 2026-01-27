"""
آزمون الگوی فصلی موجودی
Seasonal Inventory Pattern Test

این آزمون الگوهای فصلی در سطح موجودی را تحلیل و ناهنجاری‌ها را شناسایی می‌کند.
شامل تحلیل روند موجودی، نوسانات فصلی، و نسبت گردش موجودی.

مرجع استانداردها:
- ISA 501: Inventory Audit
- Inventory Management Best Practices
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
                    options=['level_trend', 'seasonal_fluctuation', 'turnover'],
                    default_value='seasonal_fluctuation',
                    labels={'level_trend': 'روند سطح موجودی',
                           'seasonal_fluctuation': 'نوسانات فصلی',
                           'turnover': 'تحلیل گردش'}),
        param_number('volatilityThreshold', 'آستانه نوسان (%)', default_value=40.0),
        param_number('turnoverThreshold', 'آستانه گردش (مقدار)', default_value=2.0),
        param_number('seasonalPeriod', 'دوره فصلی (ماه)', default_value=12),
        param_number('limit', 'تعداد رکورد', default_value=100)
    ]
    
    result_schema = schema(
        col('ItemID', 'شناسه کالا', 'string'),
        col('Period', 'دوره', 'string'),
        col('BeginningInventory', 'موجودی اول دوره', 'decimal'),
        col('Purchases', 'خرید', 'decimal'),
        col('Sales', 'فروش', 'decimal'),
        col('EndingInventory', 'موجودی آخر دوره', 'decimal'),
        col('SeasonalAverage', 'میانگین فصلی', 'decimal'),
        col('Volatility', 'نوسان', 'percent'),
        col('TurnoverRatio', 'نسبت گردش', 'decimal'),
        col('PatternType', 'نوع الگو', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون الگوی فصلی موجودی"""
    
    analysis_type = get_parameter('analysisType', 'seasonal_fluctuation')
    volatility_threshold = get_parameter('volatilityThreshold', 40.0)
    turnover_threshold = get_parameter('turnoverThreshold', 2.0)
    seasonal_period = int(get_parameter('seasonalPeriod', 12))
    limit = get_parameter('limit', 100)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # گروه‌بندی بر اساس کالا و دوره
    item_data = defaultdict(lambda: defaultdict(lambda: {'purchases': 0, 'sales': 0}))
    
    for t in results:
        # شناسایی داده‌های موجودی
        item_id = getattr(t, 'ItemID', None) or getattr(t, 'AccountCode', 'UNKNOWN')
        
        if t.DocumentDate:
            period = t.DocumentDate.strftime('%Y-%m')
            
            # تشخیص خرید و فروش
            if t.Debit and t.Debit > 0:
                item_data[item_id][period]['purchases'] += t.Debit
            if t.Credit and t.Credit > 0:
                item_data[item_id][period]['sales'] += t.Credit
    
    # تحلیل بر اساس نوع انتخابی
    data = []
    
    if analysis_type == 'level_trend':
        data = analyze_inventory_level_trend(item_data, volatility_threshold)
    elif analysis_type == 'seasonal_fluctuation':
        data = analyze_seasonal_fluctuation(item_data, seasonal_period, volatility_threshold)
    elif analysis_type == 'turnover':
        data = analyze_turnover_ratio(item_data, turnover_threshold)
    
    # مرتب‌سازی بر اساس نوسان
    data.sort(key=lambda x: x['Volatility'], reverse=True)
    
    return data[:limit]


def analyze_inventory_level_trend(item_data, threshold):
    """تحلیل روند سطح موجودی"""
    data = []
    
    for item_id, periods in item_data.items():
        if len(periods) < 3:
            continue
        
        sorted_periods = sorted(periods.items())
        inventory_levels = []
        current_inventory = 0
        
        # محاسبه سطح موجودی هر دوره
        for period, movements in sorted_periods:
            beginning = current_inventory
            purchases = movements['purchases']
            sales = movements['sales']
            ending = beginning + purchases - sales
            
            inventory_levels.append({
                'period': period,
                'beginning': beginning,
                'purchases': purchases,
                'sales': sales,
                'ending': ending
            })
            
            current_inventory = ending
        
        # محاسبه آمار
        ending_values = [inv['ending'] for inv in inventory_levels]
        if len(ending_values) > 1:
            avg_inventory = statistics.mean(ending_values)
            stdev_inventory = statistics.stdev(ending_values)
            volatility = (stdev_inventory / avg_inventory * 100) if avg_inventory > 0 else 0
            
            # تحلیل روند
            if len(ending_values) >= 3:
                recent_avg = statistics.mean(ending_values[-3:])
                overall_avg = statistics.mean(ending_values[:-3]) if len(ending_values) > 3 else avg_inventory
                trend_change = ((recent_avg - overall_avg) / overall_avg * 100) if overall_avg > 0 else 0
                
                pattern_type = determine_inventory_trend_pattern(trend_change, volatility, threshold)
            else:
                pattern_type = 'داده ناکافی'
                trend_change = 0
            
            # فقط موارد با نوسان بالا یا الگوی خاص
            if volatility >= threshold or abs(trend_change) >= threshold:
                for inv in inventory_levels:
                    row = {
                        'ItemID': str(item_id),
                        'Period': inv['period'],
                        'BeginningInventory': round(inv['beginning'], 2),
                        'Purchases': round(inv['purchases'], 2),
                        'Sales': round(inv['sales'], 2),
                        'EndingInventory': round(inv['ending'], 2),
                        'SeasonalAverage': round(avg_inventory, 2),
                        'Volatility': round(volatility, 2),
                        'TurnoverRatio': 0,
                        'PatternType': pattern_type
                    }
                    data.append(row)
    
    return data


def analyze_seasonal_fluctuation(item_data, seasonal_period, threshold):
    """تحلیل نوسانات فصلی"""
    data = []
    
    for item_id, periods in item_data.items():
        if len(periods) < seasonal_period:
            continue
        
        sorted_periods = sorted(periods.items())
        inventory_levels = []
        current_inventory = 0
        
        # محاسبه سطح موجودی
        for period, movements in sorted_periods:
            beginning = current_inventory
            purchases = movements['purchases']
            sales = movements['sales']
            ending = beginning + purchases - sales
            
            inventory_levels.append({
                'period': period,
                'beginning': beginning,
                'purchases': purchases,
                'sales': sales,
                'ending': ending
            })
            
            current_inventory = ending
        
        # محاسبه میانگین‌های فصلی
        monthly_inventories = defaultdict(list)
        for i, inv in enumerate(inventory_levels):
            month_index = i % seasonal_period
            monthly_inventories[month_index].append(inv['ending'])
        
        monthly_averages = {}
        for month_index, values in monthly_inventories.items():
            monthly_averages[month_index] = statistics.mean(values) if values else 0
        
        # محاسبه نوسان کلی
        ending_values = [inv['ending'] for inv in inventory_levels]
        if len(ending_values) > 1:
            avg_inventory = statistics.mean(ending_values)
            stdev_inventory = statistics.stdev(ending_values)
            volatility = (stdev_inventory / avg_inventory * 100) if avg_inventory > 0 else 0
        else:
            volatility = 0
        
        # فقط موارد با نوسان بالا
        if volatility >= threshold:
            for i, inv in enumerate(inventory_levels):
                month_index = i % seasonal_period
                seasonal_avg = monthly_averages.get(month_index, avg_inventory)
                
                deviation = ((inv['ending'] - seasonal_avg) / seasonal_avg * 100) if seasonal_avg > 0 else 0
                pattern_type = determine_seasonal_pattern(deviation, volatility, threshold)
                
                row = {
                    'ItemID': str(item_id),
                    'Period': inv['period'],
                    'BeginningInventory': round(inv['beginning'], 2),
                    'Purchases': round(inv['purchases'], 2),
                    'Sales': round(inv['sales'], 2),
                    'EndingInventory': round(inv['ending'], 2),
                    'SeasonalAverage': round(seasonal_avg, 2),
                    'Volatility': round(volatility, 2),
                    'TurnoverRatio': 0,
                    'PatternType': pattern_type
                }
                data.append(row)
    
    return data


def analyze_turnover_ratio(item_data, threshold):
    """تحلیل نسبت گردش موجودی"""
    data = []
    
    for item_id, periods in item_data.items():
        if len(periods) < 3:
            continue
        
        sorted_periods = sorted(periods.items())
        inventory_levels = []
        current_inventory = 0
        
        # محاسبه سطح موجودی و گردش
        for period, movements in sorted_periods:
            beginning = current_inventory
            purchases = movements['purchases']
            sales = movements['sales']
            ending = beginning + purchases - sales
            
            # محاسبه نسبت گردش
            avg_inventory = (beginning + ending) / 2 if (beginning + ending) > 0 else 1
            turnover = sales / avg_inventory if avg_inventory > 0 else 0
            
            inventory_levels.append({
                'period': period,
                'beginning': beginning,
                'purchases': purchases,
                'sales': sales,
                'ending': ending,
                'turnover': turnover
            })
            
            current_inventory = ending
        
        # محاسبه آمار
        ending_values = [inv['ending'] for inv in inventory_levels]
        turnover_values = [inv['turnover'] for inv in inventory_levels if inv['turnover'] > 0]
        
        if len(ending_values) > 1:
            avg_inventory = statistics.mean(ending_values)
            stdev_inventory = statistics.stdev(ending_values)
            volatility = (stdev_inventory / avg_inventory * 100) if avg_inventory > 0 else 0
            avg_turnover = statistics.mean(turnover_values) if turnover_values else 0
        else:
            volatility = 0
            avg_turnover = 0
        
        # فقط موارد با گردش پایین یا مشکل‌دار
        if avg_turnover < threshold or volatility >= 30:
            for inv in inventory_levels:
                pattern_type = determine_turnover_pattern(inv['turnover'], avg_turnover, threshold)
                
                row = {
                    'ItemID': str(item_id),
                    'Period': inv['period'],
                    'BeginningInventory': round(inv['beginning'], 2),
                    'Purchases': round(inv['purchases'], 2),
                    'Sales': round(inv['sales'], 2),
                    'EndingInventory': round(inv['ending'], 2),
                    'SeasonalAverage': round(avg_inventory, 2),
                    'Volatility': round(volatility, 2),
                    'TurnoverRatio': round(inv['turnover'], 2),
                    'PatternType': pattern_type
                }
                data.append(row)
    
    return data


def determine_inventory_trend_pattern(trend_change, volatility, threshold):
    """تعیین نوع الگوی روند موجودی"""
    if volatility >= threshold * 1.5:
        return 'نوسان بسیار بالا'
    elif volatility >= threshold:
        return 'نوسان بالا'
    elif trend_change >= threshold:
        return 'رشد قابل توجه'
    elif trend_change <= -threshold:
        return 'کاهش قابل توجه'
    else:
        return 'پایدار'


def determine_seasonal_pattern(deviation, volatility, threshold):
    """تعیین نوع الگوی فصلی"""
    if volatility >= threshold * 1.5:
        return 'نوسان شدید فصلی'
    elif abs(deviation) >= threshold * 1.5:
        if deviation > 0:
            return 'اوج فصلی شدید'
        else:
            return 'فرود فصلی شدید'
    elif abs(deviation) >= threshold:
        if deviation > 0:
            return 'اوج فصلی'
        else:
            return 'فرود فصلی'
    else:
        return 'الگوی عادی'


def determine_turnover_pattern(turnover, avg_turnover, threshold):
    """تعیین نوع الگوی گردش"""
    if turnover == 0:
        return 'بدون فروش'
    elif turnover < threshold * 0.5:
        return 'گردش بسیار پایین'
    elif turnover < threshold:
        return 'گردش پایین'
    elif turnover < avg_turnover * 0.7:
        return 'کمتر از میانگین'
    elif turnover > avg_turnover * 1.5:
        return 'بالاتر از میانگین'
    else:
        return 'عادی'
