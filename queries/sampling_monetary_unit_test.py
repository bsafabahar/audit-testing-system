"""
آزمون نمونه‌گیری واحد پولی
Monetary Unit Sampling (MUS) Test

این آزمون با استفاده از روش PPS (Probability Proportional to Size) نمونه‌گیری می‌کند.
اقلام با ارزش بالاتر احتمال بیشتری برای انتخاب دارند.
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
        param_string('columnName', 'نام ستون برای نمونه‌گیری', default_value='Debit'),
        param_number('sampleSize', 'تعداد نمونه مورد نیاز', default_value=50),
        param_number('materialityAmount', 'سطح اهمیت (ریال)', default_value=100000)
    ]
    
    result_schema = schema(
        col('TransactionId', 'شناسه تراکنش', 'integer'),
        col('Date', 'تاریخ', 'date'),
        col('AccountCode', 'کد حساب', 'string'),
        col('Description', 'شرح', 'string'),
        col('Amount', 'مبلغ', 'money'),
        col('CumulativeAmount', 'مبلغ تجمعی', 'money'),
        col('SelectionProbability', 'احتمال انتخاب', 'percent'),
        col('SamplingInterval', 'فاصله نمونه‌گیری', 'money')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون نمونه‌گیری واحد پولی"""
    
    column_name = get_parameter('columnName', 'Debit')
    sample_size = get_parameter('sampleSize', 50)
    materiality = get_parameter('materialityAmount', 100000)
    
    # دریافت داده‌ها
    query = session.query(Transaction).order_by(Transaction.Id)
    results = query.all()
    
    # استخراج مبالغ و محاسبه مجموع
    transactions = []
    total_amount = 0
    
    for t in results:
        amount = 0
        if column_name == 'Debit' and t.Debit:
            amount = float(t.Debit)
        elif column_name == 'Credit' and t.Credit:
            amount = float(t.Credit)
        
        if amount <= 0:
            continue
        
        amount_float = float(amount)
        total_amount += amount_float
        transactions.append({
            'transaction': t,
            'amount': amount,
            'cumulative': total_amount
        })
    
    if not transactions or total_amount == 0:
        return []
    
    # محاسبه فاصله نمونه‌گیری
    sampling_interval = total_amount / sample_size
    
    # انتخاب نقاط شروع تصادفی
    random.seed(42)
    start_point = random.uniform(0, sampling_interval)
    
    # نمونه‌گیری سیستماتیک
    selected_samples = []
    current_point = start_point
    
    while current_point <= total_amount:
        # یافتن تراکنشی که شامل این نقطه است
        for item in transactions:
            if item['cumulative'] >= current_point:
                # محاسبه احتمال انتخاب
                probability = (item['amount'] / total_amount) * 100
                
                selected_samples.append({
                    'item': item,
                    'probability': probability,
                    'sampling_point': current_point
                })
                break
        
        current_point += sampling_interval
    
    # حذف تکراری‌ها (همان تراکنش ممکن است چند بار انتخاب شود)
    unique_samples = {}
    for sample in selected_samples:
        trans_id = sample['item']['transaction'].Id
        if trans_id not in unique_samples:
            unique_samples[trans_id] = sample
    
    # آماده‌سازی خروجی
    data = []
    for trans_id, sample in unique_samples.items():
        item = sample['item']
        t = item['transaction']
        
        row = {
            'TransactionId': t.Id,
            'Date': t.DocumentDate.strftime('%Y-%m-%d') if t.DocumentDate else '',
            'AccountCode': t.AccountCode or '',
            'Description': t.Description or '',
            'Amount': item['amount'],
            'CumulativeAmount': item['cumulative'],
            'SelectionProbability': round(sample['probability'], 4),
            'SamplingInterval': round(sampling_interval, 2)
        }
        data.append(row)
    
    # مرتب‌سازی بر اساس مبلغ تجمعی
    data.sort(key=lambda x: x['CumulativeAmount'])
    
    return data
