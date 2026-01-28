"""
آزمون واریانس فصلی
Seasonal Variance Test

این آزمون واریانس فصلی و انحرافات از الگوی فصلی را شناسایی می‌کند.
انحرافات غیرعادی از الگوی فصلی معمول تشخیص داده می‌شوند.
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
        param_number('varianceThreshold', 'آستانه واریانس (%)', default_value=30.0)
    ]
    
    result_schema = schema(
        col('Month', 'ماه', 'string'),
        col('Year', 'سال', 'integer'),
        col('Amount', 'مبلغ', 'money'),
        col('SeasonalAverage', 'میانگین فصلی', 'money'),
        col('Variance', 'واریانس', 'money'),
        col('VariancePercent', 'درصد واریانس', 'percent'),
        col('Season', 'فصل', 'string'),
        col('DeviationType', 'نوع انحراف', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون واریانس فصلی"""
    
    variance_threshold = get_parameter('varianceThreshold', 30.0)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # گروه‌بندی بر اساس ماه و سال
    month_year_amounts = defaultdict(float)
    month_amounts = defaultdict(list)
    
    for t in results:
        if hasattr(t, 'TransactionDate') and t.TransactionDate:
            month = t.TransactionDate.month
            year = t.TransactionDate.year
            
            key = f"{year}-{month:02d}"
            amount = t.Debit if t.Debit else t.Credit if t.Credit else 0
            
            month_year_amounts[key] += amount
            month_amounts[month].append(amount)
    
    # محاسبه میانگین فصلی برای هر ماه
    seasonal_averages = {}
    for month, amounts in month_amounts.items():
        if amounts:
            seasonal_averages[month] = float(statistics.mean(amounts))
    
    # تعیین فصل
    def get_season(month):
        if month in [1, 2, 3]:
            return 'زمستان'
        elif month in [4, 5, 6]:
            return 'بهار'
        elif month in [7, 8, 9]:
            return 'تابستان'
        else:
            return 'پاییز'
    
    # تحلیل واریانس
    data = []
    
    for key, amount in month_year_amounts.items():
        year, month_str = key.split('-')
        month = int(month_str)
        
        if month in seasonal_averages:
            seasonal_avg = seasonal_averages[month]
            variance = float(amount) - seasonal_avg
            variance_percent = (variance / seasonal_avg * 100) if seasonal_avg > 0 else 0
            
            if abs(variance_percent) >= variance_threshold:
                # تعیین نوع انحراف
                if variance > 0:
                    deviation_type = 'بالاتر از فصلی'
                else:
                    deviation_type = 'پایین‌تر از فصلی'
                
                row = {
                    'Month': month_str,
                    'Year': int(year),
                    'Amount': round(amount, 2),
                    'SeasonalAverage': round(seasonal_avg, 2),
                    'Variance': round(variance, 2),
                    'VariancePercent': round(variance_percent, 2),
                    'Season': get_season(month),
                    'DeviationType': deviation_type
                }
                data.append(row)
    
    # مرتب‌سازی بر اساس درصد واریانس
    data.sort(key=lambda x: abs(x['VariancePercent']), reverse=True)
    
    return data
