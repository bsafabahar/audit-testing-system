"""
آزمون تراکنش‌های با ارزش بالا
High Value Transaction Test

این آزمون تراکنش‌های با ارزش بالا را بر اساس روش‌های مختلف آستانه شناسایی می‌کند.
از روش‌های ضریب، صدک و انحراف معیار برای تشخیص تراکنش‌های غیرعادی استفاده می‌شود.

مرجع استانداردها:
- ISA 530: Audit Sampling
- AICPA Audit Sampling Guide
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
    parameters = [
        param_string('columnName', 'نام ستون برای آزمون', default_value='Debit'),
        param_select('thresholdMethod', 'روش محاسبه آستانه',
                    options=['multiplier', 'percentile', 'stdev'],
                    default_value='multiplier',
                    labels={'multiplier': 'ضریب میانگین', 'percentile': 'صدک', 'stdev': 'انحراف معیار'}),
        param_number('multiplierValue', 'مقدار ضریب (برای روش ضریب)', default_value=2.0),
        param_select('percentileValue', 'مقدار صدک (برای روش صدک)',
                    options=['95', '90', '85'],
                    default_value='95',
                    labels={'95': 'بالای 95%', '90': 'بالای 90%', '85': 'بالای 85%'}),
        param_select('stdevValue', 'تعداد انحراف معیار (برای روش stdev)',
                    options=['2', '3'],
                    default_value='2',
                    labels={'2': '2 سیگما (95%)', '3': '3 سیگما (99.7%)'}),
        param_number('materialityThreshold', 'آستانه اهمیت (تومان)', default_value=1000000.0),
        param_number('limit', 'تعداد رکورد', default_value=100)
    ]
    
    result_schema = schema(
        col('Id', 'شناسه', 'integer'),
        col('DocumentDate', 'تاریخ سند', 'date'),
        col('DocumentNumber', 'شماره سند', 'integer'),
        col('AccountCode', 'کد حساب', 'string'),
        col('Amount', 'مبلغ', 'currency'),
        col('Threshold', 'آستانه', 'currency'),
        col('ExcessFactor', 'ضریب مازاد', 'decimal'),
        col('RiskLevel', 'سطح ریسک', 'string'),
        col('MaterialityLevel', 'سطح اهمیت', 'string'),
        col('Description', 'شرح', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون تراکنش‌های با ارزش بالا"""
    
    column_name = get_parameter('columnName', 'Debit')
    threshold_method = get_parameter('thresholdMethod', 'multiplier')
    multiplier_value = get_parameter('multiplierValue', 2.0)
    percentile_value = int(get_parameter('percentileValue', '95'))
    stdev_value = int(get_parameter('stdevValue', '2'))
    materiality_threshold = get_parameter('materialityThreshold', 1000000.0)
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
    threshold = 0
    if threshold_method == 'multiplier':
        mean = statistics.mean(amounts)
        threshold = mean * multiplier_value
    elif threshold_method == 'percentile':
        amounts_sorted = sorted(amounts)
        # استفاده از روش ساده برای محاسبه صدک
        index = int(len(amounts_sorted) * (percentile_value / 100.0))
        threshold = amounts_sorted[min(index, len(amounts_sorted) - 1)]
    elif threshold_method == 'stdev':
        mean = statistics.mean(amounts)
        stdev = statistics.stdev(amounts) if len(amounts) > 1 else 0
        threshold = mean + (stdev * stdev_value)
    
    # یافتن تراکنش‌های بالاتر از آستانه
    data = []
    for t in results:
        amount = 0
        if column_name == 'Debit' and t.Debit:
            amount = t.Debit
        elif column_name == 'Credit' and t.Credit:
            amount = t.Credit
        
        if amount > threshold:
            excess_factor = amount / threshold
            
            # تعیین سطح ریسک بر اساس ضریب مازاد
            if excess_factor >= 3:
                risk_level = 'بحرانی'
            elif excess_factor >= 2:
                risk_level = 'بالا'
            elif excess_factor >= 1.5:
                risk_level = 'متوسط'
            else:
                risk_level = 'پایین'
            
            # تعیین سطح اهمیت
            if amount >= materiality_threshold * 2:
                materiality_level = 'بسیار بااهمیت'
            elif amount >= materiality_threshold:
                materiality_level = 'بااهمیت'
            else:
                materiality_level = 'معمولی'
            
            row = {
                'Id': t.Id,
                'DocumentDate': t.DocumentDate.strftime('%Y-%m-%d') if t.DocumentDate else '',
                'DocumentNumber': t.DocumentNumber,
                'AccountCode': t.AccountCode,
                'Amount': float(amount),
                'Threshold': round(threshold, 2),
                'ExcessFactor': round(excess_factor, 2),
                'RiskLevel': risk_level,
                'MaterialityLevel': materiality_level,
                'Description': t.Description[:50] if t.Description else ''
            }
            data.append(row)
    
    # مرتب‌سازی بر اساس مبلغ
    data.sort(key=lambda x: x['Amount'], reverse=True)
    
    return data[:limit]
