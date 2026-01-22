"""
آزمون فروش‌های تکراری
Repeated Sales Pattern Detection

شناسایی فروش‌های مشابه در مدت زمان کوتاه.
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_number
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
from collections import defaultdict
from datetime import timedelta


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_number('daysDifference', 'تفاوت روزها', default_value=7),
        param_number('amountTolerance', 'تلرانس مبلغ (درصد)', default_value=5),
        param_number('limit', 'تعداد رکورد', default_value=100)
    ]
    
    result_schema = schema(
        col('Id1', 'شناسه ۱', 'integer'),
        col('Id2', 'شناسه ۲', 'integer'),
        col('Date1', 'تاریخ ۱', 'date'),
        col('Date2', 'تاریخ ۲', 'date'),
        col('DaysDifference', 'تفاوت روز', 'integer'),
        col('AccountCode', 'کد حساب', 'string'),
        col('Amount1', 'مبلغ ۱', 'currency'),
        col('Amount2', 'مبلغ ۲', 'currency'),
        col('AmountDifference', 'تفاوت مبلغ', 'percent'),
        col('RiskScore', 'امتیاز ریسک', 'number')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون فروش‌های تکراری"""
    
    days_diff = get_parameter('daysDifference', 7)
    amount_tolerance = get_parameter('amountTolerance', 5) / 100
    limit = get_parameter('limit', 100)
    
    query = session.query(Transaction).order_by(Transaction.DocumentDate)
    results = query.all()
    
    # گروه‌بندی بر اساس کد حساب
    account_transactions = defaultdict(list)
    
    for t in results:
        if t.AccountCode and t.DocumentDate and (t.Debit or t.Credit):
            account_transactions[t.AccountCode].append(t)
    
    # یافتن الگوهای تکراری
    data = []
    
    for account, transactions in account_transactions.items():
        for i in range(len(transactions)):
            for j in range(i + 1, len(transactions)):
                t1 = transactions[i]
                t2 = transactions[j]
                
                # محاسبه تفاوت روزها
                date_diff = (t2.DocumentDate - t1.DocumentDate).days
                
                if date_diff > days_diff:
                    break  # چون مرتب شده، دیگر نیازی به ادامه نیست
                
                # محاسبه تفاوت مبلغ
                amount1 = t1.Debit if t1.Debit else t1.Credit
                amount2 = t2.Debit if t2.Debit else t2.Credit
                
                if amount1 and amount2 and amount1 > 0:
                    amount_diff = abs((amount2 - amount1) / amount1)
                    
                    if amount_diff <= amount_tolerance:
                        # محاسبه امتیاز ریسک
                        risk_score = (
                            (1 - date_diff / days_diff) * 50 +
                            (1 - amount_diff / amount_tolerance) * 50
                        )
                        
                        row = {
                            'Id1': t1.Id,
                            'Id2': t2.Id,
                            'Date1': t1.DocumentDate.strftime('%Y-%m-%d'),
                            'Date2': t2.DocumentDate.strftime('%Y-%m-%d'),
                            'DaysDifference': date_diff,
                            'AccountCode': account,
                            'Amount1': float(amount1),
                            'Amount2': float(amount2),
                            'AmountDifference': round(amount_diff * 100, 2),
                            'RiskScore': round(risk_score, 2)
                        }
                        data.append(row)
    
    # مرتب‌سازی بر اساس امتیاز ریسک
    data.sort(key=lambda x: x['RiskScore'], reverse=True)
    
    return data[:limit]
