"""
Get Transactions Summary Query
Returns a summary of transactions with optional filters.
"""
from typing import List, Dict, Any
from models import Transaction
from parameters import param_date, param_string, param_number
from schema import col, schema
from query_runner import get_parameter
from types_definitions import QueryDefinition
from database import ReadOnlySession


def define() -> QueryDefinition:
    """
    Define parameters and schema for this query.
    This is called when --get-parameters flag is used.
    Returns a dict with 'parameters' and 'schema' keys.
    """
    # Define parameters using helper functions
    parameters = [
        param_date('startDate', 'تاریخ شروع'),
        param_date('endDate', 'تاریخ پایان'),
        param_string('accountCode', 'کد حساب'),
        param_number('limit', 'تعداد رکورد', default_value=20)
    ]
    
    # Define schema using helper functions
    result_schema = schema(
        col('Id', 'شناسه', 'integer'),
        col('DocumentDate', 'تاریخ سند', 'date'),
        col('DocumentNumber', 'شماره سند', 'integer'),
        col('AccountCode', 'کد حساب', 'string'),
        col('Debit', 'بدهکار', 'currency'),
        col('Credit', 'بستانکار', 'currency'),
        col('Description', 'شرح', 'string')
    )
    
    return {
        'parameters': parameters,
        'schema': result_schema
    }


def execute(session: ReadOnlySession) -> List[Dict[str, Any]]:
    """
    Execute the query and return data.
    
    Args:
        session: SQLAlchemy read-only session (managed by runner)
    
    Returns:
        List of dictionaries with data
    """
    # Get input parameters
    limit = get_parameter('limit', 20)
    start_date = get_parameter('startDate')
    end_date = get_parameter('endDate')
    account_code = get_parameter('accountCode')
    
    # Build query with filters based on parameters
    query = session.query(Transaction)
    
    if start_date:
        query = query.filter(Transaction.DocumentDate >= start_date)
    if end_date:
        query = query.filter(Transaction.DocumentDate <= end_date)
    if account_code:
        query = query.filter(Transaction.AccountCode.like(f'%{account_code}%'))
    
    results = query.limit(limit).all()
    
    # Return data as list of dictionaries
    data = []
    for t in results:
        row = {
            'Id': t.Id,
            'DocumentDate': t.DocumentDate.strftime('%Y-%m-%d') if t.DocumentDate else '',
            'DocumentNumber': t.DocumentNumber,
            'AccountCode': t.AccountCode,
            'Debit': float(t.Debit) if t.Debit else 0.0,
            'Credit': float(t.Credit) if t.Credit else 0.0,
            'Description': t.Description[:50] if t.Description else ''
        }
        data.append(row)
    
    return data
