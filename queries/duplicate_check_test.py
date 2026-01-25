"""
آزمون چک‌های تکراری
Duplicate Check Detection

شناسایی شماره چک‌های تکراری.
"""
from typing import List, Dict, Any
from models import CheckPayables, CheckReceivables
from parameters import param_string, param_number
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
from collections import defaultdict


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_string('checkNumberColumn', 'نام ستون شماره چک', default_value='DocumentNumber'),
        param_number('limit', 'تعداد رکورد', default_value=100)
    ]
    
    result_schema = schema(
        col('CheckNumber', 'شماره چک', 'string'),
        col('OccurrenceCount', 'تعداد وقوع', 'integer'),
        col('FirstDate', 'اولین تاریخ', 'date'),
        col('LastDate', 'آخرین تاریخ', 'date'),
        col('TotalDebit', 'جمع بدهکار', 'currency'),
        col('TotalCredit', 'جمع بستانکار', 'currency'),
        col('UniqueAmounts', 'تعداد مبالغ مختلف', 'integer'),
        col('RiskLevel', 'سطح ریسک', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون چک‌های تکراری"""
    
    check_column = get_parameter('checkNumberColumn', 'CheckNumber')
    limit = get_parameter('limit', 100)
    
    # دریافت داده‌ها از هر دو جدول چک‌های پرداختی و دریافتی
    payables = session.query(CheckPayables).all()
    receivables = session.query(CheckReceivables).all()
    
    # گروه‌بندی بر اساس شماره چک
    check_groups = defaultdict(lambda: {'items': [], 'type': set()})
    
    for t in payables:
        check_num = str(t.CheckNumber) if t.CheckNumber else None
        if check_num:
            check_groups[check_num]['items'].append({
                'date': t.CheckDate,
                'amount': t.CheckAmount,
                'type': 'Payable',
                'party': t.PayeeName
            })
            check_groups[check_num]['type'].add('Payable')
    
    for t in receivables:
        check_num = str(t.CheckNumber) if t.CheckNumber else None
        if check_num:
            check_groups[check_num]['items'].append({
                'date': t.CheckDate,
                'amount': t.CheckAmount,
                'type': 'Receivable',
                'party': t.DrawerName
            })
            check_groups[check_num]['type'].add('Receivable')
    
    # تحلیل چک‌های تکراری
    data = []
    
    for check_num, group_data in check_groups.items():
        items = group_data['items']
        if len(items) > 1:  # فقط موارد تکراری
            dates = [item['date'] for item in items if item['date']]
            amounts = set(float(item['amount']) for item in items if item['amount'])
            
            # محاسبه مجموع مبالغ بر اساس نوع
            total_payable = sum(float(item['amount']) for item in items if item['type'] == 'Payable' and item['amount'])
            total_receivable = sum(float(item['amount']) for item in items if item['type'] == 'Receivable' and item['amount'])
            
            # تعیین سطح ریسک
            # اگر هر دو نوع چک (پرداختی و دریافتی) با یک شماره وجود داشته باشد، ریسک بالاست
            if len(group_data['type']) > 1:
                risk_level = 'بسیار بالا - دو نوع چک'
            elif len(amounts) == 1 and len(dates) > 0:
                date_diff = (max(dates) - min(dates)).days if len(dates) > 1 else 0
                if date_diff < 7:
                    risk_level = 'بالا - تاریخ نزدیک'
                else:
                    risk_level = 'متوسط'
            else:
                risk_level = 'پایین'
            
            row = {
                'CheckNumber': check_num,
                'OccurrenceCount': len(items),
                'FirstDate': min(dates).strftime('%Y-%m-%d') if dates else '',
                'LastDate': max(dates).strftime('%Y-%m-%d') if dates else '',
                'TotalDebit': round(total_payable, 2),
                'TotalCredit': round(total_receivable, 2),
                'UniqueAmounts': len(amounts),
                'RiskLevel': risk_level
            }
            data.append(row)
    
    # مرتب‌سازی بر اساس تعداد وقوع
    data.sort(key=lambda x: x['OccurrenceCount'], reverse=True)
    
    return data[:limit]
