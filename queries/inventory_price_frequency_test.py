"""
آزمون فراوانی نرخ خرید
Price Frequency Test

این آزمون فراوانی نرخ‌های خرید را تحلیل می‌کند.
نرخ‌هایی که با فراوانی غیرعادی ظاهر می‌شوند، شناسایی می‌شوند.
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_number
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
from collections import Counter


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_number('minFrequency', 'حداقل فراوانی', default_value=5)
    ]
    
    result_schema = schema(
        col('ItemID', 'شناسه قلم', 'string'),
        col('UnitPrice', 'قیمت واحد', 'money'),
        col('Frequency', 'فراوانی', 'integer'),
        col('TotalQuantity', 'تعداد کل', 'integer'),
        col('TotalValue', 'ارزش کل', 'money'),
        col('FirstDate', 'اولین تاریخ', 'date'),
        col('LastDate', 'آخرین تاریخ', 'date'),
        col('DaySpan', 'بازه زمانی (روز)', 'integer')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون فراوانی نرخ خرید"""
    
    min_frequency = get_parameter('minFrequency', 5)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # گروه‌بندی بر اساس قلم و قیمت
    price_data = {}
    
    for t in results:
        if hasattr(t, 'ItemID') and hasattr(t, 'UnitPrice'):
            if t.ItemID and t.UnitPrice and t.UnitPrice > 0:
                key = (t.ItemID, t.UnitPrice)
                
                if key not in price_data:
                    price_data[key] = {
                        'frequency': 0,
                        'quantity': 0,
                        'dates': []
                    }
                
                price_data[key]['frequency'] += 1
                
                if hasattr(t, 'Quantity') and t.Quantity:
                    price_data[key]['quantity'] += t.Quantity
                
                if hasattr(t, 'TransactionDate') and t.TransactionDate:
                    price_data[key]['dates'].append(t.TransactionDate)
    
    # یافتن قیمت‌های با فراوانی بالا
    data = []
    
    for (item_id, price), info in price_data.items():
        if info['frequency'] >= min_frequency:
            dates = sorted(info['dates']) if info['dates'] else []
            first_date = dates[0] if dates else None
            last_date = dates[-1] if dates else None
            
            day_span = 0
            if first_date and last_date:
                day_span = (last_date - first_date).days
            
            total_value = price * info['quantity']
            
            row = {
                'ItemID': str(item_id),
                'UnitPrice': round(price, 2),
                'Frequency': info['frequency'],
                'TotalQuantity': info['quantity'],
                'TotalValue': round(total_value, 2),
                'FirstDate': first_date.strftime('%Y-%m-%d') if first_date else '',
                'LastDate': last_date.strftime('%Y-%m-%d') if last_date else '',
                'DaySpan': day_span
            }
            data.append(row)
    
    # مرتب‌سازی بر اساس فراوانی
    data.sort(key=lambda x: x['Frequency'], reverse=True)
    
    return data
