"""
آزمون الگوی سینوسی موجودی
Cyclical Inventory Pattern Test

این آزمون الگوهای سینوسی در سطح موجودی را شناسایی می‌کند.
نوسانات غیرعادی و الگوهای تکراری در موجودی کالا تشخیص داده می‌شوند.
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
        param_number('volatilityThreshold', 'آستانه نوسان (%)', default_value=40.0)
    ]
    
    result_schema = schema(
        col('ItemID', 'شناسه قلم', 'string'),
        col('Period', 'دوره', 'string'),
        col('BeginningInventory', 'موجودی اول دوره', 'integer'),
        col('Purchases', 'خرید', 'integer'),
        col('Sales', 'فروش', 'integer'),
        col('EndingInventory', 'موجودی آخر دوره', 'integer'),
        col('AvgInventory', 'میانگین موجودی', 'number'),
        col('Volatility', 'نوسان', 'percent')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون الگوی سینوسی موجودی"""
    
    volatility_threshold = get_parameter('volatilityThreshold', 40.0)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # گروه‌بندی بر اساس قلم و دوره
    item_inventory = defaultdict(lambda: defaultdict(lambda: {'purchases': 0, 'sales': 0}))
    
    for t in results:
        if hasattr(t, 'ItemID') and hasattr(t, 'Quantity') and hasattr(t, 'TransactionDate'):
            if t.ItemID and t.Quantity and t.TransactionDate:
                period = t.TransactionDate.strftime('%Y-%m')
                
                if hasattr(t, 'TransactionType'):
                    if t.TransactionType == 'Purchase':
                        item_inventory[t.ItemID][period]['purchases'] += t.Quantity
                    elif t.TransactionType == 'Sale':
                        item_inventory[t.ItemID][period]['sales'] += t.Quantity
    
    # تحلیل نوسانات
    data = []
    for item_id, periods in item_inventory.items():
        sorted_periods = sorted(periods.items())
        
        if len(sorted_periods) < 3:
            continue
        
        inventory_levels = []
        current_inventory = 0
        
        for period, movements in sorted_periods:
            beginning_inventory = current_inventory
            purchases = movements['purchases']
            sales = movements['sales']
            ending_inventory = beginning_inventory + purchases - sales
            
            inventory_levels.append(ending_inventory)
            
            current_inventory = ending_inventory
        
        # محاسبه نوسان
        if len(inventory_levels) > 1:
            avg_inventory = statistics.mean(inventory_levels)
            stdev_inventory = statistics.stdev(inventory_levels)
            volatility = (stdev_inventory / avg_inventory * 100) if avg_inventory > 0 else 0
            
            if volatility >= volatility_threshold:
                for i, (period, movements) in enumerate(sorted_periods):
                    row = {
                        'ItemID': str(item_id),
                        'Period': period,
                        'BeginningInventory': inventory_levels[i-1] if i > 0 else 0,
                        'Purchases': movements['purchases'],
                        'Sales': movements['sales'],
                        'EndingInventory': inventory_levels[i],
                        'AvgInventory': round(avg_inventory, 2),
                        'Volatility': round(volatility, 2)
                    }
                    data.append(row)
    
    # مرتب‌سازی
    data.sort(key=lambda x: x['Volatility'], reverse=True)
    
    return data
