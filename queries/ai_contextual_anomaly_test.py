"""
آزمون شناسایی ناهنجاری‌های زمینه‌ای
Contextual Anomaly Detection

این آزمون میانگین و انحراف معیار تراکنش‌ها را برای هر کد حساب به تفکیک محاسبه می‌کند.
تراکنش‌هایی که بیش از 3 برابر انحراف معیار از میانگین همان حساب فاصله دارند را شناسایی می‌کند.
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_number, param_string
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
from collections import defaultdict
from datetime import datetime
import statistics


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_string('columnName', 'نام ستون مبلغ', default_value='Debit'),
        param_number('sigmaThreshold', 'آستانه انحراف معیار', default_value=3.0),
        param_number('minTransactionsPerAccount', 'حداقل تراکنش در حساب', default_value=5)
    ]
    
    result_schema = schema(
        col('TransactionID', 'شناسه تراکنش', 'string'),
        col('DocumentDate', 'تاریخ سند', 'date'),
        col('AccountCode', 'کد حساب', 'string'),
        col('Amount', 'مبلغ', 'currency'),
        col('AccountMean', 'میانگین حساب', 'currency'),
        col('AccountStdDev', 'انحراف معیار حساب', 'currency'),
        col('DeviationFromMean', 'انحراف از میانگین', 'currency'),
        col('SigmaCount', 'تعداد سیگما', 'number'),
        col('TransactionsInAccount', 'تعداد تراکنش حساب', 'integer'),
        col('AnomalyType', 'نوع ناهنجاری', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون شناسایی ناهنجاری‌های زمینه‌ای"""
    
    column_name = get_parameter('columnName', 'Debit')
    sigma_threshold = get_parameter('sigmaThreshold', 3.0)
    min_transactions = int(get_parameter('minTransactionsPerAccount', 5))
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # گروه‌بندی تراکنش‌ها بر اساس کد حساب
    account_transactions = defaultdict(list)
    
    for t in results:
        amount = t.Debit if column_name == 'Debit' else t.Credit
        
        if not amount or amount <= 0:
            continue
        
        if not t.AccountCode:
            continue
        
        # استخراج تاریخ
        trans_date = None
        if hasattr(t, 'TransactionDate') and t.TransactionDate:
            trans_date = t.TransactionDate
        elif hasattr(t, 'DocumentDate') and t.DocumentDate:
            if isinstance(t.DocumentDate, datetime):
                trans_date = t.DocumentDate
            else:
                trans_date = datetime.combine(t.DocumentDate, datetime.min.time())
        
        account_transactions[t.AccountCode].append({
            'transaction': t,
            'amount': amount,
            'date': trans_date
        })
    
    # محاسبه آمار برای هر حساب
    data = []
    
    for account_code, trans_list in account_transactions.items():
        # فیلتر حساب‌هایی که تراکنش کافی ندارند
        if len(trans_list) < min_transactions:
            continue
        
        # استخراج مبالغ
        amounts = [t['amount'] for t in trans_list]
        
        # محاسبه میانگین و انحراف معیار
        mean_amount = statistics.mean(amounts)
        
        if len(amounts) < 2:
            continue
        
        stdev_amount = statistics.stdev(amounts)
        
        if stdev_amount == 0:
            continue
        
        # شناسایی تراکنش‌های ناهنجار
        for trans_info in trans_list:
            amount = trans_info['amount']
            deviation = amount - mean_amount
            sigma_count = abs(deviation) / stdev_amount
            
            # آیا این تراکنش ناهنجاری است؟
            if sigma_count >= sigma_threshold:
                t = trans_info['transaction']
                
                # تعیین نوع ناهنجاری
                if amount > mean_amount:
                    if sigma_count >= 5:
                        anomaly_type = 'بسیار بالا (>5σ)'
                    elif sigma_count >= 4:
                        anomaly_type = 'خیلی بالا (>4σ)'
                    else:
                        anomaly_type = 'بالا (>3σ)'
                else:
                    if sigma_count >= 5:
                        anomaly_type = 'بسیار پایین (>5σ)'
                    elif sigma_count >= 4:
                        anomaly_type = 'خیلی پایین (>4σ)'
                    else:
                        anomaly_type = 'پایین (>3σ)'
                
                row = {
                    'TransactionID': str(t.TransactionID) if hasattr(t, 'TransactionID') and t.TransactionID else str(t.Id),
                    'DocumentDate': trans_info['date'].strftime('%Y-%m-%d') if trans_info['date'] else '',
                    'AccountCode': account_code,
                    'Amount': round(amount, 2),
                    'AccountMean': round(mean_amount, 2),
                    'AccountStdDev': round(stdev_amount, 2),
                    'DeviationFromMean': round(deviation, 2),
                    'SigmaCount': round(sigma_count, 2),
                    'TransactionsInAccount': len(trans_list),
                    'AnomalyType': anomaly_type
                }
                data.append(row)
    
    # مرتب‌سازی بر اساس تعداد سیگما
    data.sort(key=lambda x: x['SigmaCount'], reverse=True)
    
    return data
