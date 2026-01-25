"""
آزمون شناسایی ناهنجاری با Isolation Forest
AI-Powered Anomaly Detection using Isolation Forest

این آزمون از الگوریتم Isolation Forest برای شناسایی تراکنش‌های منزوی و غیرعادی استفاده می‌کند.
تراکنش‌هایی که الگوی آن‌ها با بقیه داده‌ها متفاوت است، شناسایی می‌شوند.
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_number, param_string
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_string('columnName', 'نام ستون مبلغ', default_value='Debit'),
        param_number('contamination', 'نسبت ناهنجاری مورد انتظار', default_value=0.1),
        param_number('minAmount', 'حداقل مبلغ برای بررسی', default_value=0)
    ]
    
    result_schema = schema(
        col('TransactionID', 'شناسه تراکنش', 'string'),
        col('DocumentDate', 'تاریخ سند', 'date'),
        col('AccountCode', 'کد حساب', 'string'),
        col('Amount', 'مبلغ', 'currency'),
        col('HourOfDay', 'ساعت روز', 'integer'),
        col('DayOfWeek', 'روز هفته', 'integer'),
        col('AnomalyScore', 'امتیاز ناهنجاری', 'number'),
        col('IsAIOutlier', 'ناهنجاری AI', 'string'),
        col('Rank', 'رتبه', 'integer')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون Isolation Forest"""
    
    if not SKLEARN_AVAILABLE:
        return [{
            'TransactionID': 'ERROR',
            'DocumentDate': None,
            'AccountCode': 'N/A',
            'Amount': 0,
            'HourOfDay': 0,
            'DayOfWeek': 0,
            'AnomalyScore': 0,
            'IsAIOutlier': 'scikit-learn not installed',
            'Rank': 0
        }]
    
    column_name = get_parameter('columnName', 'Debit')
    contamination = get_parameter('contamination', 0.1)
    min_amount = get_parameter('minAmount', 0)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # استخراج ویژگی‌ها
    features = []
    transaction_data = []
    
    for t in results:
        amount = t.Debit if column_name == 'Debit' else t.Credit
        
        if not amount or amount <= min_amount:
            continue
        
        # استخراج زمان از TransactionDate یا DocumentDate
        trans_date = None
        if hasattr(t, 'TransactionDate') and t.TransactionDate:
            trans_date = t.TransactionDate
        elif hasattr(t, 'DocumentDate') and t.DocumentDate:
            if isinstance(t.DocumentDate, datetime):
                trans_date = t.DocumentDate
            else:
                # DocumentDate is a date, convert to datetime
                trans_date = datetime.combine(t.DocumentDate, datetime.min.time())
        
        hour_of_day = trans_date.hour if trans_date else 12
        day_of_week = trans_date.weekday() if trans_date else 0
        
        # کد حساب به عدد (استفاده از مجموع کدهای ASCII برای تعیین‌گرایی)
        account_code_num = sum(ord(c) for c in (t.AccountCode or '')) % 10000
        
        features.append([
            float(amount),
            float(hour_of_day),
            float(day_of_week),
            float(account_code_num)
        ])
        
        transaction_data.append({
            'transaction': t,
            'amount': amount,
            'hour': hour_of_day,
            'day': day_of_week,
            'date': trans_date
        })
    
    if len(features) < 10:
        return [{
            'TransactionID': 'ERROR',
            'DocumentDate': None,
            'AccountCode': 'N/A',
            'Amount': 0,
            'HourOfDay': 0,
            'DayOfWeek': 0,
            'AnomalyScore': 0,
            'IsAIOutlier': 'Not enough transactions (minimum 10)',
            'Rank': 0
        }]
    
    # نرمال‌سازی ویژگی‌ها
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    # اعمال Isolation Forest
    iso_forest = IsolationForest(
        contamination=contamination,
        random_state=42,
        n_estimators=100
    )
    predictions = iso_forest.fit_predict(features_scaled)
    scores = iso_forest.score_samples(features_scaled)
    
    # جمع‌آوری نتایج
    data = []
    for i, (pred, score) in enumerate(zip(predictions, scores)):
        if pred == -1:  # ناهنجاری
            trans_info = transaction_data[i]
            t = trans_info['transaction']
            
            row = {
                'TransactionID': str(t.TransactionID) if hasattr(t, 'TransactionID') and t.TransactionID else str(t.Id),
                'DocumentDate': trans_info['date'].strftime('%Y-%m-%d') if trans_info['date'] else '',
                'AccountCode': t.AccountCode or '',
                'Amount': round(trans_info['amount'], 2),
                'HourOfDay': trans_info['hour'],
                'DayOfWeek': trans_info['day'],
                'AnomalyScore': round(float(score), 4),
                'IsAIOutlier': 'بله',
                'Rank': 0
            }
            data.append(row)
    
    # مرتب‌سازی بر اساس امتیاز ناهنجاری (پایین‌ترین امتیاز = مشکوک‌ترین)
    data.sort(key=lambda x: x['AnomalyScore'])
    
    # اضافه کردن رتبه
    for i, row in enumerate(data):
        row['Rank'] = i + 1
    
    return data
