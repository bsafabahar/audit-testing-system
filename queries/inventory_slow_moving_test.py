"""
آزمون موجودی راکد
Slow Moving Inventory Test

این آزمون اقلام موجودی راکد را شناسایی می‌کند.
اقلامی که برای مدت طولانی حرکتی نداشته‌اند، شناسایی می‌شوند.
"""
from typing import List, Dict, Any
from models import InventoryIssues
from parameters import param_number
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
from collections import defaultdict
from datetime import datetime, timedelta


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_number('daysSinceLastMove', 'روزهای بدون حرکت', default_value=90)
    ]
    
    result_schema = schema(
        col('ItemID', 'شناسه قلم', 'string'),
        col('ItemDescription', 'شرح قلم', 'string'),
        col('CurrentQuantity', 'موجودی فعلی', 'integer'),
        col('UnitPrice', 'قیمت واحد', 'money'),
        col('TotalValue', 'ارزش کل', 'money'),
        col('LastMovementDate', 'آخرین حرکت', 'date'),
        col('DaysSinceLastMove', 'روزهای بدون حرکت', 'integer'),
        col('LastTransactionType', 'نوع آخرین تراکنش', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون موجودی راکد"""
    
    days_threshold = get_parameter('daysSinceLastMove', 90)
    
    # دریافت داده‌ها
    query = session.query(InventoryIssues)
    results = query.all()
    
    # گروه‌بندی بر اساس قلم
    item_movements = defaultdict(lambda: {
        'quantity': 0,
        'price': 0,
        'description': '',
        'last_date': None,
        'last_type': ''
    })
    
    for t in results:
        if t.ItemCode:
            item_code = t.ItemCode
            
            if t.Quantity:
                item_movements[item_code]['quantity'] += float(t.Quantity)
            
            if t.UnitPrice:
                item_movements[item_code]['price'] = float(t.UnitPrice)
            
            if t.ItemName:
                item_movements[item_code]['description'] = t.ItemName
            
            if t.IssueDate:
                if item_movements[item_code]['last_date'] is None or \
                   t.IssueDate > item_movements[item_code]['last_date']:
                    item_movements[item_code]['last_date'] = t.IssueDate
                    # InventoryIssues doesn't have TransactionType, it's all issues
                    item_movements[item_code]['last_type'] = 'Issue'
    
    # یافتن اقلام راکد
    data = []
    current_date = datetime.now()
    
    for item_code, movement in item_movements.items():
        if movement['last_date'] and movement['quantity'] > 0:
            days_since = (current_date - datetime.combine(movement['last_date'], datetime.min.time())).days
            
            if days_since >= days_threshold:
                total_value = movement['quantity'] * movement['price']
                
                row = {
                    'ItemID': str(item_code),
                    'ItemDescription': movement['description'],
                    'CurrentQuantity': int(movement['quantity']),
                    'UnitPrice': round(movement['price'], 2),
                    'TotalValue': round(total_value, 2),
                    'LastMovementDate': movement['last_date'].strftime('%Y-%m-%d'),
                    'DaysSinceLastMove': days_since,
                    'LastTransactionType': movement['last_type']
                }
                data.append(row)
    
    # مرتب‌سازی بر اساس روزهای بدون حرکت
    data.sort(key=lambda x: x['DaysSinceLastMove'], reverse=True)
    
    return data
