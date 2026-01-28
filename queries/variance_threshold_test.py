"""
آزمون تحلیل آستانه واریانس
Variance Threshold Analysis Test

این آزمون تراکنش‌هایی را شناسایی می‌کند که از آستانه واریانس تعیین شده انحراف دارند.
با استفاده از محاسبات آماری پیشرفته شامل Z-Score.

مرجع استانداردها:
- ISA 520: Analytical Procedures
- AICPA AU-C Section 520: Analytical Procedures
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_string, param_number, param_select
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
import statistics
import math


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    from parameters import option
    
    parameters = [
        param_string('columnName', 'نام ستون برای آزمون', default_value='Debit'),
        param_number('varianceThreshold', 'آستانه واریانس (درصد)', default_value=50.0),
        param_select('deviationType', 'نوع انحراف', 
                    options=[
                        option('both', 'دوطرفه'),
                        option('above', 'فقط بالاتر'),
                        option('below', 'فقط پایین‌تر')
                    ], 
                    default_value='both'),
        param_number('limit', 'تعداد رکورد', default_value=100)
    ]
    
    result_schema = schema(
        col('Id', 'شناسه', 'integer'),
        col('DocumentDate', 'تاریخ سند', 'date'),
        col('DocumentNumber', 'شماره سند', 'integer'),
        col('AccountCode', 'کد حساب', 'string'),
        col('Amount', 'مبلغ', 'currency'),
        col('Mean', 'میانگین', 'currency'),
        col('StdDev', 'انحراف معیار', 'currency'),
        col('ZScore', 'امتیاز Z', 'decimal'),
        col('DeviationPercent', 'درصد انحراف', 'percent'),
        col('Threshold', 'آستانه', 'currency'),
        col('ExcessAmount', 'مبلغ مازاد', 'currency'),
        col('RiskLevel', 'سطح ریسک', 'string'),
        col('Description', 'شرح', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون تحلیل آستانه واریانس"""
    
    column_name = get_parameter('columnName', 'Debit')
    variance_threshold = get_parameter('varianceThreshold', 50.0)
    deviation_type = get_parameter('deviationType', 'both')
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
    
    if not amounts or len(amounts) < 2:
        return []
    
    # محاسبه آمار
    mean = float(statistics.mean(amounts))
    stdev = float(statistics.stdev(amounts)) if len(amounts) > 1 else 0
    
    # محاسبه آستانه‌ها بر اساس واریانس
    threshold_factor = 1 + (variance_threshold / 100)
    threshold_upper = mean * threshold_factor
    threshold_lower = mean / threshold_factor
    
    # یافتن موارد غیرعادی
    data = []
    for t in results:
        amount = 0
        if column_name == 'Debit' and t.Debit:
            amount = t.Debit
        elif column_name == 'Credit' and t.Credit:
            amount = t.Credit
        
        if amount <= 0:
            continue
        
        # محاسبه Z-Score
        z_score = (float(amount) - mean) / stdev if stdev > 0 else 0
        
        # بررسی شرایط انحراف
        is_anomaly = False
        if deviation_type == 'both':
            is_anomaly = float(amount) > threshold_upper or float(amount) < threshold_lower
        elif deviation_type == 'above':
            is_anomaly = float(amount) > threshold_upper
        elif deviation_type == 'below':
            is_anomaly = float(amount) < threshold_lower
        
        if is_anomaly:
            deviation_percent = ((float(amount) - mean) / mean) * 100
            
            # محاسبه مبلغ مازاد
            if float(amount) > mean:
                excess_amount = float(amount) - threshold_upper
                threshold = threshold_upper
            else:
                excess_amount = threshold_lower - float(amount)
                threshold = threshold_lower
            
            # تعیین سطح ریسک بر اساس Z-Score
            if abs(z_score) >= 3:
                risk_level = 'بحرانی'
            elif abs(z_score) >= 2:
                risk_level = 'بالا'
            elif abs(z_score) >= 1.5:
                risk_level = 'متوسط'
            else:
                risk_level = 'پایین'
            
            row = {
                'Id': t.Id,
                'DocumentDate': t.DocumentDate.strftime('%Y-%m-%d') if t.DocumentDate else '',
                'DocumentNumber': t.DocumentNumber,
                'AccountCode': t.AccountCode,
                'Amount': float(amount),
                'Mean': round(mean, 2),
                'StdDev': round(stdev, 2),
                'ZScore': round(z_score, 2),
                'DeviationPercent': round(deviation_percent, 2),
                'Threshold': round(threshold, 2),
                'ExcessAmount': round(abs(excess_amount), 2),
                'RiskLevel': risk_level,
                'Description': t.Description[:50] if t.Description else ''
            }
            data.append(row)
    
    # مرتب‌سازی بر اساس Z-Score
    data.sort(key=lambda x: abs(x['ZScore']), reverse=True)
    
    return data[:limit]
