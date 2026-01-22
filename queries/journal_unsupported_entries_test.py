"""
آزمون ثبت‌های بدون سند
Unsupported Journal Entries Test

این آزمون ثبت‌های دفتر روزنامه که سند پشتیبان ندارند را شناسایی می‌کند.
ثبت‌های بدون سند ممکن است نشانه خطا یا تقلب باشند.
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_number
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_number('minAmount', 'حداقل مبلغ', default_value=500000.0)
    ]
    
    result_schema = schema(
        col('JournalID', 'شناسه ثبت', 'string'),
        col('EntryDate', 'تاریخ ثبت', 'date'),
        col('Amount', 'مبلغ', 'money'),
        col('Account', 'حساب', 'string'),
        col('Description', 'شرح', 'string'),
        col('DocumentStatus', 'وضعیت سند', 'string'),
        col('EnteredBy', 'ثبت‌کننده', 'string'),
        col('DaysSinceEntry', 'روزهای از ثبت', 'integer')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون ثبت‌های بدون سند"""
    
    min_amount = get_parameter('minAmount', 500000.0)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    from datetime import datetime
    current_date = datetime.now()
    
    data = []
    
    for t in results:
        has_document = False
        
        if hasattr(t, 'DocumentNumber') and t.DocumentNumber:
            has_document = True
        elif hasattr(t, 'ReferenceNumber') and t.ReferenceNumber:
            has_document = True
        elif hasattr(t, 'HasDocument') and t.HasDocument:
            has_document = True
        
        if not has_document:
            amount = t.Debit if t.Debit else t.Credit if t.Credit else 0
            
            if amount >= min_amount:
                days_since = 0
                if hasattr(t, 'TransactionDate') and t.TransactionDate:
                    days_since = (current_date - datetime.combine(t.TransactionDate, datetime.min.time())).days
                
                doc_status = 'بدون سند'
                if hasattr(t, 'DocumentStatus'):
                    doc_status = t.DocumentStatus or 'بدون سند'
                
                row = {
                    'JournalID': str(t.TransactionID) if hasattr(t, 'TransactionID') else '',
                    'EntryDate': t.TransactionDate.strftime('%Y-%m-%d') if hasattr(t, 'TransactionDate') and t.TransactionDate else '',
                    'Amount': round(amount, 2),
                    'Account': t.AccountCode if hasattr(t, 'AccountCode') else '',
                    'Description': t.Description if hasattr(t, 'Description') else '',
                    'DocumentStatus': doc_status,
                    'EnteredBy': t.EnteredBy if hasattr(t, 'EnteredBy') else '',
                    'DaysSinceEntry': days_since
                }
                data.append(row)
    
    # مرتب‌سازی بر اساس مبلغ
    data.sort(key=lambda x: x['Amount'], reverse=True)
    
    return data
