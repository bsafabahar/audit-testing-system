"""
آزمون نام‌های تکراری
Duplicate Vendor/Customer Names

شناسایی نام‌های شبیه با استفاده از Fuzzy Matching.
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
        param_number('similarityThreshold', 'آستانه شباهت (0-100)', default_value=80),
        param_number('limit', 'تعداد رکورد', default_value=100)
    ]
    
    result_schema = schema(
        col('AccountCode1', 'کد حساب ۱', 'string'),
        col('AccountCode2', 'کد حساب ۲', 'string'),
        col('SimilarityScore', 'امتیاز شباهت', 'percent'),
        col('TransactionCount1', 'تعداد تراکنش ۱', 'integer'),
        col('TransactionCount2', 'تعداد تراکنش ۲', 'integer'),
        col('TotalAmount1', 'جمع مبلغ ۱', 'currency'),
        col('TotalAmount2', 'جمع مبلغ ۲', 'currency'),
        col('IsSuspicious', 'مشکوک', 'boolean')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def levenshtein_distance(s1: str, s2: str) -> int:
    """محاسبه فاصله Levenshtein"""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def similarity_score(s1: str, s2: str) -> float:
    """محاسبه درصد شباهت"""
    if not s1 or not s2:
        return 0.0
    
    # نرمال‌سازی
    s1 = s1.lower().strip()
    s2 = s2.lower().strip()
    
    if s1 == s2:
        return 100.0
    
    distance = levenshtein_distance(s1, s2)
    max_len = max(len(s1), len(s2))
    
    if max_len == 0:
        return 100.0
    
    similarity = (1 - distance / max_len) * 100
    return similarity


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون نام‌های تکراری"""
    
    threshold = get_parameter('similarityThreshold', 80)
    limit = get_parameter('limit', 100)
    
    query = session.query(Transaction)
    results = query.all()
    
    # گروه‌بندی بر اساس کد حساب
    account_stats = defaultdict(lambda: {'count': 0, 'total': 0.0})
    
    for t in results:
        if t.AccountCode:
            account_stats[t.AccountCode]['count'] += 1
            if t.Debit:
                account_stats[t.AccountCode]['total'] += t.Debit
            if t.Credit:
                account_stats[t.AccountCode]['total'] += t.Credit
    
    # مقایسه نام‌ها
    accounts = list(account_stats.keys())
    data = []
    
    for i in range(len(accounts)):
        for j in range(i + 1, len(accounts)):
            acc1 = accounts[i]
            acc2 = accounts[j]
            
            score = similarity_score(acc1, acc2)
            
            if score >= threshold and score < 100:
                is_suspicious = (
                    account_stats[acc1]['count'] < 10 or 
                    account_stats[acc2]['count'] < 10
                )
                
                row = {
                    'AccountCode1': acc1,
                    'AccountCode2': acc2,
                    'SimilarityScore': round(score, 2),
                    'TransactionCount1': account_stats[acc1]['count'],
                    'TransactionCount2': account_stats[acc2]['count'],
                    'TotalAmount1': round(account_stats[acc1]['total'], 2),
                    'TotalAmount2': round(account_stats[acc2]['total'], 2),
                    'IsSuspicious': is_suspicious
                }
                data.append(row)
    
    # مرتب‌سازی بر اساس امتیاز شباهت
    data.sort(key=lambda x: x['SimilarityScore'], reverse=True)
    
    return data[:limit]
