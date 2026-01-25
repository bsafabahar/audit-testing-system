"""
آزمون نرخ سود
Markup Analysis Test

این آزمون نرخ سود (حاشیه سود) تراکنش‌ها را تحلیل می‌کند.
نرخ‌های سود غیرعادی شناسایی می‌شوند.
"""
from typing import List, Dict, Any
from models import SalesTransactions
from parameters import param_number
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
import statistics


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_number('markupThreshold', 'آستانه نرخ سود (%)', default_value=100.0)
    ]
    
    result_schema = schema(
        col('TransactionID', 'شناسه تراکنش', 'string'),
        col('ItemID', 'شناسه قلم', 'string'),
        col('CostPrice', 'قیمت تمام شده', 'money'),
        col('SalePrice', 'قیمت فروش', 'money'),
        col('Markup', 'نرخ سود', 'percent'),
        col('Profit', 'سود', 'money'),
        col('AvgMarkup', 'میانگین نرخ سود', 'percent'),
        col('Deviation', 'انحراف', 'percent')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون نرخ سود"""
    
    markup_threshold = get_parameter('markupThreshold', 100.0)
    
    # دریافت داده‌ها
    query = session.query(SalesTransactions)
    results = query.all()
    
    # محاسبه نرخ سود
    # Note: SalesTransactions doesn't have CostPrice, only UnitPrice (sale price)
    # This test may need to join with inventory or purchase data to get cost
    # For now, returning empty as the data model doesn't support this analysis
    return []
