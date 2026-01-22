"""
آزمون نرخ سود
Markup Analysis Test

این آزمون نرخ سود (حاشیه سود) تراکنش‌ها را تحلیل می‌کند.
نرخ‌های سود غیرعادی شناسایی می‌شوند.
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_number
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
import statistics


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_number('markupThreshold', 'آستانه نرخ سود (%)', default_value=100.0)
    ]
    
    result_schema = schema(
        col('TransactionID', 'شناسه تراکنش', 'string'),
        col('ItemID', 'شناسه قلم', 'string'),
        col('CostPrice', 'قیمت تمام شده', 'money'),
        col('SalePrice', 'قیمت فروش', 'money'),
        col('Markup', 'نرخ سود', 'percent'),
        col('Profit', 'سود', 'money'),
        col('AvgMarkup', 'میانگین نرخ سود', 'percent'),
        col('Deviation', 'انحراف', 'percent')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون نرخ سود"""
    
    markup_threshold = get_parameter('markupThreshold', 100.0)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # محاسبه نرخ سود
    markups = []
    transaction_data = []
    
    for t in results:
        if hasattr(t, 'CostPrice') and hasattr(t, 'SalePrice'):
            if t.CostPrice and t.SalePrice and t.CostPrice > 0:
                profit = t.SalePrice - t.CostPrice
                markup = (profit / t.CostPrice) * 100
                
                markups.append(markup)
                
                transaction_data.append({
                    'transaction': t,
                    'cost': t.CostPrice,
                    'sale': t.SalePrice,
                    'markup': markup,
                    'profit': profit
                })
    
    if not markups:
        return []
    
    avg_markup = statistics.mean(markups)
    
    # یافتن نرخ‌های سود غیرعادی
    data = []
    
    for td in transaction_data:
        if td['markup'] >= markup_threshold or td['markup'] < 0:
            t = td['transaction']
            deviation = td['markup'] - avg_markup
            
            row = {
                'TransactionID': str(t.TransactionID) if hasattr(t, 'TransactionID') else '',
                'ItemID': str(t.ItemID) if hasattr(t, 'ItemID') else '',
                'CostPrice': round(td['cost'], 2),
                'SalePrice': round(td['sale'], 2),
                'Markup': round(td['markup'], 2),
                'Profit': round(td['profit'], 2),
                'AvgMarkup': round(avg_markup, 2),
                'Deviation': round(deviation, 2)
            }
            data.append(row)
    
    # مرتب‌سازی بر اساس نرخ سود
    data.sort(key=lambda x: x['Markup'], reverse=True)
    
    return data
