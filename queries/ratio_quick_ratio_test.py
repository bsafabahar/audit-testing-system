"""
آزمون نسبت آنی
Quick Ratio Test

این آزمون نسبت آنی (نقدینگی سریع) را محاسبه و تحلیل می‌کند.
نسبت‌های پایین نشان‌دهنده مشکل نقدینگی هستند.
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
        param_number('minQuickRatio', 'حداقل نسبت آنی', default_value=1.0)
    ]
    
    result_schema = schema(
        col('Period', 'دوره', 'string'),
        col('Cash', 'نقد', 'money'),
        col('AccountsReceivable', 'حساب‌های دریافتنی', 'money'),
        col('MarketableSecurities', 'اوراق بهادار', 'money'),
        col('CurrentLiabilities', 'بدهی‌های جاری', 'money'),
        col('QuickRatio', 'نسبت آنی', 'number'),
        col('LiquidityStatus', 'وضعیت نقدینگی', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون نسبت آنی"""
    
    min_ratio = get_parameter('minQuickRatio', 1.0)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # گروه‌بندی بر اساس دوره
    period_data = defaultdict(lambda: {
        'cash': 0,
        'receivables': 0,
        'securities': 0,
        'liabilities': 0
    })
    
    for t in results:
        if hasattr(t, 'TransactionDate') and t.TransactionDate:
            period = t.TransactionDate.strftime('%Y-%m')
            
            if hasattr(t, 'AccountType'):
                account_type = t.AccountType
                amount = t.Debit if t.Debit else t.Credit if t.Credit else 0
                
                if account_type == 'Cash':
                    period_data[period]['cash'] += amount
                elif account_type == 'AccountsReceivable':
                    period_data[period]['receivables'] += amount
                elif account_type == 'MarketableSecurities':
                    period_data[period]['securities'] += amount
                elif account_type == 'CurrentLiability':
                    period_data[period]['liabilities'] += amount
    
    # محاسبه نسبت آنی
    data = []
    
    for period, balances in period_data.items():
        if balances['liabilities'] > 0:
            quick_assets = balances['cash'] + balances['receivables'] + balances['securities']
            quick_ratio = quick_assets / balances['liabilities']
            
            # تعیین وضعیت نقدینگی
            if quick_ratio >= 2.0:
                status = 'عالی'
            elif quick_ratio >= min_ratio:
                status = 'خوب'
            elif quick_ratio >= 0.5:
                status = 'ضعیف'
            else:
                status = 'بحرانی'
            
            row = {
                'Period': period,
                'Cash': round(balances['cash'], 2),
                'AccountsReceivable': round(balances['receivables'], 2),
                'MarketableSecurities': round(balances['securities'], 2),
                'CurrentLiabilities': round(balances['liabilities'], 2),
                'QuickRatio': round(quick_ratio, 4),
                'LiquidityStatus': status
            }
            data.append(row)
    
    # مرتب‌سازی بر اساس نسبت آنی
    data.sort(key=lambda x: x['QuickRatio'])
    
    return data
