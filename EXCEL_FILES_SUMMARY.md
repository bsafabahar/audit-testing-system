# Excel Templates and Sample Data Summary
# خلاصه فایل‌های قالب و داده نمونه اکسل

## What Was Created / آنچه ایجاد شد

### 📁 Directory Structure / ساختار پوشه‌ها

```
audit-testing-system/
├── excel_templates/              # 6 template files / 6 فایل قالب
│   ├── Transactions_Template.xlsx
│   ├── CheckPayables_Template.xlsx
│   ├── CheckReceivables_Template.xlsx
│   ├── PayrollTransactions_Template.xlsx
│   ├── InventoryIssues_Template.xlsx
│   ├── SalesTransactions_Template.xlsx
│   └── README.md                # Documentation / مستندات
│
├── excel_sample_data/           # 5 sample data files / 5 فایل داده نمونه
│   ├── Transactions_SampleData.xlsx         (500 records)
│   ├── CheckPayables_SampleData.xlsx        (50 records)
│   ├── PayrollTransactions_SampleData.xlsx  (100 records)
│   ├── InventoryIssues_SampleData.xlsx      (80 records)
│   └── SalesTransactions_SampleData.xlsx    (120 records)
│
└── generate_excel_templates.py  # Script to regenerate files
```

## Template Files Details / جزئیات فایل‌های قالب

### 1️⃣ Transactions_Template.xlsx (38 columns)

**English Headers (Row 1):**
- Id, DocumentDate, DocumentNumber, DocumentDescription
- AccountCode, TotalCode, SubsidiaryCode, Detail1Code, Detail2Code, Detail3Code
- Debit, Credit, Description, CounterPartyDescription
- IsDeleted, CreationTime
- **New fields:** CheckNumber, CheckStatus, AccountNumber, Payee
- TransactionID, TransactionDate, TransactionType, ReferenceNumber
- EmployeeID, PayrollAmount
- VendorID, VendorName, CustomerID
- OriginalAmount, DiscountAmount
- ItemID, Quantity, BeginningInventory, EndingInventory
- EntryType, EntryTime, EnteredBy

**Persian Headers (Row 2):**
شناسه، تاریخ سند، شماره سند، شرح سند، کد حساب، کد کل، کد معین، کد تفصیل 1، کد تفصیل 2، کد تفصیل 3، بدهکار، بستانکار، شرح، شرح طرف حساب، حذف شده، زمان ایجاد، شماره چک، وضعیت چک، شماره حساب بانکی، دریافت‌کننده، شناسه تراکنش، تاریخ تراکنش، نوع تراکنش، شماره مرجع، شناسه کارمند، مبلغ حقوق، شناسه فروشنده، نام فروشنده، شناسه مشتری، مبلغ اصلی، مبلغ تخفیف، شناسه کالا، مقدار، موجودی اول دوره، موجودی پایان دوره، نوع ثبت، زمان ثبت، ثبت‌کننده

### 2️⃣ CheckPayables_Template.xlsx (10 columns)
Payable checks with document payment info
چک‌های پرداختنی با اطلاعات برگه پرداخت

### 3️⃣ CheckReceivables_Template.xlsx (10 columns)
Receivable checks with document receipt info
چک‌های دریافتنی با اطلاعات برگه دریافت

### 4️⃣ PayrollTransactions_Template.xlsx (16 columns)
Payroll with overtime, deductions, net payment
حقوق و دستمزد با اضافه‌کار، کسورات، خالص پرداختی

### 5️⃣ InventoryIssues_Template.xlsx (12 columns)
Inventory issues with cost center info
حواله‌های انبار با اطلاعات مرکز هزینه

### 6️⃣ SalesTransactions_Template.xlsx (12 columns)
Sales invoices with customer and item details
فاکتورهای فروش با جزئیات مشتری و کالا

## Sample Data Coverage / پوشش داده‌های نمونه

### Transactions_SampleData.xlsx Features:

✅ **Banking Data (42% of records have check info)**
- Check numbers, status, account numbers
- Payee information
- Check statuses: Issued, Outstanding, Pending, Cleared

✅ **Payroll Data (32% of records)**
- Employee IDs (E001-E008)
- Payroll amounts
- Entry types and timestamps

