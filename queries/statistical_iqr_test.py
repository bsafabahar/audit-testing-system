"""
آزمون Quartile/IQR
Quartile/IQR Test

این آزمون از روش Interquartile Range (IQR) برای شناسایی داده‌های پرت استفاده می‌کند.
داده‌هایی که خارج از محدوده Q1-1.5*IQR تا Q3+1.5*IQR باشند، به عنوان پرت شناسایی می‌شوند.
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
        param_number('iqrMultiplier', 'ضریب IQR', default_value=1.5)
    ]
    
    result_schema = schema(
        col('TransactionID', 'شناسه تراکنش', 'string'),
        col('Amount', 'مبلغ', 'money'),
        col('Q1', 'چارک اول', 'money'),
        col('Q3', 'چارک سوم', 'money'),
        col('IQR', 'فاصله میان چارکی', 'money'),
        col('LowerBound', 'حد پایین', 'money'),
        col('UpperBound', 'حد بالا', 'money'),
        col('OutlierType', 'نوع پرت', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون IQR"""
    
    column_name = get_parameter('columnName', 'Debit')
    iqr_multiplier = get_parameter('iqrMultiplier', 1.5)
    
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
            if amount not in transaction_map:
                transaction_map[amount] = []
            transaction_map[amount].append(t)
    
    if len(amounts) < 4:
        return []
    
    # محاسبه چارک‌ها
    amounts_sorted = sorted(amounts)
    q1 = float(statistics.quantiles(amounts_sorted, n=4)[0])
    q3 = float(statistics.quantiles(amounts_sorted, n=4)[2])
    iqr = q3 - q1
    
    lower_bound = q1 - (iqr_multiplier * iqr)
    upper_bound = q3 + (iqr_multiplier * iqr)
    
    # یافتن پرت‌ها
    data = []
    for amount in set(amounts):
        amount_float = float(amount)
        if amount_float < lower_bound or amount_float > upper_bound:
            outlier_type = 'پایین‌تر از حد' if amount_float < lower_bound else 'بالاتر از حد'
            
            for t in transaction_map[amount]:
                row = {
                    'TransactionID': str(t.TransactionID) if hasattr(t, 'TransactionID') else '',
                    'Amount': round(amount_float, 2),
                    'Q1': round(q1, 2),
                    'Q3': round(q3, 2),
                    'IQR': round(iqr, 2),
                    'LowerBound': round(lower_bound, 2),
                    'UpperBound': round(upper_bound, 2),
                    'OutlierType': outlier_type
                }
                data.append(row)
    
    # مرتب‌سازی
    data.sort(key=lambda x: x['Amount'], reverse=True)
    
    return data
