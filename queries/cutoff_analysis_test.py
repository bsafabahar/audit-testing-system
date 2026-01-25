"""
آزمون برش تراکنش‌ها
Cutoff Analysis Test

این آزمون تراکنش‌های نزدیک به تاریخ پایان دوره را بررسی می‌کند.
برای اطمینان از ثبت تراکنش‌ها در دوره مالی صحیح استفاده می‌شود.
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_date, param_number
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
from datetime import datetime, timedelta


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_date('yearEndDate', 'تاریخ پایان دوره مالی', required=True),
        param_number('daysBeforeCutoff', 'تعداد روز قبل از برش', default_value=7),
        param_number('daysAfterCutoff', 'تعداد روز بعد از برش', default_value=7),
        param_number('minAmount', 'حداقل مبلغ برای بررسی', default_value=1000)
    ]
    
    result_schema = schema(
        col('TransactionId', 'شناسه تراکنش', 'integer'),
        col('Date', 'تاریخ', 'date'),
        col('AccountCode', 'کد حساب', 'string'),
        col('Description', 'شرح', 'string'),
        col('Debit', 'بدهکار', 'money'),
        col('Credit', 'بستانکار', 'money'),
        col('DaysFromCutoff', 'فاصله از برش (روز)', 'integer'),
        col('Period', 'دوره', 'string'),
        col('RiskLevel', 'سطح ریسک', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون برش تراکنش‌ها"""
    
    year_end_str = get_parameter('yearEndDate')
    days_before = get_parameter('daysBeforeCutoff', 7)
    days_after = get_parameter('daysAfterCutoff', 7)
    min_amount = get_parameter('minAmount', 1000)
    
    # تبدیل تاریخ
    try:
        year_end = datetime.strptime(year_end_str, '%Y-%m-%d').date()
    except:
        return []
    
    # محاسبه بازه تاریخی
    start_date = year_end - timedelta(days=days_before)
    end_date = year_end + timedelta(days=days_after)
    
    # دریافت تراکنش‌های در بازه
    query = session.query(Transaction).filter(
        Transaction.DocumentDate >= start_date,
        Transaction.DocumentDate <= end_date
    )
    results = query.all()
    
    data = []
    
    for t in results:
        if not t.DocumentDate:
            continue
        
        # محاسبه مبلغ
        debit = float(t.Debit) if t.Debit else 0.0
        credit = float(t.Credit) if t.Credit else 0.0
        amount = max(debit, credit)
        
        # فیلتر بر اساس حداقل مبلغ
        if amount < min_amount:
            continue
        
        # محاسبه فاصله از تاریخ برش
        days_diff = (t.DocumentDate - year_end).days
        
        # تعیین دوره
        if t.DocumentDate < year_end:
            period = 'قبل از برش'
        elif t.DocumentDate == year_end:
            period = 'روز برش'
        else:
            period = 'بعد از برش'
        
        # تعیین سطح ریسک
        risk_level = 'پایین'
        if amount > 100000:  # مبالغ بالا
            if abs(days_diff) <= 1:  # نزدیک به برش
                risk_level = 'بالا'
            elif abs(days_diff) <= 3:
                risk_level = 'متوسط'
        elif abs(days_diff) <= 1:
            risk_level = 'متوسط'
        
        row = {
            'TransactionId': t.Id,
            'Date': t.DocumentDate.strftime('%Y-%m-%d'),
            'AccountCode': t.AccountCode or '',
            'Description': t.Description or '',
            'Debit': debit,
            'Credit': credit,
            'DaysFromCutoff': days_diff,
            'Period': period,
            'RiskLevel': risk_level
        }
        data.append(row)
    
    # مرتب‌سازی بر اساس فاصله از برش و مبلغ
    data.sort(key=lambda x: (abs(x['DaysFromCutoff']), -max(x['Debit'], x['Credit'])))
    
    return data
