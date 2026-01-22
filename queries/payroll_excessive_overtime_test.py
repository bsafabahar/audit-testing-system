"""
آزمون ساعات اضافی بالا
Excessive Overtime Test

این آزمون ساعات اضافی غیرعادی و بالا را شناسایی می‌کند.
کارمندانی که ساعات اضافی بیش از حد دارند، تشخیص داده می‌شوند.
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_number
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
from collections import defaultdict


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_number('maxOvertimeHours', 'حداکثر ساعات اضافی مجاز', default_value=40.0)
    ]
    
    result_schema = schema(
        col('EmployeeID', 'شناسه کارمند', 'string'),
        col('Period', 'دوره', 'string'),
        col('RegularHours', 'ساعات عادی', 'number'),
        col('OvertimeHours', 'ساعات اضافی', 'number'),
        col('TotalHours', 'کل ساعات', 'number'),
        col('OvertimePercent', 'درصد اضافه‌کاری', 'percent'),
        col('OvertimePay', 'پرداخت اضافه‌کاری', 'money'),
        col('ExcessHours', 'ساعات اضافی بیش از حد', 'number')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون ساعات اضافی بالا"""
    
    max_overtime = get_parameter('maxOvertimeHours', 40.0)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # گروه‌بندی بر اساس کارمند و دوره
    employee_hours = defaultdict(lambda: defaultdict(lambda: {
        'regular': 0,
        'overtime': 0,
        'overtime_pay': 0
    }))
    
    for t in results:
        if hasattr(t, 'EmployeeID'):
            if t.EmployeeID:
                period = t.TransactionDate.strftime('%Y-%m') if hasattr(t, 'TransactionDate') and t.TransactionDate else 'Unknown'
                
                if hasattr(t, 'RegularHours') and t.RegularHours:
                    employee_hours[t.EmployeeID][period]['regular'] += t.RegularHours
                
                if hasattr(t, 'OvertimeHours') and t.OvertimeHours:
                    employee_hours[t.EmployeeID][period]['overtime'] += t.OvertimeHours
                
                if hasattr(t, 'OvertimePay') and t.OvertimePay:
                    employee_hours[t.EmployeeID][period]['overtime_pay'] += t.OvertimePay
    
    # یافتن ساعات اضافی بالا
    data = []
    
    for emp_id, periods in employee_hours.items():
        for period, hours in periods.items():
            overtime = hours['overtime']
            
            if overtime > max_overtime:
                regular = hours['regular']
                total = regular + overtime
                overtime_percent = (overtime / total * 100) if total > 0 else 0
                excess = overtime - max_overtime
                
                row = {
                    'EmployeeID': str(emp_id),
                    'Period': period,
                    'RegularHours': round(regular, 2),
                    'OvertimeHours': round(overtime, 2),
                    'TotalHours': round(total, 2),
                    'OvertimePercent': round(overtime_percent, 2),
                    'OvertimePay': round(hours['overtime_pay'], 2),
                    'ExcessHours': round(excess, 2)
                }
                data.append(row)
    
    # مرتب‌سازی بر اساس ساعات اضافی
    data.sort(key=lambda x: x['OvertimeHours'], reverse=True)
    
    return data
