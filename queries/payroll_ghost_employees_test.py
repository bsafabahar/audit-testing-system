"""
آزمون کارکنان جدید و منصرف‌شده
Ghost Employees Test

این آزمون کارکنانی را شناسایی می‌کند که به تازگی استخدام و سریعا منصرف شده‌اند.
این الگو ممکن است نشانه کارکنان ارواح (ghost employees) باشد.
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_number
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
from collections import defaultdict
from datetime import datetime


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_number('maxEmploymentDays', 'حداکثر روزهای استخدام', default_value=90)
    ]
    
    result_schema = schema(
        col('EmployeeID', 'شناسه کارمند', 'string'),
        col('FirstPaymentDate', 'اولین پرداخت', 'date'),
        col('LastPaymentDate', 'آخرین پرداخت', 'date'),
        col('EmploymentDays', 'روزهای استخدام', 'integer'),
        col('TotalPayments', 'تعداد پرداخت', 'integer'),
        col('TotalAmount', 'کل مبلغ پرداختی', 'money'),
        col('AvgPayment', 'میانگین پرداخت', 'money'),
        col('SuspicionLevel', 'سطح مشکوک بودن', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون کارکنان جدید و منصرف‌شده"""
    
    max_days = get_parameter('maxEmploymentDays', 90)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # گروه‌بندی بر اساس کارمند
    employee_payments = defaultdict(lambda: {
        'dates': [],
        'amounts': []
    })
    
    for t in results:
        if hasattr(t, 'EmployeeID') and hasattr(t, 'PayrollAmount'):
            if t.EmployeeID and t.PayrollAmount and t.PayrollAmount > 0:
                if hasattr(t, 'TransactionDate') and t.TransactionDate:
                    employee_payments[t.EmployeeID]['dates'].append(t.TransactionDate)
                    employee_payments[t.EmployeeID]['amounts'].append(t.PayrollAmount)
    
    # تحلیل کارکنان
    data = []
    
    for emp_id, payments in employee_payments.items():
        if payments['dates']:
            dates = sorted(payments['dates'])
            first_date = dates[0]
            last_date = dates[-1]
            
            employment_days = (last_date - first_date).days
            
            if employment_days <= max_days:
                total_payments = len(payments['amounts'])
                total_amount = sum(payments['amounts'])
                avg_payment = total_amount / total_payments if total_payments > 0 else 0
                
                # تعیین سطح مشکوک بودن
                if employment_days < 30 and total_amount > 10000000:
                    suspicion = 'بسیار مشکوک'
                elif employment_days < 60:
                    suspicion = 'مشکوک'
                else:
                    suspicion = 'نیاز به بررسی'
                
                row = {
                    'EmployeeID': str(emp_id),
                    'FirstPaymentDate': first_date.strftime('%Y-%m-%d'),
                    'LastPaymentDate': last_date.strftime('%Y-%m-%d'),
                    'EmploymentDays': employment_days,
                    'TotalPayments': total_payments,
                    'TotalAmount': round(total_amount, 2),
                    'AvgPayment': round(avg_payment, 2),
                    'SuspicionLevel': suspicion
                }
                data.append(row)
    
    # مرتب‌سازی بر اساس روزهای استخدام
    data.sort(key=lambda x: x['EmploymentDays'])
    
    return data
