"""
آزمون توزیع فروش (پارتو)
Pareto Analysis Test

این آزمون از قانون پارتو (80/20) برای تحلیل توزیع فروش استفاده می‌کند.
مشتریان یا اقلامی که بخش زیادی از فروش را تشکیل می‌دهند، شناسایی می‌شوند.
"""
from typing import List, Dict, Any
from models import SalesTransactions
from parameters import param_string
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
from collections import defaultdict


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_string('analysisType', 'نوع تحلیل (Customer/Item)', default_value='Customer')
    ]
    
    result_schema = schema(
        col('EntityID', 'شناسه', 'string'),
        col('SalesAmount', 'مبلغ فروش', 'money'),
        col('TransactionCount', 'تعداد تراکنش', 'integer'),
        col('PercentOfTotal', 'درصد از کل', 'percent'),
        col('CumulativePercent', 'درصد تجمعی', 'percent'),
        col('Rank', 'رتبه', 'integer'),
        col('ParetoCategory', 'دسته پارتو', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون پارتو"""
    
    analysis_type = get_parameter('analysisType', 'Customer')
    
    # دریافت داده‌ها از جدول SalesTransactions
    query = session.query(SalesTransactions)
    results = query.all()
    
    # گروه‌بندی بر اساس نوع تحلیل
    entity_sales = defaultdict(lambda: {'amount': 0, 'count': 0})
    
    for t in results:
        entity_id = None
        
        if analysis_type == 'Customer':
            entity_id = t.CustomerCode
        elif analysis_type == 'Item':
            entity_id = t.ItemCode
        
        if entity_id:
            # استفاده از Amount که در SalesTransactions موجود است
            amount = float(t.Amount) if t.Amount else 0
            
            entity_sales[entity_id]['amount'] += amount
            entity_sales[entity_id]['count'] += 1
    
    if not entity_sales:
        return []
    
    # محاسبه مجموع کل
    total_sales = sum(s['amount'] for s in entity_sales.values())
    
    # مرتب‌سازی بر اساس مبلغ
    sorted_entities = sorted(
        [(k, v) for k, v in entity_sales.items()],
        key=lambda x: x[1]['amount'],
        reverse=True
    )
    
    # محاسبه درصدها
    data = []
    cumulative = 0
    
    for rank, (entity_id, sales_data) in enumerate(sorted_entities, 1):
        percent_of_total = (sales_data['amount'] / total_sales * 100) if total_sales > 0 else 0
        cumulative += percent_of_total
        
        # تعیین دسته پارتو
        if cumulative <= 80:
            category = 'A (80% فروش)'
        elif cumulative <= 95:
            category = 'B (15% فروش)'
        else:
            category = 'C (5% فروش)'
        
        row = {
            'EntityID': str(entity_id),
            'SalesAmount': round(sales_data['amount'], 2),
            'TransactionCount': sales_data['count'],
            'PercentOfTotal': round(percent_of_total, 2),
            'CumulativePercent': round(cumulative, 2),
            'Rank': rank,
            'ParetoCategory': category
        }
        data.append(row)
    
    return data
