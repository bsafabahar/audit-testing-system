"""
آزمون تحلیل شبکه
Network Analysis Test

این آزمون روابط و الگوهای شبکه‌ای بین موجودیت‌ها را تحلیل می‌کند.
شبکه‌های مشکوک و الگوهای غیرعادی شناسایی می‌شوند.
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
        param_number('minConnections', 'حداقل تعداد اتصال', default_value=5)
    ]
    
    result_schema = schema(
        col('EntityID', 'شناسه موجودیت', 'string'),
        col('EntityType', 'نوع موجودیت', 'string'),
        col('ConnectionCount', 'تعداد اتصال', 'integer'),
        col('TransactionCount', 'تعداد تراکنش', 'integer'),
        col('TotalAmount', 'کل مبلغ', 'money'),
        col('ConnectedEntities', 'موجودیت‌های متصل', 'string'),
        col('NetworkScore', 'امتیاز شبکه', 'integer'),
        col('PatternType', 'نوع الگو', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون تحلیل شبکه"""
    
    min_connections = get_parameter('minConnections', 5)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # ساخت گراف
    connections = defaultdict(lambda: {
        'connected': set(),
        'transactions': 0,
        'amount': 0
    })
    
    for t in results:
        entities = []
        
        if hasattr(t, 'CustomerID') and t.CustomerID:
            entities.append(('Customer', t.CustomerID))
        if hasattr(t, 'VendorID') and t.VendorID:
            entities.append(('Vendor', t.VendorID))
        if hasattr(t, 'EmployeeID') and t.EmployeeID:
            entities.append(('Employee', t.EmployeeID))
        
        amount = t.Debit if t.Debit else t.Credit if t.Credit else 0
        
        # ایجاد اتصالات
        for i, (type1, id1) in enumerate(entities):
            key1 = f"{type1}:{id1}"
            connections[key1]['transactions'] += 1
            connections[key1]['amount'] += amount
            
            for type2, id2 in entities[i+1:]:
                key2 = f"{type2}:{id2}"
                connections[key1]['connected'].add(key2)
                connections[key2]['connected'].add(key1)
    
    # تحلیل شبکه
    data = []
    
    for entity_key, info in connections.items():
        connection_count = len(info['connected'])
        
        if connection_count >= min_connections:
            entity_type, entity_id = entity_key.split(':', 1)
            
            # محاسبه امتیاز شبکه
            network_score = 0
            pattern_type = 'عادی'
            
            # اتصالات زیاد
            if connection_count > 20:
                network_score += 30
                pattern_type = 'مرکز شبکه'
            elif connection_count > 10:
                network_score += 15
                pattern_type = 'فعال'
            
            # تراکنش‌های زیاد
            if info['transactions'] > 100:
                network_score += 20
            
            # مبلغ بالا
            if info['amount'] > 1000000000:
                network_score += 25
            
            # لیست موجودیت‌های متصل
            connected_list = ', '.join(sorted(list(info['connected']))[:5])
            if len(info['connected']) > 5:
                connected_list += f" ... (+{len(info['connected']) - 5} more)"
            
            row = {
                'EntityID': entity_id,
                'EntityType': entity_type,
                'ConnectionCount': connection_count,
                'TransactionCount': info['transactions'],
                'TotalAmount': round(info['amount'], 2),
                'ConnectedEntities': connected_list,
                'NetworkScore': network_score,
                'PatternType': pattern_type
            }
            data.append(row)
    
    # مرتب‌سازی بر اساس امتیاز شبکه
    data.sort(key=lambda x: x['NetworkScore'], reverse=True)
    
    return data
