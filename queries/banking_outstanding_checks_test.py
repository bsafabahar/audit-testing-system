"""
آزمون چک‌های معلق
Outstanding Checks Test

این آزمون چک‌های صادر شده که هنوز وصول نشده‌اند را شناسایی می‌کند.
چک‌های معلق طولانی‌مدت ممکن است نشانه مشکل باشند.
"""
from typing import List, Dict, Any
from models import Transaction
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
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    current_date = datetime.now()
    data = []
    
    for t in results:
        if hasattr(t, 'CheckNumber') and hasattr(t, 'CheckStatus'):
            if t.CheckNumber and t.CheckStatus in ['Issued', 'Outstanding', 'Pending']:
                issue_date = t.TransactionDate if hasattr(t, 'TransactionDate') and t.TransactionDate else None
                
                if issue_date:
                    days_outstanding = (current_date - datetime.combine(issue_date, datetime.min.time())).days
                    
                    if days_outstanding >= days_threshold:
                        amount = t.Debit if t.Debit else t.Credit if t.Credit else 0
                        
                        row = {
                            'CheckNumber': str(t.CheckNumber),
                            'IssueDate': issue_date.strftime('%Y-%m-%d'),
                            'Amount': round(amount, 2),
                            'Payee': t.Payee if hasattr(t, 'Payee') else '',
                            'DaysOutstanding': days_outstanding,
                            'Status': t.CheckStatus,
                            'AccountNumber': t.AccountNumber if hasattr(t, 'AccountNumber') else ''
                        }
                        data.append(row)
    
    # مرتب‌سازی بر اساس روزهای معلق
    data.sort(key=lambda x: x['DaysOutstanding'], reverse=True)
    
    return data
