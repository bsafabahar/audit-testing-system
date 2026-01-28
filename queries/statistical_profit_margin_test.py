"""
آزمون نوسانات حاشیه سود
Profit Margin Volatility Test

این آزمون نوسانات حاشیه سود را بررسی می‌کند.
تراکنش‌هایی که حاشیه سود غیرعادی دارند، شناسایی می‌شوند.
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
        param_number('marginThreshold', 'آستانه انحراف حاشیه (%)', default_value=30.0)
    ]
    
    result_schema = schema(
        col('TransactionID', 'شناسه تراکنش', 'string'),
        col('SaleAmount', 'مبلغ فروش', 'money'),
        col('CostAmount', 'مبلغ بهای تمام شده', 'money'),
        col('ProfitMargin', 'حاشیه سود', 'percent'),
        col('AvgMargin', 'میانگین حاشیه', 'percent'),
        col('Deviation', 'انحراف', 'percent'),
        col('ZScore', 'Z-Score', 'number')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون نوسانات حاشیه سود"""
    
    margin_threshold = get_parameter('marginThreshold', 30.0)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # محاسبه حاشیه سود
    margins = []
    transaction_data = []
    
    for t in results:
        if hasattr(t, 'SaleAmount') and hasattr(t, 'CostAmount'):
            if t.SaleAmount and t.CostAmount and t.SaleAmount > 0:
                profit = t.SaleAmount - t.CostAmount
                margin = (profit / t.SaleAmount) * 100
                margins.append(margin)
                transaction_data.append({
                    'transaction': t,
                    'sale': t.SaleAmount,
                    'cost': t.CostAmount,
                    'margin': margin
                })
    
    if len(margins) < 2:
        return []
    
    # محاسبه میانگین و انحراف معیار
    avg_margin = float(statistics.mean(margins))
    stdev_margin = float(statistics.stdev(margins))
    
    if stdev_margin == 0:
        return []
    
    # یافتن تراکنش‌های با نوسان بالا
    data = []
    for td in transaction_data:
        deviation = abs(td['margin'] - avg_margin)
        z_score = (td['margin'] - avg_margin) / stdev_margin
        
        if deviation >= margin_threshold:
            t = td['transaction']
            row = {
                'TransactionID': str(t.TransactionID) if hasattr(t, 'TransactionID') else '',
                'SaleAmount': round(td['sale'], 2),
                'CostAmount': round(td['cost'], 2),
                'ProfitMargin': round(td['margin'], 2),
                'AvgMargin': round(avg_margin, 2),
                'Deviation': round(deviation, 2),
                'ZScore': round(z_score, 4)
            }
            data.append(row)
    
    # مرتب‌سازی بر اساس انحراف
    data.sort(key=lambda x: x['Deviation'], reverse=True)
    
    return data
