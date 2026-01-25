"""
اسکریپت تولید فایل‌های نمونه داده برای آزمون‌های حسابرسی
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# تنظیمات
np.random.seed(42)
random.seed(42)

def generate_transactions_data(num_records=1000):
    """تولید داده‌های تراکنش مالی (دفتر روزنامه)"""
    start_date = datetime(2023, 1, 1)
    
    data = []
    for i in range(num_records):
        date = start_date + timedelta(days=random.randint(0, 365))
        doc_number = 1000 + i
        account_code = random.choice(['1101', '1102', '2101', '3101', '4101', '5101', '6101'])
        
        # مبالغ متنوع برای آزمون بنفورد
        amount = random.choice([
            round(random.uniform(100, 10000), 2),
            round(random.uniform(10000, 100000), 2),
            round(random.uniform(1000, 5000), 0),  # اعداد گرد
            random.choice([1000, 2000, 5000, 10000])  # اعداد گرد کامل
        ])
        
        debit = amount if random.random() > 0.5 else 0
        credit = 0 if debit > 0 else amount
        
        description = random.choice([
            'خرید کالا',
            'فروش محصول',
            'پرداخت حقوق',
            'دریافت از مشتری',
            'پرداخت به تامین کننده',
            'هزینه اداری'
        ])
        
        data.append({
            'تاریخ': date.strftime('%Y/%m/%d'),
            'شماره سند': doc_number,
            'کد حساب': account_code,
            'بدهکار': debit,
            'بستانکار': credit,
            'شرح': description
        })
    
    return pd.DataFrame(data)

def generate_sales_data(num_records=500):
    """تولید داده‌های فروش"""
    start_date = datetime(2023, 1, 1)
    
    customers = ['مشتری ' + str(i) for i in range(1, 51)]
    products = ['کالا ' + chr(65+i) for i in range(10)]
    
    data = []
    for i in range(num_records):
        date = start_date + timedelta(days=random.randint(0, 365))
        invoice_number = 5000 + i
        customer_id = 'C' + str(random.randint(1, 50)).zfill(3)
        customer_name = random.choice(customers)
        product_id = 'P' + str(random.randint(1, 10)).zfill(3)
        product_name = random.choice(products)
        quantity = random.randint(1, 100)
        unit_price = round(random.uniform(10, 1000), 2)
        discount_percent = random.choice([0, 0, 0, 5, 10, 15, 20, 50])  # برخی تخفیفات غیرعادی
        
        subtotal = quantity * unit_price
        discount_amount = subtotal * discount_percent / 100
        total = subtotal - discount_amount
        
        data.append({
            'تاریخ': date.strftime('%Y/%m/%d'),
            'شماره فاکتور': invoice_number,
            'کد مشتری': customer_id,
            'نام مشتری': customer_name,
            'کد کالا': product_id,
            'نام کالا': product_name,
            'تعداد': quantity,
            'قیمت واحد': unit_price,
            'درصد تخفیف': discount_percent,
            'مبلغ تخفیف': round(discount_amount, 2),
            'مبلغ کل': round(total, 2)
        })
    
    return pd.DataFrame(data)

def generate_inventory_data(num_records=300):
    """تولید داده‌های موجودی انبار"""
    start_date = datetime(2023, 1, 1)
    
    products = ['کالا ' + chr(65+i) for i in range(20)]
    
    data = []
    for i in range(num_records):
        date = start_date + timedelta(days=random.randint(0, 365))
        product_id = 'P' + str(random.randint(1, 20)).zfill(3)
        product_name = random.choice(products)
        quantity = random.randint(-50, 100)  # منفی برای خروج، مثبت برای ورود
        
        # برخی قیمت‌های غیرعادی
        if random.random() < 0.05:
            unit_price = 1  # قیمت یک ریال
        else:
            unit_price = round(random.uniform(10, 500), 2)
        
        total = quantity * unit_price
        movement_type = 'ورود' if quantity > 0 else 'خروج'
        
        data.append({
            'تاریخ': date.strftime('%Y/%m/%d'),
            'کد کالا': product_id,
            'نام کالا': product_name,
            'تعداد': abs(quantity),
            'قیمت واحد': unit_price,
            'مبلغ کل': abs(total),
            'نوع حرکت': movement_type
        })
    
    return pd.DataFrame(data)

def generate_payroll_data(num_records=120):
    """تولید داده‌های حقوق و دستمزد"""
    months = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 
              'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
    
    employees = []
    for i in range(1, 31):
        emp_id = 'E' + str(i).zfill(3)
        emp_name = f'کارمند {i}'
        employees.append((emp_id, emp_name))
    
    data = []
    for month in months[:10]:  # 10 ماه
        for emp_id, emp_name in employees:
            base_salary = random.choice([5000000, 7000000, 10000000, 15000000])
            
            # برخی ساعات اضافی غیرعادی
            if random.random() < 0.1:
                overtime = base_salary * random.uniform(0.5, 1.0)  # اضافه کار بیش از حد
            else:
                overtime = base_salary * random.uniform(0, 0.3)
            
            bonus = random.choice([0, 0, 0, 500000, 1000000])
            deductions = base_salary * 0.07  # بیمه و مالیات
            net_pay = base_salary + overtime + bonus - deductions
            
            data.append({
                'ماه': month,
                'کد پرسنلی': emp_id,
                'نام': emp_name,
                'حقوق پایه': base_salary,
                'اضافه کار': round(overtime, 0),
                'پاداش': bonus,
                'کسورات': round(deductions, 0),
                'خالص پرداختی': round(net_pay, 0)
            })
    
    return pd.DataFrame(data)

def generate_checks_data(num_records=200):
    """تولید داده‌های چک‌ها"""
    start_date = datetime(2023, 1, 1)
    
    banks = ['ملی', 'ملت', 'صادرات', 'تجارت', 'سپه']
    payees = ['شرکت ' + chr(65+i) for i in range(20)]
    statuses = ['پاس شده', 'در جریان وصول', 'معلق', 'برگشتی']
    
    data = []
    for i in range(num_records):
        issue_date = start_date + timedelta(days=random.randint(0, 365))
        due_date = issue_date + timedelta(days=random.randint(30, 180))
        check_number = 1000000 + i
        bank = random.choice(banks)
        
        amount = round(random.uniform(1000000, 50000000), 0)
        payee = random.choice(payees)
        status = random.choice(statuses)
        
        data.append({
            'تاریخ صدور': issue_date.strftime('%Y/%m/%d'),
            'تاریخ سررسید': due_date.strftime('%Y/%m/%d'),
            'شماره چک': check_number,
            'بانک': bank,
            'مبلغ': amount,
            'دریافت کننده': payee,
            'وضعیت': status
        })
    
    return pd.DataFrame(data)

def main():
    """تولید تمام فایل‌های نمونه"""
    print("Generating sample data files...")
    
    # تولید داده‌ها
    transactions = generate_transactions_data(1000)
    sales = generate_sales_data(500)
    inventory = generate_inventory_data(300)
    payroll = generate_payroll_data(120)
    checks = generate_checks_data(200)
    
    # ذخیره فایل‌های نمونه
    transactions.to_excel('excel_sample_data/Transactions_SampleData.xlsx', index=False)
    sales.to_excel('excel_sample_data/SalesTransactions_SampleData.xlsx', index=False)
    inventory.to_excel('excel_sample_data/InventoryIssues_SampleData.xlsx', index=False)
    payroll.to_excel('excel_sample_data/PayrollTransactions_SampleData.xlsx', index=False)
    checks.to_excel('excel_sample_data/CheckPayables_SampleData.xlsx', index=False)
    
    # ذخیره فایل‌های template (خالی با عنوان ستون‌ها)
    transactions.head(0).to_excel('excel_templates/Transactions_Template.xlsx', index=False)
    sales.head(0).to_excel('excel_templates/SalesTransactions_Template.xlsx', index=False)
    inventory.head(0).to_excel('excel_templates/InventoryIssues_Template.xlsx', index=False)
    payroll.head(0).to_excel('excel_templates/PayrollTransactions_Template.xlsx', index=False)
    checks.head(0).to_excel('excel_templates/CheckPayables_Template.xlsx', index=False)
    
    print("\nFiles generated successfully:")
    print(f"  - Transactions: {len(transactions)} records")
    print(f"  - Sales: {len(sales)} records")
    print(f"  - Inventory: {len(inventory)} records")
    print(f"  - Payroll: {len(payroll)} records")
    print(f"  - Checks: {len(checks)} records")
    print("\nFiles saved to:")
    print("  - excel_sample_data/")
    print("  - excel_templates/")

if __name__ == '__main__':
    main()
