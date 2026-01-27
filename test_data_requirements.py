"""
Test Data Requirements Configuration
این فایل مشخص می‌کند هر آزمون چه فایل‌های اکسلی نیاز دارد
"""

# تعریف انواع فایل‌های داده
DATA_FILES = {
    'transactions': {
        'file': 'Transactions_SampleData.xlsx',
        'template': 'Transactions_Template.xlsx',
        'description': 'تراکنش‌های مالی عمومی (دفتر روزنامه)',
        'columns': ['تاریخ', 'شماره سند', 'کد حساب', 'بدهکار', 'بستانکار', 'شرح']
    },
    'sales': {
        'file': 'SalesTransactions_SampleData.xlsx',
        'template': 'SalesTransactions_Template.xlsx',
        'description': 'تراکنش‌های فروش',
        'columns': ['تاریخ', 'شماره فاکتور', 'کد مشتری', 'نام مشتری', 'کد کالا', 'نام کالا', 'تعداد', 'قیمت واحد', 'تخفیف', 'مبلغ کل']
    },
    'inventory': {
        'file': 'InventoryIssues_SampleData.xlsx',
        'template': 'InventoryIssues_Template.xlsx',
        'description': 'حرکات موجودی انبار',
        'columns': ['تاریخ', 'کد کالا', 'نام کالا', 'تعداد', 'قیمت واحد', 'مبلغ کل', 'نوع حرکت']
    },
    'payroll': {
        'file': 'PayrollTransactions_SampleData.xlsx',
        'template': 'PayrollTransactions_Template.xlsx',
        'description': 'لیست حقوق و دستمزد',
        'columns': ['ماه', 'کد پرسنلی', 'نام', 'حقوق پایه', 'اضافه کار', 'پاداش', 'کسورات', 'خالص پرداختی']
    },
    'checks': {
        'file': 'CheckPayables_SampleData.xlsx',
        'template': 'CheckPayables_Template.xlsx',
        'description': 'چک‌های پرداختی/دریافتی',
        'columns': ['تاریخ صدور', 'تاریخ سررسید', 'شماره چک', 'بانک', 'مبلغ', 'دریافت کننده', 'وضعیت']
    }
}

