"""
آزمون نمونه‌گیری طبقه‌بندی شده
Stratified Sampling Test

این آزمون داده‌ها را به طبقات مختلف تقسیم کرده و از هر طبقه نمونه می‌گیرد.
برای حسابرسی موثر حساب‌های دریافتنی، موجودی و سایر حساب‌ها استفاده می‌شود.
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_string, param_number
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
import random


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_string('columnName', 'نام ستون برای طبقه‌بندی', default_value='Debit'),
        param_number('smallPercent', 'درصد نمونه از طبقه کوچک', default_value=5),
        param_number('mediumPercent', 'درصد نمونه از طبقه متوسط', default_value=10),
        param_number('largePercent', 'درصد نمونه از طبقه بزرگ', default_value=20),
        param_number('smallThreshold', 'حد بالای طبقه کوچک', default_value=1000),
        param_number('mediumThreshold', 'حد بالای طبقه متوسط', default_value=10000)
    ]
    
    result_schema = schema(
        col('TransactionId', 'شناسه تراکنش', 'integer'),
        col('Date', 'تاریخ', 'date'),
        col('AccountCode', 'کد حساب', 'string'),
        col('Description', 'شرح', 'string'),
        col('Amount', 'مبلغ', 'money'),
        col('Stratum', 'طبقه', 'string'),
        col('SamplingProbability', 'احتمال انتخاب', 'percent')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون نمونه‌گیری طبقه‌بندی شده"""
    
    column_name = get_parameter('columnName', 'Debit')
    small_pct = get_parameter('smallPercent', 5) / 100
    medium_pct = get_parameter('mediumPercent', 10) / 100
    large_pct = get_parameter('largePercent', 20) / 100
    small_threshold = get_parameter('smallThreshold', 1000)
    medium_threshold = get_parameter('mediumThreshold', 10000)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # طبقه‌بندی داده‌ها
    small_stratum = []
    medium_stratum = []
    large_stratum = []
    
    for t in results:
        amount = 0
        if column_name == 'Debit' and t.Debit:
            amount = float(t.Debit)
        elif column_name == 'Credit' and t.Credit:
            amount = float(t.Credit)
        
        if amount <= 0:
            continue
            
        transaction_data = {
            'transaction': t,
            'amount': amount
        }
        
        if amount <= small_threshold:
            small_stratum.append(transaction_data)
        elif amount <= medium_threshold:
            medium_stratum.append(transaction_data)
        else:
            large_stratum.append(transaction_data)
    
    # نمونه‌گیری از هر طبقه
    small_sample_size = max(1, int(len(small_stratum) * small_pct))
    medium_sample_size = max(1, int(len(medium_stratum) * medium_pct))
    large_sample_size = max(1, int(len(large_stratum) * large_pct))
    
    # انتخاب تصادفی
    random.seed(42)  # برای تکرارپذیری
    
    small_sample = random.sample(small_stratum, min(small_sample_size, len(small_stratum)))
    medium_sample = random.sample(medium_stratum, min(medium_sample_size, len(medium_stratum)))
    large_sample = random.sample(large_stratum, min(large_sample_size, len(large_stratum)))
    
    # ترکیب نمونه‌ها
    data = []
    
    for item in small_sample:
        t = item['transaction']
        row = {
            'TransactionId': t.Id,
            'Date': t.DocumentDate.strftime('%Y-%m-%d') if t.DocumentDate else '',
            'AccountCode': t.AccountCode or '',
            'Description': t.Description or '',
            'Amount': item['amount'],
            'Stratum': 'کوچک',
            'SamplingProbability': round(small_pct * 100, 2)
        }
        data.append(row)
    
    for item in medium_sample:
        t = item['transaction']
        row = {
            'TransactionId': t.Id,
            'Date': t.DocumentDate.strftime('%Y-%m-%d') if t.DocumentDate else '',
            'AccountCode': t.AccountCode or '',
            'Description': t.Description or '',
            'Amount': item['amount'],
            'Stratum': 'متوسط',
            'SamplingProbability': round(medium_pct * 100, 2)
        }
        data.append(row)
    
    for item in large_sample:
        t = item['transaction']
        row = {
            'TransactionId': t.Id,
            'Date': t.DocumentDate.strftime('%Y-%m-%d') if t.DocumentDate else '',
            'AccountCode': t.AccountCode or '',
            'Description': t.Description or '',
            'Amount': item['amount'],
            'Stratum': 'بزرگ',
            'SamplingProbability': round(large_pct * 100, 2)
        }
        data.append(row)
    
    # مرتب‌سازی بر اساس مبلغ
    data.sort(key=lambda x: x['Amount'], reverse=True)
    
    return data
