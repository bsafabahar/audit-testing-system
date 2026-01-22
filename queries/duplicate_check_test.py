"""
آزمون چک‌های تکراری
Duplicate Check Detection

شناسایی شماره چک‌های تکراری.
"""
from typing import List, Dict, Any
from models import Transaction
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
    
    check_column = get_parameter('checkNumberColumn', 'DocumentNumber')
    limit = get_parameter('limit', 100)
    
    query = session.query(Transaction)
    results = query.all()
    
    # گروه‌بندی بر اساس شماره چک
    check_groups = defaultdict(list)
    
    for t in results:
        check_num = str(t.DocumentNumber) if t.DocumentNumber else None
        if check_num:
            check_groups[check_num].append(t)
    
    # تحلیل چک‌های تکراری
    data = []
    
    for check_num, transactions in check_groups.items():
        if len(transactions) > 1:  # فقط موارد تکراری
            dates = [t.DocumentDate for t in transactions if t.DocumentDate]
            debits = [t.Debit for t in transactions if t.Debit]
            credits = [t.Credit for t in transactions if t.Credit]
            
            amounts = set()
            for t in transactions:
                if t.Debit:
                    amounts.add(t.Debit)
                if t.Credit:
                    amounts.add(t.Credit)
            
            # تعیین سطح ریسک
            if len(amounts) == 1 and len(dates) > 0:
                date_diff = (max(dates) - min(dates)).days if len(dates) > 1 else 0
                if date_diff < 7:
                    risk_level = 'بالا'
                else:
                    risk_level = 'متوسط'
            else:
                risk_level = 'پایین'
            
            row = {
                'CheckNumber': check_num,
                'OccurrenceCount': len(transactions),
                'FirstDate': min(dates).strftime('%Y-%m-%d') if dates else '',
                'LastDate': max(dates).strftime('%Y-%m-%d') if dates else '',
                'TotalDebit': round(sum(debits), 2) if debits else 0.0,
                'TotalCredit': round(sum(credits), 2) if credits else 0.0,
                'UniqueAmounts': len(amounts),
                'RiskLevel': risk_level
            }
            data.append(row)
    
    # مرتب‌سازی بر اساس تعداد وقوع
    data.sort(key=lambda x: x['OccurrenceCount'], reverse=True)
    
    return data[:limit]
