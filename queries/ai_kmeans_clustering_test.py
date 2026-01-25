"""
آزمون خوشه‌بندی تراکنش‌ها با K-Means
Transaction Clustering using K-Means

این آزمون تراکنش‌ها را بر اساس ویژگی‌های عددی خوشه‌بندی می‌کند.
تراکنش‌های دور از مرکز خوشه یا در خوشه‌های کوچک به عنوان موارد نیازمند بررسی علامت‌گذاری می‌شوند.
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_number, param_string
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession
from datetime import datetime
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = [
        param_string('columnName', 'نام ستون مبلغ', default_value='Debit'),
        param_number('nClusters', 'تعداد خوشه', default_value=5),
        param_number('minClusterSize', 'حداقل اندازه خوشه (درصد)', default_value=1.0),
        param_number('distanceThreshold', 'آستانه فاصله از مرکز', default_value=2.5)
    ]
    
    result_schema = schema(
        col('TransactionID', 'شناسه تراکنش', 'string'),
        col('DocumentDate', 'تاریخ سند', 'date'),
        col('AccountCode', 'کد حساب', 'string'),
        col('Amount', 'مبلغ', 'currency'),
        col('ClusterID', 'شناسه خوشه', 'integer'),
        col('ClusterSize', 'اندازه خوشه', 'integer'),
        col('ClusterPercent', 'درصد خوشه', 'number'),
        col('DistanceFromCenter', 'فاصله از مرکز', 'number'),
        col('NeedsReview', 'نیاز به بررسی', 'string'),
        col('ReviewReason', 'دلیل بررسی', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون K-Means Clustering"""
    
    if not SKLEARN_AVAILABLE:
        return [{
            'TransactionID': 'ERROR',
            'DocumentDate': None,
            'AccountCode': 'N/A',
            'Amount': 0,
            'ClusterID': 0,
            'ClusterSize': 0,
            'ClusterPercent': 0,
            'DistanceFromCenter': 0,
            'NeedsReview': 'خیر',
            'ReviewReason': 'scikit-learn not installed'
        }]
    
    column_name = get_parameter('columnName', 'Debit')
    n_clusters = int(get_parameter('nClusters', 5))
    min_cluster_size_pct = get_parameter('minClusterSize', 1.0)
    distance_threshold = get_parameter('distanceThreshold', 2.5)
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # استخراج ویژگی‌ها
    features = []
    transaction_data = []
    
    for t in results:
        amount = t.Debit if column_name == 'Debit' else t.Credit
        
        if not amount or amount <= 0:
            continue
        
        # استخراج زمان
        trans_date = None
        if hasattr(t, 'TransactionDate') and t.TransactionDate:
            trans_date = t.TransactionDate
        elif hasattr(t, 'DocumentDate') and t.DocumentDate:
            if isinstance(t.DocumentDate, datetime):
                trans_date = t.DocumentDate
            else:
                trans_date = datetime.combine(t.DocumentDate, datetime.min.time())
        
        hour_of_day = trans_date.hour if trans_date else 12
        day_of_week = trans_date.weekday() if trans_date else 0
        day_of_month = trans_date.day if trans_date else 15
        
        # کد حساب به عدد (استفاده از مجموع کدهای ASCII برای تعیین‌گرایی)
        account_code_num = sum(ord(c) for c in (t.AccountCode or '')) % 10000
        
        features.append([
            float(amount),
            float(hour_of_day),
            float(day_of_week),
            float(day_of_month),
            float(account_code_num)
        ])
        
        transaction_data.append({
            'transaction': t,
            'amount': amount,
            'date': trans_date
        })
    
    if len(features) < n_clusters:
        return [{
            'TransactionID': 'ERROR',
            'DocumentDate': None,
            'AccountCode': 'N/A',
            'Amount': 0,
            'ClusterID': 0,
            'ClusterSize': 0,
            'ClusterPercent': 0,
            'DistanceFromCenter': 0,
            'NeedsReview': 'خیر',
            'ReviewReason': f'Not enough transactions (minimum {n_clusters})'
        }]
    
    # نرمال‌سازی ویژگی‌ها
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    # اعمال K-Means
    kmeans = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init=10,
        max_iter=300
    )
    cluster_labels = kmeans.fit_predict(features_scaled)
    
    # محاسبه فاصله از مراکز خوشه‌ها
    distances = []
    for i, features_point in enumerate(features_scaled):
        cluster_id = cluster_labels[i]
        center = kmeans.cluster_centers_[cluster_id]
        distance = np.linalg.norm(features_point - center)
        distances.append(distance)
    
    # شمارش تعداد تراکنش در هر خوشه
    cluster_counts = Counter(cluster_labels)
    total_transactions = len(cluster_labels)
    
    # شناسایی موارد نیازمند بررسی
    data = []
    for i, (cluster_id, distance) in enumerate(zip(cluster_labels, distances)):
        cluster_size = cluster_counts[cluster_id]
        cluster_percent = (cluster_size / total_transactions) * 100
        
        # بررسی شرایط
        is_small_cluster = cluster_percent < min_cluster_size_pct
        is_far_from_center = distance > distance_threshold
        needs_review = is_small_cluster or is_far_from_center
        
        if needs_review:
            trans_info = transaction_data[i]
            t = trans_info['transaction']
            
            # تعیین دلیل بررسی
            reasons = []
            if is_small_cluster:
                reasons.append('خوشه کوچک')
            if is_far_from_center:
                reasons.append('دور از مرکز')
            review_reason = ' - '.join(reasons)
            
            row = {
                'TransactionID': str(t.TransactionID) if hasattr(t, 'TransactionID') and t.TransactionID else str(t.Id),
                'DocumentDate': trans_info['date'].strftime('%Y-%m-%d') if trans_info['date'] else '',
                'AccountCode': t.AccountCode or '',
                'Amount': round(trans_info['amount'], 2),
                'ClusterID': int(cluster_id),
                'ClusterSize': cluster_size,
                'ClusterPercent': round(cluster_percent, 2),
                'DistanceFromCenter': round(float(distance), 4),
                'NeedsReview': 'بله',
                'ReviewReason': review_reason
            }
            data.append(row)
    
    # مرتب‌سازی بر اساس فاصله از مرکز
    data.sort(key=lambda x: x['DistanceFromCenter'], reverse=True)
    
    return data
