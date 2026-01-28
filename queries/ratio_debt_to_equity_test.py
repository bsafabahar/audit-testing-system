"""
آزمون نسبت بدهی به حقوق صاحبان سهام
Debt to Equity Ratio Test

این آزمون نسبت بدهی به حقوق صاحبان سهام را محاسبه و تحلیل می‌کند.
نسبت‌های بالا نشان‌دهنده ریسک مالی بالا هستند.
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
        param_number('maxDebtRatio', 'حداکثر نسبت بدهی', default_value=2.0)
    ]
    
    result_schema = schema(
        col('Period', 'دوره', 'string'),
        col('TotalDebt', 'کل بدهی', 'money'),
        col('TotalEquity', 'کل حقوق صاحبان سهام', 'money'),
        col('DebtToEquityRatio', 'نسبت بدهی به حقوق', 'number'),
        col('PreviousRatio', 'نسبت دوره قبل', 'number'),
        col('RatioChange', 'تغییر نسبت', 'number'),
        col('RiskLevel', 'سطح ریسک', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون نسبت بدهی به حقوق"""
    
    max_ratio = get_parameter('maxDebtRatio', 2.0)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # گروه‌بندی بر اساس دوره
    period_data = defaultdict(lambda: {
        'debt': 0,
        'equity': 0
    })
    
    for t in results:
        if hasattr(t, 'TransactionDate') and t.TransactionDate:
            period = t.TransactionDate.strftime('%Y-%m')
            
            if hasattr(t, 'AccountType'):
                account_type = t.AccountType
                amount = t.Debit if t.Debit else t.Credit if t.Credit else 0
                
                if account_type in ['Liability', 'Debt', 'Payable']:
                    period_data[period]['debt'] += amount
                elif account_type in ['Equity', 'Capital', 'RetainedEarnings']:
                    period_data[period]['equity'] += amount
    
    # محاسبه نسبت
    sorted_periods = sorted(period_data.items())
    data = []
    prev_ratio = None
    
    for period, balances in sorted_periods:
        if balances['equity'] > 0:
            debt_ratio = balances['debt'] / balances['equity']
            
            # محاسبه تغییر نسبت
            ratio_change = 0
            if prev_ratio is not None:
                ratio_change = debt_ratio - prev_ratio
            
            # تعیین سطح ریسک
            if debt_ratio > max_ratio * 2:
                risk = 'خیلی بالا'
            elif debt_ratio > max_ratio:
                risk = 'بالا'
            elif debt_ratio > max_ratio * 0.5:
                risk = 'متوسط'
            else:
                risk = 'پایین'
            
            row = {
                'Period': period,
                'TotalDebt': round(balances['debt'], 2),
                'TotalEquity': round(balances['equity'], 2),
                'DebtToEquityRatio': round(debt_ratio, 4),
                'PreviousRatio': round(prev_ratio, 4) if prev_ratio is not None else 0,
                'RatioChange': round(ratio_change, 4),
                'RiskLevel': risk
            }
            data.append(row)
            
            prev_ratio = debt_ratio
    
    # مرتب‌سازی بر اساس نسبت
    data.sort(key=lambda x: x['DebtToEquityRatio'], reverse=True)
    
    return data
