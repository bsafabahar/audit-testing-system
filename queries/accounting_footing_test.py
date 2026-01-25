"""
آزمون جمع و تطبیق
Footing and Cross-Footing Test

این آزمون صحت محاسبات جمع ستون‌ها و ردیف‌ها را بررسی می‌کند.
برای اعتبارسنجی محاسبات حسابداری و یافتن خطاهای ریاضی استفاده می‌شود.
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_string, param_date
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
from datetime import datetime
from collections import defaultdict


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_date('startDate', 'تاریخ شروع', required=False),
        param_date('endDate', 'تاریخ پایان', required=False),
        param_string('groupBy', 'گروه‌بندی بر اساس', default_value='AccountCode')
    ]
    
    result_schema = schema(
        col('GroupKey', 'کلید گروه', 'string'),
        col('TransactionCount', 'تعداد تراکنش', 'integer'),
        col('TotalDebit', 'جمع بدهکار', 'money'),
        col('TotalCredit', 'جمع بستانکار', 'money'),
        col('Balance', 'مانده', 'money'),
        col('DebitTransactions', 'تعداد بدهکار', 'integer'),
        col('CreditTransactions', 'تعداد بستانکار', 'integer'),
        col('IsBalanced', 'متعادل است', 'string'),
        col('VariancePercent', 'درصد اختلاف', 'percent')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون جمع و تطبیق"""
    
    start_date_str = get_parameter('startDate')
    end_date_str = get_parameter('endDate')
    group_by = get_parameter('groupBy', 'AccountCode')
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    
    # اعمال فیلتر تاریخی
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            query = query.filter(Transaction.DocumentDate >= start_date)
        except:
            pass
    
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(Transaction.DocumentDate <= end_date)
        except:
            pass
    
    results = query.all()
    
    # گروه‌بندی داده‌ها
    groups = defaultdict(lambda: {
        'debit_sum': 0.0,
        'credit_sum': 0.0,
        'debit_count': 0,
        'credit_count': 0,
        'total_count': 0
    })
    
    for t in results:
        # تعیین کلید گروه
        group_key = ''
        if group_by == 'AccountCode':
            group_key = t.AccountCode or 'نامشخص'
        elif group_by == 'DocumentType':
            group_key = t.DocumentType or 'نامشخص'
        elif group_by == 'Date':
            group_key = t.DocumentDate.strftime('%Y-%m') if t.DocumentDate else 'نامشخص'
        else:
            group_key = 'همه'
        
        # محاسبه مبالغ
        debit = float(t.Debit) if t.Debit else 0.0
        credit = float(t.Credit) if t.Credit else 0.0
        
        groups[group_key]['debit_sum'] += debit
        groups[group_key]['credit_sum'] += credit
        groups[group_key]['total_count'] += 1
        
        if debit > 0:
            groups[group_key]['debit_count'] += 1
        if credit > 0:
            groups[group_key]['credit_count'] += 1
    
    # آماده‌سازی خروجی
    data = []
    total_debit = 0.0
    total_credit = 0.0
    
    for group_key, values in groups.items():
        debit_sum = values['debit_sum']
        credit_sum = values['credit_sum']
        balance = debit_sum - credit_sum
        
        # محاسبه اختلاف
        total_sum = debit_sum + credit_sum
        variance_percent = 0.0
        if total_sum > 0:
            variance_percent = (abs(balance) / total_sum) * 100
        
        # بررسی تعادل
        is_balanced = 'بله' if abs(balance) < 0.01 else 'خیر'
        
        row = {
            'GroupKey': group_key,
            'TransactionCount': values['total_count'],
            'TotalDebit': round(debit_sum, 2),
            'TotalCredit': round(credit_sum, 2),
            'Balance': round(balance, 2),
            'DebitTransactions': values['debit_count'],
            'CreditTransactions': values['credit_count'],
            'IsBalanced': is_balanced,
            'VariancePercent': round(variance_percent, 2)
        }
        data.append(row)
        
        total_debit += debit_sum
        total_credit += credit_sum
    
    # افزودن ردیف جمع کل
    total_balance = total_debit - total_credit
    total_transactions = sum(g['total_count'] for g in groups.values())
    
    total_sum = total_debit + total_credit
    total_variance = 0.0
    if total_sum > 0:
        total_variance = (abs(total_balance) / total_sum) * 100
    
    data.append({
        'GroupKey': '*** جمع کل ***',
        'TransactionCount': total_transactions,
        'TotalDebit': round(total_debit, 2),
        'TotalCredit': round(total_credit, 2),
        'Balance': round(total_balance, 2),
        'DebitTransactions': sum(g['debit_count'] for g in groups.values()),
        'CreditTransactions': sum(g['credit_count'] for g in groups.values()),
        'IsBalanced': 'بله' if abs(total_balance) < 0.01 else 'خیر',
        'VariancePercent': round(total_variance, 2)
    })
    
    # مرتب‌سازی بر اساس مبلغ بدهکار
    data_without_total = [d for d in data if d['GroupKey'] != '*** جمع کل ***']
    data_without_total.sort(key=lambda x: x['TotalDebit'], reverse=True)
    
    # افزودن جمع کل به انتها
    total_row = [d for d in data if d['GroupKey'] == '*** جمع کل ***'][0]
    final_data = data_without_total + [total_row]
    
    return final_data
