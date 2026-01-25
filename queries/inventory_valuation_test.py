"""
آزمون ارزیابی موجودی
Inventory Valuation Test

این آزمون ارزش‌گذاری موجودی را با روش‌های مختلف بررسی می‌کند.
اختلافات بین روش‌های مختلف ارزش‌گذاری شناسایی می‌شوند.
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
        param_number('varianceThreshold', 'آستانه واریانس (%)', default_value=10.0)
    ]
    
    result_schema = schema(
        col('ItemID', 'شناسه قلم', 'string'),
        col('Quantity', 'تعداد', 'integer'),
        col('FIFOValue', 'ارزش FIFO', 'money'),
        col('LIFOValue', 'ارزش LIFO', 'money'),
        col('AverageCostValue', 'ارزش میانگین', 'money'),
        col('CurrentMarketValue', 'ارزش بازار', 'money'),
        col('MaxVariance', 'حداکثر واریانس', 'percent'),
        col('ValuationMethod', 'روش ارزیابی', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون ارزیابی موجودی"""
    
    variance_threshold = get_parameter('varianceThreshold', 10.0)
    
    # دریافت داده‌ها
    query = session.query(InventoryIssues)
    results = query.all()
    
    # گروه‌بندی بر اساس قلم
    item_transactions = defaultdict(list)
    
    for t in results:
        if t.ItemCode and t.UnitPrice and t.Quantity:
            if t.IssueDate:
                item_transactions[t.ItemCode].append({
                    'date': t.IssueDate,
                    'price': float(t.UnitPrice),
                    'quantity': float(t.Quantity)
                })
    
    # محاسبه ارزش به روش‌های مختلف
    data = []
    
    for item_code, transactions in item_transactions.items():
        if len(transactions) < 2:
            continue
        
        # مرتب‌سازی بر اساس تاریخ
        sorted_trans = sorted(transactions, key=lambda x: x['date'])
        
        total_quantity = sum(t['quantity'] for t in sorted_trans)
        
        if total_quantity <= 0:
            continue
        
        # FIFO (اولین ورود، اولین خروج)
        fifo_value = sum(t['price'] * t['quantity'] for t in sorted_trans[:3]) if len(sorted_trans) >= 3 else \
                     sum(t['price'] * t['quantity'] for t in sorted_trans)
        
        # LIFO (آخرین ورود، اولین خروج)
        lifo_value = sum(t['price'] * t['quantity'] for t in sorted_trans[-3:]) if len(sorted_trans) >= 3 else \
                     sum(t['price'] * t['quantity'] for t in sorted_trans)
        
        # میانگین موزون
        total_cost = sum(t['price'] * t['quantity'] for t in sorted_trans)
        avg_cost_value = total_cost
        
        # ارزش بازار (آخرین قیمت)
        current_price = sorted_trans[-1]['price']
        market_value = current_price * total_quantity
        
        # محاسبه حداکثر واریانس
        values = [fifo_value, lifo_value, avg_cost_value, market_value]
        min_val = min(values)
        max_val = max(values)
        max_variance = ((max_val - min_val) / min_val * 100) if min_val > 0 else 0
        
        if max_variance >= variance_threshold:
            row = {
                'ItemID': str(item_code),
                'Quantity': int(total_quantity),
                'FIFOValue': round(fifo_value, 2),
                'LIFOValue': round(lifo_value, 2),
                'AverageCostValue': round(avg_cost_value, 2),
                'CurrentMarketValue': round(market_value, 2),
                'MaxVariance': round(max_variance, 2),
                'ValuationMethod': 'مختلط'
            }
            data.append(row)
    
    # مرتب‌سازی بر اساس واریانس
    data.sort(key=lambda x: x['MaxVariance'], reverse=True)
    
    return data
