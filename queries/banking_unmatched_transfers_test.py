"""
آزمون انتقالات بدون تطبیق
Unmatched Transfers Test

این آزمون انتقالات بانکی که با طرف مقابل تطبیق ندارند را شناسایی می‌کند.
انتقالات بدون تطبیق ممکن است نشانه خطا یا تقلب باشند.
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
        param_number('toleranceAmount', 'مبلغ تلورانس', default_value=10.0)
    ]
    
    result_schema = schema(
        col('TransferID', 'شناسه انتقال', 'string'),
        col('TransferDate', 'تاریخ انتقال', 'date'),
        col('FromAccount', 'از حساب', 'string'),
        col('ToAccount', 'به حساب', 'string'),
        col('Amount', 'مبلغ', 'money'),
        col('MatchStatus', 'وضعیت تطبیق', 'string'),
        col('DaysSinceTransfer', 'روزهای از انتقال', 'integer')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون انتقالات بدون تطبیق"""
    
    tolerance = get_parameter('toleranceAmount', 10.0)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # گروه‌بندی انتقالات
    transfers_out = {}
    transfers_in = {}
    
    for t in results:
        if hasattr(t, 'TransferID') and t.TransferID:
            transfer_id = str(t.TransferID)
            amount = t.Debit if t.Debit else t.Credit if t.Credit else 0
            
            if hasattr(t, 'TransferType'):
                if t.TransferType == 'Outgoing':
                    transfers_out[transfer_id] = {
                        'transaction': t,
                        'amount': amount
                    }
                elif t.TransferType == 'Incoming':
                    transfers_in[transfer_id] = {
                        'transaction': t,
                        'amount': amount
                    }
    
    # یافتن انتقالات بدون تطبیق
    data = []
    from datetime import datetime
    current_date = datetime.now()
    
    # بررسی انتقالات خروجی
    for transfer_id, out_data in transfers_out.items():
        t = out_data['transaction']
        out_amount = out_data['amount']
        
        match_status = 'بدون تطبیق ورودی'
        
        if transfer_id in transfers_in:
            in_amount = transfers_in[transfer_id]['amount']
            difference = abs(out_amount - in_amount)
            
            if difference > tolerance:
                match_status = 'اختلاف مبلغ'
            else:
                continue
        
        days_since = 0
        if hasattr(t, 'TransactionDate') and t.TransactionDate:
            days_since = (current_date - datetime.combine(t.TransactionDate, datetime.min.time())).days
        
        row = {
            'TransferID': transfer_id,
            'TransferDate': t.TransactionDate.strftime('%Y-%m-%d') if hasattr(t, 'TransactionDate') and t.TransactionDate else '',
            'FromAccount': t.FromAccount if hasattr(t, 'FromAccount') else '',
            'ToAccount': t.ToAccount if hasattr(t, 'ToAccount') else '',
            'Amount': round(out_amount, 2),
            'MatchStatus': match_status,
            'DaysSinceTransfer': days_since
        }
        data.append(row)
    
    # مرتب‌سازی بر اساس روزها
    data.sort(key=lambda x: x['DaysSinceTransfer'], reverse=True)
    
    return data
