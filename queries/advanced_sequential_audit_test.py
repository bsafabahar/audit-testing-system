"""
آزمون ترتیب تراکنش
Sequential Audit Test

این آزمون ترتیب و تسلسل تراکنش‌ها را بررسی می‌کند.
شکاف‌ها و ناهماهنگی‌ها در شماره تراکنش‌ها شناسایی می‌شوند.
"""
from typing import List, Dict, Any
from models import Transaction
from schema import col, schema
from types_definitions import QueryDefinition
from database import ReadOnlySession


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = []
    
    result_schema = schema(
        col('SequenceNumber', 'شماره ترتیب', 'integer'),
        col('ExpectedNext', 'شماره مورد انتظار', 'integer'),
        col('ActualNext', 'شماره واقعی', 'integer'),
        col('GapSize', 'اندازه شکاف', 'integer'),
        col('Date', 'تاریخ', 'date'),
        col('GapType', 'نوع شکاف', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون ترتیب تراکنش"""
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # استخراج شماره‌های ترتیب
    sequences = []
    
    for t in results:
        if hasattr(t, 'SequenceNumber') and t.SequenceNumber:
            sequences.append({
                'number': t.SequenceNumber,
                'date': t.TransactionDate if hasattr(t, 'TransactionDate') else None
            })
    
    if len(sequences) < 2:
        return []
    
    # مرتب‌سازی بر اساس شماره
    sequences.sort(key=lambda x: x['number'])
    
    # یافتن شکاف‌ها
    data = []
    
    for i in range(len(sequences) - 1):
        current = sequences[i]['number']
        next_actual = sequences[i + 1]['number']
        next_expected = current + 1
        
        if next_actual != next_expected:
            gap_size = next_actual - current - 1
            
            # تعیین نوع شکاف
            if gap_size == 1:
                gap_type = 'یک شماره گم شده'
            elif gap_size < 5:
                gap_type = 'شکاف کوچک'
            elif gap_size < 10:
                gap_type = 'شکاف متوسط'
            else:
                gap_type = 'شکاف بزرگ'
            
            row = {
                'SequenceNumber': current,
                'ExpectedNext': next_expected,
                'ActualNext': next_actual,
                'GapSize': gap_size,
                'Date': sequences[i]['date'].strftime('%Y-%m-%d') if sequences[i]['date'] else '',
                'GapType': gap_type
            }
            data.append(row)
    
    return data
