"""
آزمون تطابق گزارش مشتری
Customer Confirmation Reconciliation Test

این آزمون تطابق مانده حساب مشتریان با گزارشات تایید شده را بررسی می‌کند.
اختلافات بین دفاتر و تاییدیه مشتریان شناسایی می‌شوند.
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
        param_number('differenceThreshold', 'آستانه اختلاف', default_value=1000.0)
    ]
    
    result_schema = schema(
        col('CustomerID', 'شناسه مشتری', 'string'),
        col('BookBalance', 'مانده دفتری', 'money'),
        col('ConfirmedBalance', 'مانده تایید شده', 'money'),
        col('Difference', 'اختلاف', 'money'),
        col('DifferencePercent', 'درصد اختلاف', 'percent'),
        col('LastTransactionDate', 'آخرین تراکنش', 'date'),
        col('ReconciliationStatus', 'وضعیت تطبیق', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون تطابق گزارش مشتری"""
    
    diff_threshold = get_parameter('differenceThreshold', 1000.0)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # محاسبه مانده مشتریان
    customer_balances = defaultdict(lambda: {
        'book_balance': 0,
        'confirmed_balance': 0,
        'last_date': None
    })
    
    for t in results:
        if hasattr(t, 'CustomerID') and t.CustomerID:
            cust_id = t.CustomerID
            
            # مانده دفتری
            if t.Debit:
                customer_balances[cust_id]['book_balance'] += t.Debit
            if t.Credit:
                customer_balances[cust_id]['book_balance'] -= t.Credit
            
            # مانده تایید شده
            if hasattr(t, 'ConfirmedAmount') and t.ConfirmedAmount:
                customer_balances[cust_id]['confirmed_balance'] = t.ConfirmedAmount
            
            # آخرین تاریخ
            if hasattr(t, 'TransactionDate') and t.TransactionDate:
                if customer_balances[cust_id]['last_date'] is None or \
                   t.TransactionDate > customer_balances[cust_id]['last_date']:
                    customer_balances[cust_id]['last_date'] = t.TransactionDate
    
    # یافتن اختلافات
    data = []
    for customer_id, balances in customer_balances.items():
        book_balance = balances['book_balance']
        confirmed_balance = balances['confirmed_balance']
        
        if confirmed_balance != 0:
            difference = abs(book_balance - confirmed_balance)
            diff_percent = (difference / abs(confirmed_balance) * 100) if confirmed_balance != 0 else 0
            
            if difference >= diff_threshold:
                status = 'عدم تطابق'
                if book_balance > confirmed_balance:
                    status = 'مانده دفتری بیشتر'
                elif book_balance < confirmed_balance:
                    status = 'مانده دفتری کمتر'
                
                row = {
                    'CustomerID': str(customer_id),
                    'BookBalance': round(book_balance, 2),
                    'ConfirmedBalance': round(confirmed_balance, 2),
                    'Difference': round(difference, 2),
                    'DifferencePercent': round(diff_percent, 2),
                    'LastTransactionDate': balances['last_date'].strftime('%Y-%m-%d') if balances['last_date'] else '',
                    'ReconciliationStatus': status
                }
                data.append(row)
    
    # مرتب‌سازی بر اساس اختلاف
    data.sort(key=lambda x: x['Difference'], reverse=True)
    
    return data
