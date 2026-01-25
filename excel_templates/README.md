# Excel Templates and Sample Data
# قالب‌های اکسل و داده‌های نمونه

This directory contains Excel template files and sample data for the audit testing system.
این پوشه شامل فایل‌های قالب اکسل و داده‌های نمونه برای سیستم آزمون حسابرسی است.

## Directory Structure / ساختار پوشه‌ها

```
excel_templates/       - Template files with bilingual headers (English/Persian)
                        فایل‌های قالب با عناوین دو زبانه (انگلیسی/فارسی)

excel_sample_data/     - Sample data files for testing
                        فایل‌های داده نمونه برای آزمایش
```

## Template Files / فایل‌های قالب

Template files contain only column headers in both English and Persian:
فایل‌های قالب فقط شامل عناوین ستون‌ها به دو زبان انگلیسی و فارسی هستند:

### 1. Transactions_Template.xlsx
Main transaction table with all fields including:
- Basic fields: DocumentDate, DocumentNumber, AccountCode, Debit, Credit
- Banking fields: CheckNumber, CheckStatus, AccountNumber, Payee
- Transaction fields: TransactionID, TransactionDate, TransactionType
- Payroll fields: EmployeeID, PayrollAmount
- Vendor fields: VendorID, VendorName
- Customer fields: CustomerID
- Discount fields: OriginalAmount, DiscountAmount
- Inventory fields: ItemID, Quantity, BeginningInventory, EndingInventory
- Journal fields: EntryType, EntryTime, EnteredBy

جدول اصلی تراکنش‌ها با تمام فیلدها شامل:
- فیلدهای پایه: تاریخ سند، شماره سند، کد حساب، بدهکار، بستانکار
- فیلدهای بانکی: شماره چک، وضعیت چک، شماره حساب، دریافت‌کننده
- فیلدهای تراکنش: شناسه تراکنش، تاریخ تراکنش، نوع تراکنش
- فیلدهای حقوق: شناسه کارمند، مبلغ حقوق
- فیلدهای فروشنده: شناسه فروشنده، نام فروشنده
- فیلدهای مشتری: شناسه مشتری
- فیلدهای تخفیف: مبلغ اصلی، مبلغ تخفیف
- فیلدهای موجودی: شناسه کالا، مقدار، موجودی اول دوره، موجودی پایان دوره
- فیلدهای دفتر روزنامه: نوع ثبت، زمان ثبت، ثبت‌کننده

### 2. CheckPayables_Template.xlsx
Payable checks template / قالب چک‌های پرداختنی

### 3. CheckReceivables_Template.xlsx
Receivable checks template / قالب چک‌های دریافتنی

### 4. PayrollTransactions_Template.xlsx
Payroll transactions template / قالب تراکنش‌های حقوق و دستمزد

### 5. InventoryIssues_Template.xlsx
Inventory issues template / قالب حواله‌های انبار

### 6. SalesTransactions_Template.xlsx
Sales transactions template / قالب تراکنش‌های فروش

## Sample Data Files / فایل‌های داده نمونه

Sample data files contain realistic test data for meaningful test execution:
فایل‌های داده نمونه شامل داده‌های واقعی برای اجرای معنادار آزمون‌ها هستند:

### 1. Transactions_SampleData.xlsx (500 records)
- Various transaction types: Purchase, Sale, Payment, Receipt, Payroll, Manual
- Banking transactions with check information
- Payroll transactions with employee data
- Sales transactions with customer and discount data
- Inventory transactions with item data
- Manual journal entries with entry metadata

انواع مختلف تراکنش: خرید، فروش، پرداخت، دریافت، حقوق، دستی
- تراکنش‌های بانکی با اطلاعات چک
- تراکنش‌های حقوق با داده‌های کارمند
- تراکنش‌های فروش با داده‌های مشتری و تخفیف
- تراکنش‌های موجودی با داده‌های کالا
- ثبت‌های دستی دفتر روزنامه با متادیتا

### 2. CheckPayables_SampleData.xlsx (50 records)
Sample payable checks data / داده‌های نمونه چک‌های پرداختنی

### 3. PayrollTransactions_SampleData.xlsx (100 records)
Sample payroll data with overtime, deductions, etc.
داده‌های نمونه حقوق با اضافه‌کار، کسورات و غیره

### 4. InventoryIssues_SampleData.xlsx (80 records)
Sample inventory issue transactions / تراکنش‌های نمونه حواله انبار

### 5. SalesTransactions_SampleData.xlsx (120 records)
Sample sales transactions / تراکنش‌های نمونه فروش

## Usage / نحوه استفاده

### Using Templates / استفاده از قالب‌ها

1. Open a template file in Excel
2. Fill in data starting from row 3 (rows 1-2 are headers)
3. Save and import into the system

1. فایل قالب را در اکسل باز کنید
2. داده‌ها را از ردیف 3 شروع کنید (ردیف‌های 1-2 عناوین هستند)
3. ذخیره کنید و به سیستم وارد کنید

### Using Sample Data / استفاده از داده‌های نمونه

1. Use sample data files directly for testing
2. Modify the data as needed
3. Import into the database or web interface

1. از فایل‌های داده نمونه مستقیماً برای آزمایش استفاده کنید
2. داده‌ها را در صورت نیاز تغییر دهید
3. به پایگاه داده یا رابط وب وارد کنید

## Regenerating Files / ایجاد مجدد فایل‌ها

To regenerate these files, run:
برای ایجاد مجدد این فایل‌ها، اجرا کنید:

```bash
python generate_excel_templates.py
```

This will recreate all template and sample data files.
این دستور تمام فایل‌های قالب و داده نمونه را مجدداً ایجاد می‌کند.

## Notes / نکات

- All template files have bilingual headers (English row 1, Persian row 2)
- Sample data includes various scenarios for comprehensive testing
- Date format: YYYY-MM-DD
- Boolean values: "True" or "False"
- All monetary amounts are in Rials

- تمام فایل‌های قالب دارای عناوین دو زبانه هستند (ردیف 1 انگلیسی، ردیف 2 فارسی)
- داده‌های نمونه شامل سناریوهای مختلف برای آزمون جامع است
- فرمت تاریخ: YYYY-MM-DD
- مقادیر بولی: "True" یا "False"
- تمام مبالغ پولی به ریال است

## Test Coverage / پوشش آزمون‌ها

The sample data is designed to test:
- Banking tests (outstanding checks, weekend transactions)
- Payroll tests (ghost employees, abnormal salary, overtime)
- Sales tests (abnormal discounts, customer analysis)
- Inventory tests (consumption, slow-moving items)
- Journal tests (manual entries, unsupported entries)
- Statistical tests (Benford's law, Z-score, IQR)
- Fraud detection tests (kiting, shell companies)
- And many more...

داده‌های نمونه برای آزمون موارد زیر طراحی شده است:
- آزمون‌های بانکی (چک‌های معلق، تراکنش‌های آخر هفته)
- آزمون‌های حقوق (کارکنان ارواح، حقوق غیرعادی، اضافه‌کار)
- آزمون‌های فروش (تخفیفات نجومی، تحلیل مشتری)
- آزمون‌های موجودی (مصرف، اقلام کند رو)
- آزمون‌های دفتر روزنامه (ثبت‌های دستی، ثبت‌های بدون پشتوانه)
- آزمون‌های آماری (قانون بنفورد، Z-score، IQR)
- آزمون‌های تشخیص تقلب (کایتینگ، شرکت‌های کاغذی)
- و موارد دیگر...
