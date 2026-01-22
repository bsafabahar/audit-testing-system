"""
آزمون Z-Score
Z-Score Test

این آزمون از Z-Score برای شناسایی اقلام خارج از محدوده استاندارد استفاده می‌کند.
داده‌هایی که Z-Score آن‌ها بیشتر از آستانه تعیین شده باشد، به عنوان ناهنجاری شناسایی می‌شوند.
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_number, param_string
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
import statistics


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_string('columnName', 'نام ستون برای آزمون', default_value='Debit'),
        param_number('zScoreThreshold', 'آستانه Z-Score', default_value=3.0)
    ]
    
    result_schema = schema(
        col('TransactionID', 'شناسه تراکنش', 'string'),
        col('Amount', 'مبلغ', 'money'),
        col('ZScore', 'Z-Score', 'number'),
        col('Mean', 'میانگین', 'money'),
        col('StdDev', 'انحراف معیار', 'money'),
        col('DeviationFromMean', 'انحراف از میانگین', 'money')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون Z-Score"""
    
    column_name = get_parameter('columnName', 'Debit')
    z_threshold = get_parameter('zScoreThreshold', 3.0)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # استخراج مقادیر
    amounts = []
    transaction_map = {}
    
    for t in results:
        amount = t.Debit if column_name == 'Debit' else t.Credit
        if amount and amount > 0:
            amounts.append(amount)
            transaction_map[amount] = t
    
    if len(amounts) < 2:
        return []
    
    # محاسبه میانگین و انحراف معیار
    mean = statistics.mean(amounts)
    stdev = statistics.stdev(amounts)
    
    if stdev == 0:
        return []
    
    # یافتن اقلام با Z-Score بالا
    data = []
    for amount in amounts:
        z_score = (amount - mean) / stdev
        
        if abs(z_score) >= z_threshold:
            t = transaction_map[amount]
            row = {
                'TransactionID': str(t.TransactionID) if hasattr(t, 'TransactionID') else '',
                'Amount': round(amount, 2),
                'ZScore': round(z_score, 4),
                'Mean': round(mean, 2),
                'StdDev': round(stdev, 2),
                'DeviationFromMean': round(amount - mean, 2)
            }
            data.append(row)
    
    # مرتب‌سازی بر اساس Z-Score
    data.sort(key=lambda x: abs(x['ZScore']), reverse=True)
    
    return data
