"""
آزمون تفکیک وظایف
Segregation of Duties Test

این آزمون تفکیک وظایف را بررسی می‌کند.
کاربرانی که دسترسی به وظایف متعارض دارند، شناسایی می‌شوند.
"""
from typing import List, Dict, Any
from models import Transaction
from schema import col, schema
from types_definitions import QueryDefinition
from database import ReadOnlySession
from collections import defaultdict


def define() -> QueryDefinition:
    """تعریف پارامترها و اسکیما"""
    parameters = []
    
    result_schema = schema(
        col('UserID', 'شناسه کاربر', 'string'),
        col('UserName', 'نام کاربر', 'string'),
        col('FunctionCount', 'تعداد وظیفه', 'integer'),
        col('Functions', 'وظایف', 'string'),
        col('ConflictingFunctions', 'وظایف متعارض', 'string'),
        col('TransactionCount', 'تعداد تراکنش', 'integer'),
        col('ViolationSeverity', 'شدت تخلف', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """اجرای آزمون تفکیک وظایف"""
    
    # دریافت داده‌ها
    query = session.query(Transaction)
    results = query.all()
    
    # گروه‌بندی بر اساس کاربر
    user_functions = defaultdict(lambda: {
        'name': '',
        'functions': set(),
        'count': 0
    })
    
    for t in results:
        if hasattr(t, 'UserID') and t.UserID:
            user_id = t.UserID
            
            if hasattr(t, 'UserName') and t.UserName:
                user_functions[user_id]['name'] = t.UserName
            
            user_functions[user_id]['count'] += 1
            
            # استخراج نوع وظیفه
            if hasattr(t, 'FunctionType') and t.FunctionType:
                user_functions[user_id]['functions'].add(t.FunctionType)
            elif hasattr(t, 'TransactionType') and t.TransactionType:
                user_functions[user_id]['functions'].add(t.TransactionType)
            elif hasattr(t, 'EntryType') and t.EntryType:
                user_functions[user_id]['functions'].add(t.EntryType)
    
    # تعریف وظایف متعارض
    conflicting_pairs = [
        ('Approve', 'Record'),
        ('Initiate', 'Approve'),
        ('Custody', 'Record'),
        ('Purchase', 'Receive'),
        ('Sale', 'Collect')
    ]
    
    # تحلیل تفکیک وظایف
    data = []
    
    for user_id, info in user_functions.items():
        if len(info['functions']) >= 2:
            # بررسی وظایف متعارض
            conflicts = []
            
            for func1, func2 in conflicting_pairs:
                if func1 in info['functions'] and func2 in info['functions']:
                    conflicts.append(f"{func1}-{func2}")
            
            if conflicts:
                # تعیین شدت تخلف
                if len(conflicts) >= 3:
                    severity = 'بحرانی'
                elif len(conflicts) >= 2:
                    severity = 'بالا'
                else:
                    severity = 'متوسط'
                
                row = {
                    'UserID': str(user_id),
                    'UserName': info['name'] or 'نامشخص',
                    'FunctionCount': len(info['functions']),
                    'Functions': ', '.join(sorted(info['functions'])),
                    'ConflictingFunctions': ', '.join(conflicts),
                    'TransactionCount': info['count'],
                    'ViolationSeverity': severity
                }
                data.append(row)
    
    # مرتب‌سازی بر اساس شدت
    severity_order = {'بحرانی': 0, 'بالا': 1, 'متوسط': 2}
    data.sort(key=lambda x: severity_order.get(x['ViolationSeverity'], 3))
    
    return data
