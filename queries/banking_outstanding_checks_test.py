"""
آزمون چک‌های معلق
Outstanding Checks Test

این آزمون چک‌های صادر شده که هنوز وصول نشده‌اند را شناسایی می‌کند.
چک‌های معلق طولانی‌مدت ممکن است نشانه مشکل باشند.
"""
from typing import List, Dict, Any
from models import CheckPayables
from parameters import param_number
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
from datetime import datetime


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_number('daysOutstanding', 'روزهای معلق', default_value=60)
    ]
    
    result_schema = schema(
        col('CheckNumber', 'شماره چک', 'string'),
        col('IssueDate', 'تاریخ صدور', 'date'),
        col('Amount', 'مبلغ', 'money'),
        col('Payee', 'گیرنده', 'string'),
        col('DaysOutstanding', 'روزهای معلق', 'integer'),
        col('Status', 'وضعیت', 'string'),
        col('AccountNumber', 'شماره حساب', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون چک‌های معلق"""
    
    days_threshold = get_parameter('daysOutstanding', 60)
    
    # دریافت داده‌ها از جدول CheckPayables
    query = session.query(CheckPayables)
    results = query.all()
    
    current_date = datetime.now()
    data = []
    
    for t in results:
        if t.CheckNumber and t.CheckDate:
            # محاسبه روزهای گذشته از تاریخ چک
            days_outstanding = (current_date - t.CheckDate).days
            
            # چک‌هایی که از سررسید گذشته اند
            if days_outstanding >= days_threshold:
                # تعیین وضعیت بر اساس روزهای معلق
                if days_outstanding > 180:
                    status = 'Overdue - Critical'
                elif days_outstanding > 90:
                    status = 'Overdue - High'
                else:
                    status = 'Outstanding'
                
                row = {
                    'CheckNumber': str(t.CheckNumber),
                    'IssueDate': t.DocumentPaymentDate.strftime('%Y-%m-%d') if t.DocumentPaymentDate else '',
                    'Amount': round(float(t.CheckAmount), 2),
                    'Payee': t.PayeeName if t.PayeeName else '',
                    'DaysOutstanding': days_outstanding,
                    'Status': status,
                    'AccountNumber': t.PayeeCode if t.PayeeCode else ''
                }
                data.append(row)
    
    # مرتب‌سازی بر اساس روزهای معلق
    data.sort(key=lambda x: x['DaysOutstanding'], reverse=True)
    
    return data
