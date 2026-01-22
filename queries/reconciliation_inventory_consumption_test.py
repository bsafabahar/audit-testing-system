"""
آزمون تطابق مصرف موجودی
Inventory Consumption Reconciliation Test

این آزمون تطابق مصرف موجودی با فروش و تولید را بررسی می‌کند.
اختلافات بین موجودی مصرفی و مورد انتظار شناسایی می‌شوند.
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
        param_number('varianceThreshold', 'آستانه واریانس (%)', default_value=5.0)
    ]
    
    result_schema = schema(
        col('ItemID', 'شناسه قلم', 'string'),
        col('Period', 'دوره', 'string'),
        col('BeginningInventory', 'موجودی اول دوره', 'integer'),
        col('Purchases', 'خرید', 'integer'),
        col('Sales', 'فروش', 'integer'),
        col('ExpectedEnding', 'موجودی مورد انتظار', 'integer'),
        col('ActualEnding', 'موجودی واقعی', 'integer'),
        col('Variance', 'واریانس', 'integer'),
        col('VariancePercent', 'درصد واریانس', 'percent')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون تطابق مصرف موجودی"""
    
    variance_threshold = get_parameter('varianceThreshold', 5.0)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # گروه‌بندی بر اساس قلم و دوره
    item_movements = defaultdict(lambda: defaultdict(lambda: {
        'purchases': 0,
        'sales': 0,
        'beginning': 0,
        'ending': 0
    }))
    
    for t in results:
        if hasattr(t, 'ItemID') and hasattr(t, 'Quantity') and hasattr(t, 'TransactionDate'):
            if t.ItemID and t.Quantity and t.TransactionDate:
                period = t.TransactionDate.strftime('%Y-%m')
                
                if hasattr(t, 'TransactionType'):
                    if t.TransactionType == 'Purchase':
                        item_movements[t.ItemID][period]['purchases'] += t.Quantity
                    elif t.TransactionType == 'Sale':
                        item_movements[t.ItemID][period]['sales'] += t.Quantity
                
                if hasattr(t, 'BeginningInventory') and t.BeginningInventory:
                    item_movements[t.ItemID][period]['beginning'] = t.BeginningInventory
                
                if hasattr(t, 'EndingInventory') and t.EndingInventory:
                    item_movements[t.ItemID][period]['ending'] = t.EndingInventory
    
    # تحلیل اختلافات
    data = []
    for item_id, periods in item_movements.items():
        for period, movements in periods.items():
            beginning = movements['beginning']
            purchases = movements['purchases']
            sales = movements['sales']
            actual_ending = movements['ending']
            
            expected_ending = beginning + purchases - sales
            variance = actual_ending - expected_ending
            
            if expected_ending != 0:
                variance_percent = (variance / expected_ending * 100)
            else:
                variance_percent = 0
            
            if abs(variance_percent) >= variance_threshold:
                row = {
                    'ItemID': str(item_id),
                    'Period': period,
                    'BeginningInventory': beginning,
                    'Purchases': purchases,
                    'Sales': sales,
                    'ExpectedEnding': expected_ending,
                    'ActualEnding': actual_ending,
                    'Variance': variance,
                    'VariancePercent': round(variance_percent, 2)
                }
                data.append(row)
    
    # مرتب‌سازی بر اساس واریانس
    data.sort(key=lambda x: abs(x['VariancePercent']), reverse=True)
    
    return data