# تعریف نیازمندی داده برای هر آزمون
TEST_DATA_REQUIREMENTS = {
    # آزمون‌های بنفورد
    'benford_first_digit_test': {
        'required_files': ['transactions'],
        'description': 'آزمون رقم اول بنفورد روی تراکنش‌های مالی'
    },
    'benford_first_two_digits_test': {
        'required_files': ['transactions'],
        'description': 'آزمون دو رقم اول بنفورد'
    },
    'benford_last_two_digits_test': {
        'required_files': ['transactions'],
        'description': 'آزمون دو رقم آخر بنفورد'
    },
    'benford_difference_test': {
        'required_files': ['transactions'],
        'description': 'آزمون تفاضل بنفورد'
    },
    
    # آزمون‌های آستانه
    'variance_threshold_test': {
        'required_files': ['transactions'],
        'description': 'تحلیل آستانه واریانس - تراکنش‌های با انحراف قابل تنظیم از میانگین'
    },
    'statistical_upper_limit_test': {
        'required_files': ['transactions'],
        'description': 'حد بالای آماری - تراکنش‌های بالاتر از حد آماری'
    },
    'high_value_transaction_test': {
        'required_files': ['transactions'],
        'description': 'تحلیل تراکنش‌های با ارزش بالا - شناسایی تراکنش‌های غیرمعمول'
    },
    
    # آزمون‌های تکراری
    'duplicate_transaction_test': {
        'required_files': ['transactions'],
        'description': 'تراکنش‌های تکراری در دفتر روزنامه'
    },
    'duplicate_check_test': {
        'required_files': ['checks'],
        'description': 'چک‌های تکراری'
    },
    'duplicate_names_test': {
        'required_files': ['payroll'],
        'description': 'نام‌های تکراری در لیست حقوق'
    },
    'duplicate_sales_pattern_test': {
        'required_files': ['sales'],
        'description': 'الگوهای تکراری در فروش'
    },
    
    # آزمون‌های آماری
    'statistical_zscore_test': {
        'required_files': ['transactions'],
        'description': 'تراکنش‌های دارای Z-Score بالا'
    },
    'statistical_iqr_test': {
        'required_files': ['transactions'],
        'description': 'تراکنش‌های خارج از محدوده IQR'
    },
    'statistical_price_volatility_test': {
        'required_files': ['inventory'],
        'description': 'نوسانات قیمت کالاها'
    },
    'statistical_profit_margin_test': {
        'required_files': ['sales'],
        'description': 'نوسانات حاشیه سود'
    },
    
    # آزمون‌های الگوی فصلی
    'seasonal_cash_flow_test': {
        'required_files': ['transactions'],
        'description': 'تحلیل فصلی جریان نقدی - شناسایی الگوهای فصلی در نقدینگی'
    },
    'seasonal_inventory_pattern_test': {
        'required_files': ['inventory'],
        'description': 'تحلیل الگوی فصلی موجودی - شناسایی نوسانات فصلی موجودی'
    },
    'seasonal_sales_pattern_test': {
        'required_files': ['sales'],
        'description': 'تحلیل الگوی فصلی فروش - شناسایی الگوهای فصلی در فروش'
    },
    
    # آزمون‌های تطبیق (نیاز به چند فایل)
    'reconciliation_bank_test': {
        'required_files': ['transactions', 'checks'],
        'description': 'تطبیق بانکی - نیاز به تراکنش‌ها و چک‌ها'
    },
    'reconciliation_payroll_attendance_test': {
        'required_files': ['payroll'],
        'description': 'تطابق حقوق با حضور'
    },
    'reconciliation_customer_confirmation_test': {
        'required_files': ['sales'],
        'description': 'تطابق گزارش مشتریان'
    },
    'reconciliation_inventory_consumption_test': {
        'required_files': ['inventory', 'sales'],
        'description': 'تطابق مصرف موجودی با فروش'
    },
    
    # آزمون‌های صفر
    'zero_three_zeros_test': {
        'required_files': ['transactions'],
        'description': 'اعداد با سه رقم صفر'
    },
    'zero_round_amounts_test': {
        'required_files': ['transactions'],
        'description': 'اعداد گرد'
    },
    'zero_digit_frequency_test': {
        'required_files': ['transactions'],
        'description': 'فراوانی ارقام صفر'
    },
    
    # آزمون‌های موجودی
    'inventory_one_dollar_items_test': {
        'required_files': ['inventory'],
        'description': 'اقلام با قیمت یک ریال'
    },
    'inventory_slow_moving_test': {
        'required_files': ['inventory'],
        'description': 'موجودی راکد'
    },
    'inventory_valuation_test': {
        'required_files': ['inventory'],
        'description': 'ارزیابی موجودی'
    },
    'inventory_price_frequency_test': {
        'required_files': ['inventory'],
        'description': 'فراوانی نرخ‌های خرید'
    },
    
    # آزمون‌های فروش
    'sales_abnormal_discount_test': {
        'required_files': ['sales'],
        'description': 'تخفیفات غیرمعمول'
    },
    'sales_markup_analysis_test': {
        'required_files': ['sales'],
        'description': 'تحلیل نرخ سود'
    },
    'sales_customer_employee_test': {
        'required_files': ['sales', 'payroll'],
        'description': 'مطابقت مشتریان با کارکنان'
    },
    'sales_pareto_analysis_test': {
        'required_files': ['sales'],
        'description': 'تحلیل پارتو فروش'
    },
    
    # آزمون‌های حقوق
    'payroll_abnormal_salary_test': {
        'required_files': ['payroll'],
        'description': 'حقوق‌های غیرمعمول'
    },
    'payroll_excessive_overtime_test': {
        'required_files': ['payroll'],
        'description': 'ساعات اضافه کار بیش از حد'
    },
    'payroll_ghost_employees_test': {
        'required_files': ['payroll'],
        'description': 'کارکنان جدید و منصرف شده'
    },
    'payroll_duplicate_numbers_test': {
        'required_files': ['payroll'],
        'description': 'شماره پرسنلی تکراری'
    },
    
    # آزمون‌های بانک
    'banking_outstanding_checks_test': {
        'required_files': ['checks'],
        'description': 'چک‌های معلق'
    },
    'banking_unmatched_transfers_test': {
        'required_files': ['transactions'],
        'description': 'انتقالات بدون تطبیق'
    },
    'banking_weekend_transactions_test': {
        'required_files': ['transactions'],
        'description': 'تراکنش‌های آخر هفته'
    },
    'banking_transparency_test': {
        'required_files': ['transactions'],
        'description': 'شفافیت بانکی'
    },
    
    # آزمون‌های دفتر روزنامه
    'journal_manual_entries_test': {
        'required_files': ['transactions'],
        'description': 'ثبت‌های دستی'
    },
    'journal_unsupported_entries_test': {
        'required_files': ['transactions'],
        'description': 'ثبت‌های بدون سند'
    },
    'journal_period_end_entries_test': {
        'required_files': ['transactions'],
        'description': 'ثبت‌های آخر دوره'
    },
    'journal_unusual_combinations_test': {
        'required_files': ['transactions'],
        'description': 'ترکیب‌های نامعمول حساب‌ها'
    },
    
    # آزمون‌های کیفیت داده
    'data_quality_missing_data_test': {
        'required_files': ['transactions'],
        'description': 'داده‌های خالی یا ناقص'
    },
    'data_quality_reasonableness_test': {
        'required_files': ['transactions'],
        'description': 'داده‌های غیرمعقول'
    },
    'data_quality_data_type_test': {
        'required_files': ['transactions'],
        'description': 'بررسی نوع داده‌ها'
    },
    
    # آزمون‌های پیشرفته
    'advanced_shell_company_test': {
        'required_files': ['transactions', 'sales'],
        'description': 'تشخیص شرکت‌های کاغذی'
    },
    'advanced_sequential_audit_test': {
        'required_files': ['transactions'],
        'description': 'بررسی ترتیب شماره اسناد'
    },
    'advanced_network_analysis_test': {
        'required_files': ['transactions'],
        'description': 'تحلیل شبکه تراکنش‌ها'
    },
    
    # آزمون‌های تقلب
    'fraud_kiting_test': {
        'required_files': ['checks', 'transactions'],
        'description': 'تشخیص Kiting'
    },
    'fraud_lapping_test': {
        'required_files': ['transactions'],
        'description': 'تشخیص Lapping'
    },
    'fraud_skimming_test': {
        'required_files': ['transactions', 'sales'],
        'description': 'تشخیص Skimming'
    },
    
    # آزمون‌های ناهنجاری
    'anomaly_gap_analysis_test': {
        'required_files': ['transactions'],
        'description': 'تحلیل فاصله‌ها در شماره اسناد'
    },
    'anomaly_spike_detection_test': {
        'required_files': ['transactions'],
        'description': 'تشخیص رشد ناگهانی'
    },
    
    # آزمون‌های روند
    'trend_seasonal_variance_test': {
        'required_files': ['sales'],
        'description': 'واریانس فصلی'
    },
    
    # آزمون‌های نسبت مالی
    'ratio_quick_ratio_test': {
        'required_files': ['transactions'],
        'description': 'نسبت آنی'
    },
    'ratio_debt_to_equity_test': {
        'required_files': ['transactions'],
        'description': 'نسبت بدهی به حقوق صاحبان سهام'
    },
    
    # آزمون‌های انطباق
    'compliance_segregation_duties_test': {
        'required_files': ['transactions'],
        'description': 'بررسی تفکیک وظایف'
    },
    
    # آزمون‌های حسابداری
    'accounting_footing_test': {
        'required_files': ['transactions'],
        'description': 'بررسی مجموع ستون‌ها'
    },
    'cutoff_analysis_test': {
        'required_files': ['transactions'],
        'description': 'تحلیل برش (Cutoff)'
    },
    
    # آزمون‌های هوش مصنوعی
    'ai_benford_advanced_test': {
        'required_files': ['transactions'],
        'description': 'بنفورد پیشرفته با ML'
    },
    'ai_contextual_anomaly_test': {
        'required_files': ['transactions'],
        'description': 'ناهنجاری متنی با NLP'
    },
    'ai_isolation_forest_test': {
        'required_files': ['transactions'],
        'description': 'Isolation Forest برای تشخیص ناهنجاری'
    },
    'ai_kmeans_clustering_test': {
        'required_files': ['transactions'],
        'description': 'خوشه‌بندی K-Means'
    },
    
    # آزمون‌های حسابهای دریافتنی
    'ar_confirmation_analysis_test': {
        'required_files': ['sales'],
        'description': 'تحلیل تایید مشتریان'
    },
    
    # آزمون‌های نمونه‌گیری
    'sampling_monetary_unit_test': {
        'required_files': ['transactions'],
        'description': 'نمونه‌گیری واحد پولی'
    },
    'sampling_stratified_test': {
        'required_files': ['transactions'],
        'description': 'نمونه‌گیری طبقه‌بندی شده'
    }
}

def get_test_requirements(test_id: str) -> dict:
    """دریافت نیازمندی‌های داده یک آزمون"""
    if test_id not in TEST_DATA_REQUIREMENTS:
        return {
            'required_files': ['transactions'],
            'description': 'نیازمندی داده مشخص نشده'
        }
    
    req = TEST_DATA_REQUIREMENTS[test_id]
    files_info = []
    
    for file_key in req['required_files']:
        if file_key in DATA_FILES:
            files_info.append(DATA_FILES[file_key])
    
    return {
        'description': req['description'],
        'required_files': req['required_files'],
        'files_info': files_info
    }

def get_all_required_files(test_ids: list) -> list:
    """دریافت تمام فایل‌های مورد نیاز برای لیستی از آزمون‌ها"""
    all_files = set()
    files_detail = []
    file_keys_added = set()
    
    for test_id in test_ids:
        req = get_test_requirements(test_id)
        all_files.update(req['required_files'])
    
    for file_key in all_files:
        if file_key in DATA_FILES and file_key not in file_keys_added:
            files_detail.append(DATA_FILES[file_key]['file'])
            file_keys_added.add(file_key)
    
    return files_detail
