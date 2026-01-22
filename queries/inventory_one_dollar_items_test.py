"""
آزمون اقلام یک‌ریالی
One Dollar Items Test

این آزمون اقلام موجودی با ارزش خیلی کم (یک ریال) را شناسایی می‌کند.
این اقلام ممکن است برای مخفی کردن کمبود موجودی استفاده شده باشند.
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_number
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
from collections import defaultdict


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_number('minQuantity', 'حداقل تعداد', default_value=1)
    ]
    
    result_schema = schema(
        col('ItemID', 'شناسه قلم', 'string'),
        col('ItemDescription', 'شرح قلم', 'string'),
        col('UnitPrice', 'قیمت واحد', 'money'),
        col('Quantity', 'تعداد', 'integer'),
        col('TotalValue', 'ارزش کل', 'money'),
        col('LastTransactionDate', 'آخرین تراکنش', 'date'),
        col('AveragePreviousPrice', 'میانگین قیمت قبلی', 'money')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون اقلام یک‌ریالی"""
    
    min_quantity = get_parameter('minQuantity', 1)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # گروه‌بندی بر اساس قلم
    item_data = defaultdict(lambda: {
        'prices': [],
        'quantity': 0,
        'description': '',
        'last_date': None,
        'current_price': 0
    })
    
    for t in results:
        if hasattr(t, 'ItemID') and hasattr(t, 'UnitPrice'):
            if t.ItemID and t.UnitPrice is not None:
                item_id = t.ItemID
                
                item_data[item_id]['current_price'] = t.UnitPrice
                
                if t.UnitPrice > 1:
                    item_data[item_id]['prices'].append(t.UnitPrice)
                
                if hasattr(t, 'Quantity') and t.Quantity:
                    item_data[item_id]['quantity'] += t.Quantity
                
                if hasattr(t, 'ItemDescription') and t.ItemDescription:
                    item_data[item_id]['description'] = t.ItemDescription
                
                if hasattr(t, 'TransactionDate') and t.TransactionDate:
                    if item_data[item_id]['last_date'] is None or \
                       t.TransactionDate > item_data[item_id]['last_date']:
                        item_data[item_id]['last_date'] = t.TransactionDate
    
    # یافتن اقلام یک‌ریالی
    data = []
    for item_id, item_info in item_data.items():
        current_price = item_info['current_price']
        
        if current_price <= 1 and item_info['quantity'] >= min_quantity:
            avg_prev_price = 0
            if item_info['prices']:
                avg_prev_price = sum(item_info['prices']) / len(item_info['prices'])
            
            total_value = current_price * item_info['quantity']
            
            row = {
                'ItemID': str(item_id),
                'ItemDescription': item_info['description'],
                'UnitPrice': round(current_price, 2),
                'Quantity': item_info['quantity'],
                'TotalValue': round(total_value, 2),
                'LastTransactionDate': item_info['last_date'].strftime('%Y-%m-%d') if item_info['last_date'] else '',
                'AveragePreviousPrice': round(avg_prev_price, 2)
            }
            data.append(row)
    
    # مرتب‌سازی بر اساس تعداد
    data.sort(key=lambda x: x['Quantity'], reverse=True)
    
    return data
