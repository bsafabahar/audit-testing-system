#!/usr/bin/env python3
"""
Script to update test files to use proper model classes
"""
import os
import re

# Define which tests should use which models
TEST_MODEL_MAPPING = {
    # Payroll tests - use PayrollTransactions
    'payroll_abnormal_salary_test.py': {
        'model': 'PayrollTransactions',
        'field_mapping': {
            'EmployeeID': 'EmployeeCode',
            'PayrollAmount': 'NetPayment',
            'TransactionDate': 'VoucherDate',
        }
    },
    'payroll_excessive_overtime_test.py': {
        'model': 'PayrollTransactions',
        'field_mapping': {
            'EmployeeID': 'EmployeeCode',
            'TransactionDate': 'VoucherDate',
        }
    },
    'payroll_duplicate_numbers_test.py': {
        'model': 'PayrollTransactions',
        'field_mapping': {
            'EmployeeID': 'EmployeeCode',
            'PayrollAmount': 'NetPayment',
            'TransactionDate': 'VoucherDate',
        }
    },
    'payroll_ghost_employees_test.py': {
        'model': 'PayrollTransactions',
        'field_mapping': {
            'EmployeeID': 'EmployeeCode',
            'PayrollAmount': 'NetPayment',
            'TransactionDate': 'VoucherDate',
        }
    },
    
    # Banking/Check tests - use CheckPayables or keep Transaction
    'banking_outstanding_checks_test.py': {
        'model': 'CheckPayables',
        'field_mapping': {
            'CheckStatus': None,  # May need to be calculated
            'Payee': 'PayeeName',
            'AccountNumber': None,  # Not in CheckPayables
        }
    },
    
    # Sales tests - use SalesTransactions
    'sales_abnormal_discount_test.py': {
        'model': 'SalesTransactions',
        'field_mapping': {
            'TransactionID': 'InvoiceNumber',
            'TransactionDate': 'InvoiceDate',
            'OriginalAmount': None,  # Need to calculate from Quantity * UnitPrice
            'DiscountAmount': None,  # Not in model, may need to add
        }
    },
    'sales_customer_employee_test.py': {
        'model': 'SalesTransactions',  # May need to join with PayrollTransactions
        'field_mapping': {
            'CustomerID': 'CustomerCode',
            'TransactionDate': 'InvoiceDate',
        }
    },
    'sales_markup_analysis_test.py': {
        'model': 'SalesTransactions',
        'field_mapping': {
            'ItemID': 'ItemCode',
            'TransactionID': 'InvoiceNumber',
        }
    },
    'sales_pareto_analysis_test.py': {
        'model': 'SalesTransactions',
        'field_mapping': {
            'CustomerID': 'CustomerCode',
            'TransactionDate': 'InvoiceDate',
        }
    },
    
    # Inventory tests - use InventoryIssues
    'inventory_slow_moving_test.py': {
        'model': 'InventoryIssues',
        'field_mapping': {
            'ItemID': 'ItemCode',
            'TransactionDate': 'IssueDate',
            'TransactionType': None,  # Not in InventoryIssues
        }
    },
    'inventory_one_dollar_items_test.py': {
        'model': 'InventoryIssues',
        'field_mapping': {
            'ItemID': 'ItemCode',
            'TransactionDate': 'IssueDate',
        }
    },
    'inventory_valuation_test.py': {
        'model': 'InventoryIssues',
        'field_mapping': {
            'ItemID': 'ItemCode',
            'TransactionDate': 'IssueDate',
        }
    },
    'inventory_price_frequency_test.py': {
        'model': 'InventoryIssues',
        'field_mapping': {
            'ItemID': 'ItemCode',
            'TransactionDate': 'IssueDate',
        }
    },
    'reconciliation_inventory_consumption_test.py': {
        'model': 'InventoryIssues',
        'field_mapping': {
            'ItemID': 'ItemCode',
            'TransactionDate': 'IssueDate',
            'TransactionType': None,
        }
    },
}

def update_test_file(filepath, model_name, field_mapping):
    """Update a single test file to use the correct model"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update the import statement
    old_import = 'from models import Transaction'
    new_import = f'from models import {model_name}'
    content = content.replace(old_import, new_import)
    
    # Update the query statement
    old_query = 'session.query(Transaction)'
    new_query = f'session.query({model_name})'
    content = content.replace(old_query, new_query)
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Updated {os.path.basename(filepath)} to use {model_name}")

def main():
    queries_dir = 'queries'
    
    for test_file, config in TEST_MODEL_MAPPING.items():
        filepath = os.path.join(queries_dir, test_file)
        
        if os.path.exists(filepath):
            update_test_file(filepath, config['model'], config['field_mapping'])
        else:
            print(f"✗ File not found: {test_file}")

if __name__ == '__main__':
    main()
