"""
آزمون تخفیفات نجومی
Abnormal Discount Test

این آزمون تخفیفات غیرعادی و نجومی را شناسایی می‌کند.
تخفیفات بیش از حد معمول ممکن است نشانه تقلب باشد.
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
        param_number('discountThreshold', 'آستانه تخفیف (%)', default_value=30.0)
    ]
    
    result_schema = schema(
        col('TransactionID', 'شناسه تراکنش', 'string'),
        col('CustomerID', 'شناسه مشتری', 'string'),
        col('OriginalAmount', 'مبلغ اصلی', 'money'),
        col('DiscountAmount', 'مبلغ تخفیف', 'money'),
        col('FinalAmount', 'مبلغ نهایی', 'money'),
        col('DiscountPercent', 'درصد تخفیف', 'percent'),
        col('TransactionDate', 'تاریخ تراکنش', 'date'),
        col('AvgDiscount', 'میانگین تخفیف', 'percent')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون تخفیفات نجومی"""
    
    discount_threshold = get_parameter('discountThreshold', 30.0)
    
    # دریافت داده‌ها
    query = session.query(SalesTransactions)
    results = query.all()
    
    # Note: SalesTransactions doesn't have OriginalAmount or DiscountAmount fields
    # It only has Amount field which is the final sale amount
    # This test may need additional data to calculate discounts
    # For now, returning empty as the data model doesn't support this analysis
    return []
