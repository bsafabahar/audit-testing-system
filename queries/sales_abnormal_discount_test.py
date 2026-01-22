"""
آزمون تخفیفات نجومی
Abnormal Discount Test

این آزمون تخفیفات غیرعادی و نجومی را شناسایی می‌کند.
تخفیفات بیش از حد معمول ممکن است نشانه تقلب باشد.
"""
from typing import List, Dict, Any
from models import Transaction
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
    query = session.query(Transaction)
    results = query.all()
    
    # جمع‌آوری داده‌های تخفیف
    discounts = []
    transaction_data = []
    
    for t in results:
        if hasattr(t, 'OriginalAmount') and hasattr(t, 'DiscountAmount'):
            if t.OriginalAmount and t.OriginalAmount > 0:
                discount = t.DiscountAmount if t.DiscountAmount else 0
                discount_percent = (discount / t.OriginalAmount) * 100
                
                discounts.append(discount_percent)
                
                transaction_data.append({
                    'transaction': t,
                    'original': t.OriginalAmount,
                    'discount': discount,
                    'discount_percent': discount_percent
                })
    
    if not discounts:
        return []
    
    avg_discount = statistics.mean(discounts)
    
    # یافتن تخفیفات غیرعادی
    data = []
    
    for td in transaction_data:
        if td['discount_percent'] >= discount_threshold:
            t = td['transaction']
            final_amount = td['original'] - td['discount']
            
            row = {
                'TransactionID': str(t.TransactionID) if hasattr(t, 'TransactionID') else '',
                'CustomerID': str(t.CustomerID) if hasattr(t, 'CustomerID') else '',
                'OriginalAmount': round(td['original'], 2),
                'DiscountAmount': round(td['discount'], 2),
                'FinalAmount': round(final_amount, 2),
                'DiscountPercent': round(td['discount_percent'], 2),
                'TransactionDate': t.TransactionDate.strftime('%Y-%m-%d') if hasattr(t, 'TransactionDate') and t.TransactionDate else '',
                'AvgDiscount': round(avg_discount, 2)
            }
            data.append(row)
    
    # مرتب‌سازی بر اساس درصد تخفیف
    data.sort(key=lambda x: x['DiscountPercent'], reverse=True)
    
    return data
