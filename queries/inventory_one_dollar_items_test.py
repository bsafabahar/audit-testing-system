"""
آزمون اقلام یک‌ریالی
One Dollar Items Test

این آزمون اقلام موجودی با ارزش خیلی کم (یک ریال) را شناسایی می‌کند.
این اقلام ممکن است برای مخفی کردن کمبود موجودی استفاده شده باشند.
"""
from typing import List, Dict, Any
from models import InventoryIssues
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
    query = session.query(InventoryIssues)
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
        if t.ItemCode and t.UnitPrice is not None:
            item_code = t.ItemCode
            unit_price = float(t.UnitPrice)
            
            item_data[item_code]['current_price'] = unit_price
            
            if unit_price > 1:
                item_data[item_code]['prices'].append(unit_price)
            
            if t.Quantity:
                item_data[item_code]['quantity'] += float(t.Quantity)
            
            if t.ItemName:
                item_data[item_code]['description'] = t.ItemName
            
            if t.IssueDate:
                if item_data[item_code]['last_date'] is None or \
                   t.IssueDate > item_data[item_code]['last_date']:
                    item_data[item_code]['last_date'] = t.IssueDate
    
    # یافتن اقلام یک‌ریالی
    data = []
    for item_code, item_info in item_data.items():
        current_price = item_info['current_price']
        
        if current_price <= 1 and item_info['quantity'] >= min_quantity:
            avg_prev_price = 0
            if item_info['prices']:
                avg_prev_price = sum(item_info['prices']) / len(item_info['prices'])
            
            total_value = current_price * item_info['quantity']
            
            row = {
                'ItemID': str(item_code),
                'ItemDescription': item_info['description'],
                'UnitPrice': round(current_price, 2),
                'Quantity': int(item_info['quantity']),
                'TotalValue': round(total_value, 2),
                'LastTransactionDate': item_info['last_date'].strftime('%Y-%m-%d') if item_info['last_date'] else '',
                'AveragePreviousPrice': round(avg_prev_price, 2)
            }
            data.append(row)
    
    # مرتب‌سازی بر اساس تعداد
    data.sort(key=lambda x: x['Quantity'], reverse=True)
    
    return data
