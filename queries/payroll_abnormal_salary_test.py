"""
آزمون حقوق نجومی
Abnormal Salary Test

این آزمون حقوق‌های غیرعادی و نجومی را شناسایی می‌کند.
حقوق‌هایی که به طور غیرعادی بالا یا پایین هستند، تشخیص داده می‌شوند.
"""
from typing import List, Dict, Any
from models import PayrollTransactions
from parameters import param_number
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
from collections import defaultdict
import statistics


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_number('zScoreThreshold', 'آستانه Z-Score', default_value=3.0)
    ]
    
    result_schema = schema(
        col('EmployeeID', 'شناسه کارمند', 'string'),
        col('Period', 'دوره', 'string'),
        col('SalaryAmount', 'مبلغ حقوق', 'money'),
        col('AvgSalary', 'میانگین حقوق', 'money'),
        col('ZScore', 'Z-Score', 'number'),
        col('Deviation', 'انحراف', 'money'),
        col('DeviationPercent', 'درصد انحراف', 'percent')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون حقوق نجومی"""
    
    z_threshold = get_parameter('zScoreThreshold', 3.0)
    
    # دریافت داده‌ها از جدول PayrollTransactions
    query = session.query(PayrollTransactions)
    results = query.all()
    
    # گروه‌بندی بر اساس کارمند و دوره
    employee_salaries = defaultdict(lambda: defaultdict(float))
    
    for t in results:
        if t.EmployeeCode and t.NetPayment and t.NetPayment > 0:
            # استفاده از Month برای دوره یا VoucherDate
            period = t.Month if t.Month else (t.VoucherDate.strftime('%Y-%m') if t.VoucherDate else 'Unknown')
            employee_salaries[t.EmployeeCode][period] += float(t.NetPayment)
    
    # جمع‌آوری همه حقوق‌ها
    all_salaries = []
    salary_details = []
    
    for emp_id, periods in employee_salaries.items():
        for period, amount in periods.items():
            all_salaries.append(amount)
            salary_details.append({
                'employee': emp_id,
                'period': period,
                'amount': amount
            })
    
    if len(all_salaries) < 2:
        return []
    
    # محاسبه میانگین و انحراف معیار
    avg_salary = statistics.mean(all_salaries)
    stdev_salary = statistics.stdev(all_salaries)
    
    if stdev_salary == 0:
        return []
    
    # یافتن حقوق‌های غیرعادی
    data = []
    
    for sd in salary_details:
        z_score = (sd['amount'] - avg_salary) / stdev_salary
        
        if abs(z_score) >= z_threshold:
            deviation = sd['amount'] - avg_salary
            deviation_percent = (deviation / avg_salary * 100) if avg_salary > 0 else 0
            
            row = {
                'EmployeeID': str(sd['employee']),
                'Period': sd['period'],
                'SalaryAmount': round(sd['amount'], 2),
                'AvgSalary': round(avg_salary, 2),
                'ZScore': round(z_score, 4),
                'Deviation': round(deviation, 2),
                'DeviationPercent': round(deviation_percent, 2)
            }
            data.append(row)
    
    # مرتب‌سازی بر اساس Z-Score
    data.sort(key=lambda x: abs(x['ZScore']), reverse=True)
    
    return data
