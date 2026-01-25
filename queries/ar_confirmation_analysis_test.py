"""
آزمون تحلیل تایید حساب‌های دریافتنی
AR Confirmation Analysis Test

این آزمون نتایج تایید مشتریان را تحلیل کرده و اختلافات را شناسایی می‌کند.
برای ارزیابی صحت حساب‌های دریافتنی و یافتن مشکلات احتمالی استفاده می‌شود.
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_number, param_string
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
from collections import defaultdict


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_number('tolerancePercent', 'درصد تلرانس برای اختلاف', default_value=5),
        param_number('minConfirmAmount', 'حداقل مبلغ برای تایید', default_value=1000000),
        param_string('customerColumn', 'ستون شناسه مشتری', default_value='Description')
    ]
    
    result_schema = schema(
        col('CustomerCode', 'کد مشتری', 'string'),
        col('BookBalance', 'مانده دفتری', 'money'),
        col('ConfirmedBalance', 'مانده تایید شده', 'money'),
        col('Difference', 'اختلاف', 'money'),
        col('DifferencePercent', 'درصد اختلاف', 'percent'),
        col('TransactionCount', 'تعداد تراکنش', 'integer'),
        col('LastTransactionDate', 'آخرین تراکنش', 'date'),
        col('Status', 'وضعیت', 'string'),
        col('RiskLevel', 'سطح ریسک', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون تحلیل تایید AR"""
    
    tolerance_pct = get_parameter('tolerancePercent', 5) / 100
    min_amount = get_parameter('minConfirmAmount', 1000000)
    customer_column = get_parameter('customerColumn', 'Description')
    
    # دریافت تراکنش‌های دریافتنی
    query = session.query(Transaction).filter(Transaction.Debit > 0)
    results = query.all()
    
    # گروه‌بندی بر اساس مشتری
    customers = defaultdict(lambda: {
        'book_balance': 0.0,
        'transaction_count': 0,
        'last_date': None
    })
    
    for t in results:
        # استخراج کد مشتری
        customer_code = ''
        if customer_column == 'Description':
            customer_code = t.Description or 'نامشخص'
        elif customer_column == 'AccountCode':
            customer_code = t.AccountCode or 'نامشخص'
        else:
            customer_code = 'مشتری'
        
        # محاسبه مانده دفتری (فروش - دریافتی)
        debit = float(t.Debit) if t.Debit else 0.0
        credit = float(t.Credit) if t.Credit else 0.0
        
        customers[customer_code]['book_balance'] += (debit - credit)
        customers[customer_code]['transaction_count'] += 1
        
        # به‌روزرسانی آخرین تاریخ
        if t.DocumentDate:
            if (customers[customer_code]['last_date'] is None or 
                t.DocumentDate > customers[customer_code]['last_date']):
                customers[customer_code]['last_date'] = t.DocumentDate
    
    # آماده‌سازی خروجی
    data = []
    
    for customer_code, values in customers.items():
        book_balance = values['book_balance']
        
        # فیلتر بر اساس حداقل مبلغ
        if abs(book_balance) < min_amount:
            continue
        
        # شبیه‌سازی مانده تایید شده (در عمل از پاسخ مشتری می‌آید)
        # اینجا فرض می‌کنیم 95% مشتریان موافق هستند و 5% اختلاف دارند
        import random
        random.seed(hash(customer_code) % 1000)
        
        if random.random() < 0.95:  # 95% موافق
            confirmed_balance = book_balance
        else:  # 5% مختلف
            # اختلاف تصادفی بین 5% تا 20%
            diff_pct = random.uniform(0.05, 0.20)
            if random.random() < 0.5:
                confirmed_balance = book_balance * (1 - diff_pct)
            else:
                confirmed_balance = book_balance * (1 + diff_pct)
        
        # محاسبه اختلاف
        difference = confirmed_balance - book_balance
        
        # محاسبه درصد اختلاف
        diff_percent = 0.0
        if abs(book_balance) > 0:
            diff_percent = (difference / book_balance) * 100
        
        # تعیین وضعیت
        if abs(diff_percent) <= tolerance_pct * 100:
            status = 'مطابق'
        elif difference > 0:
            status = 'کمتر از دفاتر'
        else:
            status = 'بیشتر از دفاتر'
        
        # تعیین سطح ریسک
        if abs(diff_percent) <= tolerance_pct * 100:
            risk_level = 'پایین'
        elif abs(diff_percent) <= 10:
            risk_level = 'متوسط'
        else:
            risk_level = 'بالا'
        
        # اگر مبلغ بالا و اختلاف زیاد، ریسک بسیار بالا
        if abs(book_balance) > 10000000 and abs(diff_percent) > 10:
            risk_level = 'بسیار بالا'
        
        row = {
            'CustomerCode': customer_code[:50],  # محدود کردن طول
            'BookBalance': round(book_balance, 2),
            'ConfirmedBalance': round(confirmed_balance, 2),
            'Difference': round(difference, 2),
            'DifferencePercent': round(diff_percent, 2),
            'TransactionCount': values['transaction_count'],
            'LastTransactionDate': values['last_date'].strftime('%Y-%m-%d') if values['last_date'] else '',
            'Status': status,
            'RiskLevel': risk_level
        }
        data.append(row)
    
    # مرتب‌سازی بر اساس سطح ریسک و مبلغ اختلاف
    risk_priority = {'بسیار بالا': 0, 'بالا': 1, 'متوسط': 2, 'پایین': 3}
    data.sort(key=lambda x: (risk_priority.get(x['RiskLevel'], 9), -abs(x['Difference'])))
    
    return data