✅ **Vendor/Purchase Data (14% of records)**
- Vendor IDs and names
- Purchase transactions
- Item quantities and inventory

✅ **Customer/Sales Data (14% of records)**
- Customer IDs
- Sales transactions
- Discounts (30% of sales have discounts)

✅ **Inventory Data (28% of records)**
- Item codes (ITEM001-ITEM005)
- Quantities
- Beginning/Ending inventory

✅ **Journal Entries (26% manual entries)**
- Entry types (Manual/Automatic)
- Entry timestamps
- User information

## Test Coverage / پوشش آزمون‌ها

These files support testing for:

### 🏦 Banking Tests
- banking_outstanding_checks_test.py
- banking_transparency_test.py
- banking_weekend_transactions_test.py
- banking_unmatched_transfers_test.py

### 💰 Payroll Tests
- payroll_ghost_employees_test.py
- payroll_abnormal_salary_test.py
- payroll_excessive_overtime_test.py
- payroll_duplicate_numbers_test.py

### 🛒 Sales Tests
- sales_abnormal_discount_test.py
- sales_customer_employee_test.py
- sales_markup_analysis_test.py
- sales_pareto_analysis_test.py

### 📦 Inventory Tests
- reconciliation_inventory_consumption_test.py
- inventory_slow_moving_test.py

### 📝 Journal Tests
- journal_manual_entries_test.py
- journal_unsupported_entries_test.py
- journal_period_end_entries_test.py

### 📊 Statistical Tests
- benford_first_digit_test.py
- statistical_zscore_test.py
- statistical_iqr_test.py
- And many more...

## How to Use / نحوه استفاده

### Option 1: Use Templates / استفاده از قالب‌ها

1. Open a template file in Excel
2. Fill in your data starting from row 3
3. Row 1 has English column names
4. Row 2 has Persian column names
5. Save and import into the system

### Option 2: Use Sample Data / استفاده از داده‌های نمونه

1. Use sample data files directly for testing
2. Modify as needed
3. Import into database or web interface
4. Run tests to verify functionality

### Option 3: Regenerate Files / ایجاد مجدد فایل‌ها

```bash
python generate_excel_templates.py
```

This will recreate all files with fresh data.

## File Sizes / حجم فایل‌ها

| File | Size | Records |
|------|------|---------|
| Transactions_SampleData.xlsx | ~93 KB | 500 |
| PayrollTransactions_SampleData.xlsx | ~15 KB | 100 |
| SalesTransactions_SampleData.xlsx | ~13 KB | 120 |
| InventoryIssues_SampleData.xlsx | ~11 KB | 80 |
| CheckPayables_SampleData.xlsx | ~8 KB | 50 |
| **Total** | **~140 KB** | **850** |

## Technical Details / جزئیات فنی

### Template Structure
- Row 1: English column headers
- Row 2: Persian column headers (فارسی)
- Row 3+: Data entry area
- Styled headers: Blue background, white bold text
- Auto-adjusted column widths

### Data Formats
- Dates: YYYY-MM-DD format
- DateTime: YYYY-MM-DD HH:MM:SS format
- Boolean: "True" or "False" strings
- Numbers: Decimal format
- Currency: Iranian Rials

### Data Quality
- Realistic transaction amounts
- Proper date ranges (2024)
- Valid account codes
- Consistent referential integrity
- Mixed manual and automatic entries

## Next Steps / مراحل بعدی

1. ✅ Excel templates created with bilingual headers
2. ✅ Sample data files generated with realistic test data
3. ⏭️ Import sample data into database
4. ⏭️ Run audit tests with sample data
5. ⏭️ Verify test results are meaningful
6. ⏭️ Customize data for specific test scenarios

## Support / پشتیبانی

For questions or issues:
- See README.md in excel_templates/ directory
- Run `python generate_excel_templates.py --help` (if implemented)
- Check models.py for field definitions

برای سؤالات یا مشکلات:
- README.md در پوشه excel_templates/ را ببینید
- فایل models.py را برای تعریف فیلدها بررسی کنید
- اسکریپت generate_excel_templates.py را مجدداً اجرا کنید
