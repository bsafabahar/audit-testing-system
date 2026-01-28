"""
آزمون نوسانات نرخ خرید
Price Volatility Test

این آزمون نوسانات نرخ خرید اقلام را بررسی می‌کند.
اقلامی که نوسانات قیمتی بالایی دارند، شناسایی می‌شوند.
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
        param_number('cvThreshold', 'آستانه ضریب تغییرات (%)', default_value=20.0),
        param_number('minTransactions', 'حداقل تعداد تراکنش', default_value=3)
    ]
    
    result_schema = schema(
        col('ItemID', 'شناسه قلم', 'string'),
        col('TransactionCount', 'تعداد تراکنش', 'integer'),
        col('MinPrice', 'حداقل قیمت', 'money'),
        col('MaxPrice', 'حداکثر قیمت', 'money'),
        col('AvgPrice', 'میانگین قیمت', 'money'),
        col('StdDev', 'انحراف معیار', 'money'),
        col('CoefficientOfVariation', 'ضریب تغییرات', 'percent'),
        col('PriceRange', 'دامنه قیمت', 'money')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون نوسانات قیمت"""
    
    cv_threshold = get_parameter('cvThreshold', 20.0)
    min_trans = get_parameter('minTransactions', 3)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # گروه‌بندی بر اساس قلم
    item_prices = defaultdict(list)
    
    for t in results:
        if hasattr(t, 'ItemID') and hasattr(t, 'UnitPrice'):
            if t.ItemID and t.UnitPrice and t.UnitPrice > 0:
                item_prices[t.ItemID].append(t.UnitPrice)
    
    # تحلیل نوسانات
    data = []
    for item_id, prices in item_prices.items():
        if len(prices) >= min_trans:
            min_price = float(min(prices))
            max_price = float(max(prices))
            avg_price = float(statistics.mean(prices))
            
            if len(prices) > 1:
                stdev = float(statistics.stdev(prices))
                cv = (stdev / avg_price) * 100 if avg_price > 0 else 0
                
                if cv >= cv_threshold:
                    row = {
                        'ItemID': str(item_id),
                        'TransactionCount': len(prices),
                        'MinPrice': round(min_price, 2),
                        'MaxPrice': round(max_price, 2),
                        'AvgPrice': round(avg_price, 2),
                        'StdDev': round(stdev, 2),
                        'CoefficientOfVariation': round(cv, 2),
                        'PriceRange': round(max_price - min_price, 2)
                    }
                    data.append(row)
    
    # مرتب‌سازی بر اساس ضریب تغییرات
    data.sort(key=lambda x: x['CoefficientOfVariation'], reverse=True)
    
    return data
