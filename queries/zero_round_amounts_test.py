"""
آزمون اعداد گرد
Round Amounts Test

این آزمون تراکنش‌هایی را شناسایی می‌کند که مبالغ گرد دارند (مانند 1000، 5000، 10000).
اعداد گرد ممکن است نشانه تراکنش‌های دستی یا تخمینی باشند.
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_string, param_number
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_string('columnName', 'نام ستون برای آزمون', default_value='Debit'),
        param_number('minAmount', 'حداقل مبلغ', default_value=1000.0)
    ]
    
    result_schema = schema(
        col('TransactionID', 'شناسه تراکنش', 'string'),
        col('Amount', 'مبلغ', 'money'),
        col('RoundnessLevel', 'سطح گردی', 'string'),
        col('LastDigits', 'ارقام آخر', 'string'),
        col('TransactionDate', 'تاریخ تراکنش', 'date')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def is_round_amount(amount: float) -> tuple:
    """بررسی گرد بودن عدد"""
    amount_int = int(amount)
    
    # بررسی سطوح مختلف گردی
    if amount_int % 100000 == 0:
        return (True, 'خیلی گرد (100000)', str(amount_int)[-6:])
    elif amount_int % 50000 == 0:
        return (True, 'خیلی گرد (50000)', str(amount_int)[-5:])
    elif amount_int % 10000 == 0:
        return (True, 'گرد (10000)', str(amount_int)[-5:])
    elif amount_int % 5000 == 0:
        return (True, 'گرد (5000)', str(amount_int)[-4:])
    elif amount_int % 1000 == 0:
        return (True, 'نسبتا گرد (1000)', str(amount_int)[-4:])
    
    return (False, '', '')


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون اعداد گرد"""
    
    column_name = get_parameter('columnName', 'Debit')
    min_amount = get_parameter('minAmount', 1000.0)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    data = []
    for t in results:
        amount = t.Debit if column_name == 'Debit' else t.Credit
        
        if amount and amount >= min_amount:
            is_round, level, last_digits = is_round_amount(amount)
            
            if is_round:
                row = {
                    'TransactionID': str(t.TransactionID) if hasattr(t, 'TransactionID') else '',
                    'Amount': round(amount, 2),
                    'RoundnessLevel': level,
                    'LastDigits': last_digits,
                    'TransactionDate': t.TransactionDate.strftime('%Y-%m-%d') if hasattr(t, 'TransactionDate') and t.TransactionDate else ''
                }
                data.append(row)
    
    # مرتب‌سازی بر اساس مبلغ
    data.sort(key=lambda x: x['Amount'], reverse=True)
    
    return data
