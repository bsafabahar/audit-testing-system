# Parameter and Schema Helper Functions - Usage Guide

## Overview

Use helper functions to define parameters and schemas easily instead of writing dictionaries manually.

---

## Schema Helper Functions

### 1. `col(key, display_name, col_type='string')`
Define a single column for your schema with optional type.

**Supported Column Types:**
- `string` - Text data (default)
- `number` - Numeric data (any number)
- `integer` - Integer numbers only
- `decimal` - Decimal/float numbers
- `date` - Date values (YYYY-MM-DD)
- `datetime` - DateTime values (ISO 8601)
- `boolean` - True/false values
- `currency` - Money/currency values

```python
col('Id', 'شناسه', 'integer')
col('Name', 'نام', 'string')
col('Amount', 'مبلغ', 'currency')
col('Price', 'قیمت', 'decimal')
col('Date', 'تاریخ', 'date')
col('IsActive', 'فعال', 'boolean')
```

### 2. `schema(*columns)`
Combine multiple columns into a complete schema.

```python
result_schema = schema(
    col('Id', 'شناسه', 'integer'),
    col('DocumentDate', 'تاریخ سند', 'date'),
    col('AccountCode', 'کد حساب', 'string'),
    col('Debit', 'بدهکار', 'currency'),
    col('Credit', 'بستانکار', 'currency')
)
```

**Old Way vs New Way:**

```python
# ❌ Old way - verbose, no type information
schema = [
    {'key': 'Id', 'displayName': 'شناسه'},
    {'key': 'DocumentDate', 'displayName': 'تاریخ سند'},
    {'key': 'AccountCode', 'displayName': 'کد حساب'}
]

# ✅ New way - clean, readable, with type information
result_schema = schema(
    col('Id', 'شناسه', 'integer'),
    col('DocumentDate', 'تاریخ سند', 'date'),
    col('AccountCode', 'کد حساب', 'string')
)
```

**JSON Output with Types:**
```json
{
  "schema": {
    "columns": [
      {
        "key": "Id",
        "displayName": "شناسه",
        "type": "integer"
      },
      {
        "key": "Amount",
        "displayName": "مبلغ",
        "type": "currency"
      },
      {
        "key": "Date",
        "displayName": "تاریخ",
        "type": "date"
      }
    ]
  }
}
```

---

## Parameter Helper Functions

### 1. `param_string(key, display_name, required=False, default_value=None)`
For text input fields.

```python
param_string('accountCode', 'کد حساب')
param_string('description', 'شرح', required=True)
param_string('name', 'نام', default_value='پیش فرض')
```

### 2. `param_number(key, display_name, required=False, default_value=None)`
For numeric input (integer or decimal).

```python
param_number('limit', 'تعداد رکورد', default_value=20)
param_number('amount', 'مبلغ', required=True)
param_number('age', 'سن', default_value=0)
```

### 3. `param_date(key, display_name, required=False, default_value=None)`
For date picker (YYYY-MM-DD format).

```python
param_date('startDate', 'تاریخ شروع')
param_date('birthDate', 'تاریخ تولد', required=True)
param_date('filterDate', 'تاریخ فیلتر', default_value='2025-01-01')
```

### 4. `param_datetime(key, display_name, required=False, default_value=None)`
For datetime picker (ISO 8601 format).

```python
param_datetime('createdAt', 'تاریخ ایجاد')
param_datetime('lastModified', 'آخرین تغییر', required=True)
```

### 5. `param_boolean(key, display_name, required=False, default_value=False)`
For checkbox (true/false).

```python
param_boolean('includeDeleted', 'شامل حذف شده ها')
param_boolean('isActive', 'فعال', default_value=True)
param_boolean('showDetails', 'نمایش جزئیات', required=True)
```

### 6. `param_select(key, display_name, options, required=False, default_value=None)`
For dropdown with predefined options.

```python
param_select(
    'transactionType',
    'نوع تراکنش',
    options=[
        option('all', 'همه'),
        option('debit', 'بدهکار'),
        option('credit', 'بستانکار')
    ],
    default_value='all'
)

param_select(
    'status',
    'وضعیت',
    options=[
        option('pending', 'در انتظار'),
        option('approved', 'تایید شده'),
        option('rejected', 'رد شده')
    ],
    required=True
)
```

### 7. `option(value, label)`
Helper to create option items for select parameters.

```python
option('value1', 'Label 1')
option('active', 'فعال')
```

## Complete Example

```python
def my_report_query():
    """
    Custom report with various parameter types
    """
    # Define parameters - Much cleaner!
    parameters = [
        param_date('startDate', 'تاریخ شروع', required=True),
        param_date('endDate', 'تاریخ پایان', required=True),
        param_string('accountCode', 'کد حساب'),
        param_number('minAmount', 'حداقل مبلغ', default_value=0),
        param_select(
            'reportType',
            'نوع گزارش',
            options=[
                option('summary', 'خلاصه'),
                option('detailed', 'تفصیلی'),
                option('chart', 'نمودار')
            ],
            default_value='summary'
        ),
        param_boolean('includeSubAccounts', 'شامل حساب های فرعی', default_value=True)
    ]
    
    # Define schema - Clean and simple!
    result_schema = schema(
        col('Id', 'شناسه', 'integer'),
        col('AccountName', 'نام حساب', 'string'),
        col('Amount', 'مبلغ', 'currency'),
        col('Date', 'تاریخ', 'date'),
        col('Description', 'شرح', 'string')
    )
    
    if GET_PARAMETERS_ONLY:
        display_table([], schema=result_schema, parameters=parameters)
        return
    
    session = get_db()
    try:
        # Get parameter values
        start_date = get_parameter('startDate')
        end_date = get_parameter('endDate')
        account_code = get_parameter('accountCode')
        min_amount = get_parameter('minAmount', 0)
        report_type = get_parameter('reportType', 'summary')
        include_sub = get_parameter('includeSubAccounts', True)
        
        # Build your query...
        query = session.query(Transaction)
        
        if start_date:
            query = query.filter(Transaction.DocumentDate >= start_date)
        if end_date:
            query = query.filter(Transaction.DocumentDate <= end_date)
        if account_code:
            query = query.filter(Transaction.AccountCode == account_code)
        
        results = query.all()
        
        # Format data
        data = [(r.Id, r.AccountCode, float(r.Debit), r.DocumentDate, r.Description) for r in results]
        
        display_table(data, schema=result_schema, parameters=parameters)
        
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
    finally:
        session.close()
```

## Old Way vs New Way Summary

### ❌ Old Way (Manual Dictionaries)
```python
parameters = [
    {
        'key': 'startDate',
        'displayName': 'تاریخ شروع',
        'type': 'date',
        'required': False,
        'defaultValue': None
    },
    {
        'key': 'limit',
        'displayName': 'تعداد رکورد',
        'type': 'number',
        'required': False,
        'defaultValue': 20
    }
]

schema = [
    {'key': 'Id', 'displayName': 'شناسه'},
    {'key': 'Name', 'displayName': 'نام'},
    {'key': 'Amount', 'displayName': 'مبلغ'}
]
```

### ✅ New Way (Helper Functions)
```python
parameters = [
    param_date('startDate', 'تاریخ شروع'),
    param_number('limit', 'تعداد رکورد', default_value=20)
]

result_schema = schema(
    col('Id', 'شناسه', 'integer'),
    col('Name', 'نام', 'string'),
    col('Amount', 'مبلغ', 'currency')
)
```

Much cleaner, easier to read, and includes type information for better frontend handling!
