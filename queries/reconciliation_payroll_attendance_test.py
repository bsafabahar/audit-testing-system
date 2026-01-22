"""
آزمون تطابق حقوق و حضور
Payroll Attendance Reconciliation Test

این آزمون تطابق حقوق پرداختی با ساعات حضور کارکنان را بررسی می‌کند.
عدم تطابق بین حقوق و حضور شناسایی می‌شود.
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
        param_number('varianceThreshold', 'آستانه واریانس (%)', default_value=10.0)
    ]
    
    result_schema = schema(
        col('EmployeeID', 'شناسه کارمند', 'string'),
        col('Period', 'دوره', 'string'),
        col('PayrollAmount', 'حقوق پرداختی', 'money'),
        col('ExpectedPayroll', 'حقوق مورد انتظار', 'money'),
        col('AttendanceHours', 'ساعات حضور', 'number'),
        col('ExpectedHours', 'ساعات مورد انتظار', 'number'),
        col('Variance', 'واریانس', 'percent'),
        col('ReconciliationStatus', 'وضعیت تطبیق', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون تطابق حقوق و حضور"""
    
    variance_threshold = get_parameter('varianceThreshold', 10.0)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # گروه‌بندی بر اساس کارمند و دوره
    employee_data = defaultdict(lambda: defaultdict(lambda: {
        'payroll': 0,
        'hours': 0,
        'expected_hours': 160
    }))
    
    for t in results:
        if hasattr(t, 'EmployeeID') and hasattr(t, 'TransactionDate'):
            if t.EmployeeID and t.TransactionDate:
                period = t.TransactionDate.strftime('%Y-%m')
                
                if hasattr(t, 'PayrollAmount') and t.PayrollAmount:
                    employee_data[t.EmployeeID][period]['payroll'] += t.PayrollAmount
                
                if hasattr(t, 'AttendanceHours') and t.AttendanceHours:
                    employee_data[t.EmployeeID][period]['hours'] += t.AttendanceHours
    
    # تحلیل تطابق
    data = []
    for employee_id, periods in employee_data.items():
        for period, emp_data in periods.items():
            payroll = emp_data['payroll']
            hours = emp_data['hours']
            expected_hours = emp_data['expected_hours']
            
            if payroll > 0 and hours > 0:
                hourly_rate = payroll / hours
                expected_payroll = hourly_rate * expected_hours
                variance = ((payroll - expected_payroll) / expected_payroll * 100) if expected_payroll > 0 else 0
                
                status = 'مطابق'
                if abs(variance) > variance_threshold:
                    if variance > 0:
                        status = 'پرداخت بیش از حد'
                    else:
                        status = 'پرداخت کمتر از حد'
                
                if abs(variance) > variance_threshold:
                    row = {
                        'EmployeeID': str(employee_id),
                        'Period': period,
                        'PayrollAmount': round(payroll, 2),
                        'ExpectedPayroll': round(expected_payroll, 2),
                        'AttendanceHours': round(hours, 2),
                        'ExpectedHours': round(expected_hours, 2),
                        'Variance': round(variance, 2),
                        'ReconciliationStatus': status
                    }
                    data.append(row)
    
    # مرتب‌سازی
    data.sort(key=lambda x: abs(x['Variance']), reverse=True)
    
    return data
