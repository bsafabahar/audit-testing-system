"""
آزمون شرکت کاغذی
Shell Company Test

این آزمون تراکنش‌های مشکوک با شرکت‌های کاغذی را شناسایی می‌کند.
شرکت‌هایی که فعالیت واقعی ندارند، تشخیص داده می‌شوند.
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
        param_number('minTransactionAmount', 'حداقل مبلغ تراکنش', default_value=10000000.0)
    ]
    
    result_schema = schema(
        col('VendorID', 'شناسه فروشنده', 'string'),
        col('VendorName', 'نام فروشنده', 'string'),
        col('TransactionCount', 'تعداد تراکنش', 'integer'),
        col('TotalAmount', 'کل مبلغ', 'money'),
        col('AvgAmount', 'میانگین مبلغ', 'money'),
        col('FirstTransaction', 'اولین تراکنش', 'date'),
        col('LastTransaction', 'آخرین تراکنش', 'date'),
        col('SuspicionScore', 'امتیاز مشکوک', 'integer'),
        col('SuspicionReasons', 'دلایل مشکوک بودن', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون شرکت کاغذی"""
    
    min_amount = get_parameter('minTransactionAmount', 10000000.0)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # گروه‌بندی بر اساس فروشنده
    vendor_data = defaultdict(lambda: {
        'name': '',
        'transactions': [],
        'total': 0,
        'dates': []
    })
    
    for t in results:
        if hasattr(t, 'VendorID') and t.VendorID:
            vendor_id = t.VendorID
            amount = t.Debit if t.Debit else t.Credit if t.Credit else 0
            
            if amount >= min_amount:
                vendor_data[vendor_id]['transactions'].append(amount)
                vendor_data[vendor_id]['total'] += amount
                
                if hasattr(t, 'VendorName') and t.VendorName:
                    vendor_data[vendor_id]['name'] = t.VendorName
                
                if hasattr(t, 'TransactionDate') and t.TransactionDate:
                    vendor_data[vendor_id]['dates'].append(t.TransactionDate)
    
    # تحلیل فروشندگان
    data = []
    
    for vendor_id, info in vendor_data.items():
        if info['transactions']:
            trans_count = len(info['transactions'])
            total_amount = info['total']
            avg_amount = total_amount / trans_count
            
            dates = sorted(info['dates']) if info['dates'] else []
            first_date = dates[0] if dates else None
            last_date = dates[-1] if dates else None
            
            # محاسبه امتیاز مشکوک
            suspicion_score = 0
            reasons = []
            
            # تعداد تراکنش کم
            if trans_count <= 3:
                suspicion_score += 20
                reasons.append('تعداد تراکنش کم')
            
            # مبلغ بالا در تراکنش واحد
            if avg_amount > 100000000:
                suspicion_score += 30
                reasons.append('مبلغ تراکنش بالا')
            
            # فعالیت کوتاه‌مدت
            if first_date and last_date:
                days_active = (last_date - first_date).days
                if days_active < 90:
                    suspicion_score += 25
                    reasons.append('فعالیت کوتاه‌مدت')
            
            # نام مشکوک
            if not info['name'] or len(info['name']) < 5:
                suspicion_score += 15
                reasons.append('نام نامشخص')
            
            # فقط موارد مشکوک
            if suspicion_score >= 40:
                row = {
                    'VendorID': str(vendor_id),
                    'VendorName': info['name'] or 'نامشخص',
                    'TransactionCount': trans_count,
                    'TotalAmount': round(total_amount, 2),
                    'AvgAmount': round(avg_amount, 2),
                    'FirstTransaction': first_date.strftime('%Y-%m-%d') if first_date else '',
                    'LastTransaction': last_date.strftime('%Y-%m-%d') if last_date else '',
                    'SuspicionScore': suspicion_score,
                    'SuspicionReasons': ', '.join(reasons)
                }
                data.append(row)
    
    # مرتب‌سازی بر اساس امتیاز
    data.sort(key=lambda x: x['SuspicionScore'], reverse=True)
    
    return data
