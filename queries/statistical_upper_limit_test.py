"""
آزمون حد بالای آماری
Statistical Upper Limit Test

این آزمون تراکنش‌هایی را شناسایی می‌کند که از حد بالای آماری تجاوز می‌کنند.
با قابلیت استفاده از ضرایب میانگین یا انحراف معیار.

مرجع استانداردها:
- ISA 530: Audit Sampling
- ACL Analytics Guide: Statistical Upper Limits
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_string, param_number, param_select
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
import statistics


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    from parameters import option
    
    parameters = [
        param_string('columnName', 'نام ستون برای آزمون', default_value='Debit'),
        param_number('multiplier', 'ضریب (Multiplier)', default_value=1.5),
        param_select('limitMethod', 'روش محاسبه حد',
                    options=[
                        option('mean-based', 'بر اساس میانگین'),
                        option('stdev-based', 'بر اساس انحراف معیار')
                    ],
                    default_value='mean-based'),
        param_number('limit', 'تعداد رکورد', default_value=100)
    ]
    
    result_schema = schema(
        col('Id', 'شناسه', 'integer'),
        col('DocumentDate', 'تاریخ سند', 'date'),
        col('DocumentNumber', 'شماره سند', 'integer'),
        col('AccountCode', 'کد حساب', 'string'),
        col('Amount', 'مبلغ', 'currency'),
        col('Threshold', 'آستانه', 'currency'),
        col('ExcessAmount', 'مبلغ مازاد', 'currency'),
        col('ExcessPercent', 'درصد مازاد', 'percent'),
        col('RiskLevel', 'سطح ریسک', 'string'),
        col('StatisticalSignificance', 'اهمیت آماری', 'string'),
        col('Description', 'شرح', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون حد بالای آماری"""
    
    column_name = get_parameter('columnName', 'Debit')
    multiplier = get_parameter('multiplier', 1.5)
    limit_method = get_parameter('limitMethod', 'mean-based')
    limit = get_parameter('limit', 100)
    
    query = session.query(Transaction)
    results = query.all()
    
    # استخراج مبالغ
    amounts = []
    for t in results:
        if column_name == 'Debit' and t.Debit and t.Debit > 0:
            amounts.append(t.Debit)
        elif column_name == 'Credit' and t.Credit and t.Credit > 0:
            amounts.append(t.Credit)
    
    if not amounts:
        return []
    
    # محاسبه آستانه بر اساس روش انتخابی
    if limit_method == 'mean-based':
        mean = statistics.mean(amounts)
        threshold = mean * multiplier
    else:  # stdev-based
        mean = statistics.mean(amounts)
        stdev = statistics.stdev(amounts) if len(amounts) > 1 else 0
        threshold = mean + (stdev * multiplier)
    
    # یافتن موارد بالاتر از آستانه
    data = []
    for t in results:
        amount = 0
        if column_name == 'Debit' and t.Debit:
            amount = t.Debit
        elif column_name == 'Credit' and t.Credit:
            amount = t.Credit
        
        if amount > threshold:
            excess_amount = amount - threshold
            excess_percent = (excess_amount / threshold) * 100
            
            # تعیین سطح ریسک بر اساس میزان تجاوز
            if excess_percent >= 100:
                risk_level = 'بحرانی'
                significance = 'بسیار بالا'
            elif excess_percent >= 50:
                risk_level = 'بالا'
                significance = 'بالا'
            elif excess_percent >= 25:
                risk_level = 'متوسط'
                significance = 'متوسط'
            else:
                risk_level = 'پایین'
                significance = 'پایین'
            
            row = {
                'Id': t.Id,
                'DocumentDate': t.DocumentDate.strftime('%Y-%m-%d') if t.DocumentDate else '',
                'DocumentNumber': t.DocumentNumber,
                'AccountCode': t.AccountCode,
                'Amount': float(amount),
                'Threshold': round(threshold, 2),
                'ExcessAmount': round(excess_amount, 2),
                'ExcessPercent': round(excess_percent, 2),
                'RiskLevel': risk_level,
                'StatisticalSignificance': significance,
                'Description': t.Description[:50] if t.Description else ''
            }
            data.append(row)
    
    # مرتب‌سازی بر اساس مبلغ مازاد
    data.sort(key=lambda x: x['ExcessAmount'], reverse=True)
    
    return data[:limit]
