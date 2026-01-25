"""
آزمون ارقام تکراری در حقوق
Duplicate Payroll Numbers Test

این آزمون ارقام تکراری و مشابه در حقوق کارکنان را شناسایی می‌کند.
حقوق‌های یکسان ممکن است نشانه خطا یا تقلب باشد.
"""
from typing import List, Dict, Any
from models import PayrollTransactions
from parameters import param_number
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
from collections import defaultdict


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_number('minOccurrences', 'حداقل تکرار', default_value=3)
    ]
    
    result_schema = schema(
        col('SalaryAmount', 'مبلغ حقوق', 'money'),
        col('Occurrences', 'تعداد تکرار', 'integer'),
        col('EmployeeIDs', 'شناسه کارمندان', 'string'),
        col('TotalAmount', 'کل مبلغ', 'money'),
        col('FirstDate', 'اولین تاریخ', 'date'),
        col('LastDate', 'آخرین تاریخ', 'date')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون ارقام تکراری حقوق"""
    
    min_occurrences = get_parameter('minOccurrences', 3)
    
    # دریافت داده‌ها از جدول PayrollTransactions
    query = session.query(PayrollTransactions)
    results = query.all()
    
    # گروه‌بندی بر اساس مبلغ حقوق
    salary_data = defaultdict(lambda: {
        'employees': set(),
        'dates': [],
        'count': 0
    })
    
    for t in results:
        if t.NetPayment and t.NetPayment > 0 and t.EmployeeCode:
            # گرد کردن به نزدیکترین 1000 تومان
            rounded_amount = round(float(t.NetPayment) / 1000) * 1000
            
            salary_data[rounded_amount]['employees'].add(str(t.EmployeeCode))
            salary_data[rounded_amount]['count'] += 1
            
            if t.VoucherDate:
                salary_data[rounded_amount]['dates'].append(t.VoucherDate)
    
    # یافتن ارقام تکراری
    data = []
    
    for amount, info in salary_data.items():
        if info['count'] >= min_occurrences:
            dates = sorted(info['dates']) if info['dates'] else []
            first_date = dates[0] if dates else None
            last_date = dates[-1] if dates else None
            
            employee_list = ', '.join(sorted(info['employees'])[:10])
            if len(info['employees']) > 10:
                employee_list += f' ... (+{len(info['employees']) - 10} more)'
            
            row = {
                'SalaryAmount': round(amount, 2),
                'Occurrences': info['count'],
                'EmployeeIDs': employee_list,
                'TotalAmount': round(amount * info['count'], 2),
                'FirstDate': first_date.strftime('%Y-%m-%d') if first_date else '',
                'LastDate': last_date.strftime('%Y-%m-%d') if last_date else ''
            }
            data.append(row)
    
    # مرتب‌سازی بر اساس تعداد تکرار
    data.sort(key=lambda x: x['Occurrences'], reverse=True)
    
    return data
