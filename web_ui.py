"""
رابط کاربری وب برای آزمون‌های حسابرسی
Audit Tests Web UI

این فایل یک رابط کاربری وب با Flask ایجاد می‌کند که:
- فایل اکسل را دریافت می‌کند
- داده‌ها را به دیتابیس SQL Server وارد می‌کند
- آزمون‌های حسابرسی را اجرا می‌کند
- نتایج را نمایش می‌دهد
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import pandas as pd
import os
import importlib
import sys
from typing import Dict, List, Any
from datetime import datetime
import json
from pathlib import Path
import traceback

# اضافه کردن مسیر پروژه به sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database import get_db, Base, db
from models import Transaction
from sqlalchemy.orm import sessionmaker
from test_data_requirements import get_test_requirements, get_all_required_files

# ایجاد session factory برای write operations
def get_write_session():
    """Get a writable session for data uploads"""
    if not db._initialized:
        db._initialize()
    if db.SessionLocal is None:
        raise Exception("Database not initialized")
    return db.SessionLocal()


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# ایجاد پوشه uploads
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# لیست تمام آزمون‌های موجود
AUDIT_TESTS = {
    'benford': {
        'name': 'آزمون‌های قانون بنفورد',
        'tests': [
            {'id': 'benford_first_digit_test', 'name': 'آزمون رقم اول بنفورد', 'icon': '1️⃣'},
            {'id': 'benford_first_two_digits_test', 'name': 'آزمون دو رقم اول بنفورد', 'icon': '🔢'},
            {'id': 'benford_last_two_digits_test', 'name': 'آزمون رقم آخر بنفورد', 'icon': '🔚'},
            {'id': 'benford_difference_test', 'name': 'آزمون تفاضل بنفورد', 'icon': '➖'},
        ]
    },
    'threshold': {
        'name': 'آزمون‌های آستانه',
        'tests': [
            {'id': 'variance_threshold_test', 'name': 'تحلیل آستانه واریانس', 'icon': '📈'},
            {'id': 'statistical_upper_limit_test', 'name': 'حد بالای آماری', 'icon': '📏'},
            {'id': 'high_value_transaction_test', 'name': 'تحلیل تراکنش‌های با ارزش بالا', 'icon': '✖️'},
        ]
    },
    'duplicate': {
        'name': 'آزمون‌های تکراری',
        'tests': [
            {'id': 'duplicate_transaction_test', 'name': 'تراکنش‌های تکراری', 'icon': '🔄'},
            {'id': 'duplicate_check_test', 'name': 'چک‌های تکراری', 'icon': '✅'},
            {'id': 'duplicate_names_test', 'name': 'نام‌های تکراری', 'icon': '👥'},
            {'id': 'duplicate_sales_pattern_test', 'name': 'فروش‌های تکراری', 'icon': '💰'},
        ]
    },
    'statistical': {
        'name': 'آزمون‌های آماری',
        'tests': [
            {'id': 'statistical_zscore_test', 'name': 'آزمون Z-Score', 'icon': '📐'},
            {'id': 'statistical_iqr_test', 'name': 'آزمون IQR', 'icon': '📦'},
            {'id': 'statistical_price_volatility_test', 'name': 'نوسانات نرخ خرید', 'icon': '📉'},
            {'id': 'statistical_profit_margin_test', 'name': 'نوسانات حاشیه سود', 'icon': '💹'},
        ]
    },
    'seasonal': {
        'name': 'آزمون‌های الگوی فصلی',
        'tests': [
            {'id': 'seasonal_cash_flow_test', 'name': 'تحلیل فصلی جریان نقدی', 'icon': '💵'},
            {'id': 'seasonal_inventory_pattern_test', 'name': 'تحلیل الگوی فصلی موجودی', 'icon': '📦'},
            {'id': 'seasonal_sales_pattern_test', 'name': 'تحلیل الگوی فصلی فروش', 'icon': '🛒'},
        ]
    },
    'reconciliation': {
        'name': 'آزمون‌های مطابقت',
        'tests': [
            {'id': 'reconciliation_bank_test', 'name': 'تطبیق بانکی', 'icon': '🏦'},
            {'id': 'reconciliation_payroll_attendance_test', 'name': 'تطابق حقوق و حضور', 'icon': '👔'},
            {'id': 'reconciliation_customer_confirmation_test', 'name': 'تطابق گزارش مشتری', 'icon': '📋'},
            {'id': 'reconciliation_inventory_consumption_test', 'name': 'تطابق مصرف موجودی', 'icon': '📊'},
        ]
    },
    'zero': {
        'name': 'آزمون‌های صفرها',
        'tests': [
            {'id': 'zero_three_zeros_test', 'name': 'سه رقم صفر', 'icon': '000'},
            {'id': 'zero_round_amounts_test', 'name': 'اعداد گرد', 'icon': '🔵'},
            {'id': 'zero_digit_frequency_test', 'name': 'فراوانی ارقام صفر', 'icon': '0️⃣'},
        ]
    },
    'inventory': {
        'name': 'آزمون‌های موجودی',
        'tests': [
            {'id': 'inventory_one_dollar_items_test', 'name': 'اقلام یک‌ریالی', 'icon': '💲'},
            {'id': 'inventory_slow_moving_test', 'name': 'موجودی راکد', 'icon': '🐌'},
            {'id': 'inventory_valuation_test', 'name': 'ارزیابی موجودی', 'icon': '💰'},
            {'id': 'inventory_price_frequency_test', 'name': 'فراوانی نرخ خرید', 'icon': '📊'},
        ]
    },
    'sales': {
        'name': 'آزمون‌های فروش',
        'tests': [
            {'id': 'sales_abnormal_discount_test', 'name': 'تخفیفات نجومی', 'icon': '🎫'},
            {'id': 'sales_markup_analysis_test', 'name': 'نرخ سود', 'icon': '💹'},
            {'id': 'sales_customer_employee_test', 'name': 'مطابقت مشتریان با کارکنان', 'icon': '🤝'},
            {'id': 'sales_pareto_analysis_test', 'name': 'توزیع فروش (پارتو)', 'icon': '📈'},
        ]
    },
    'payroll': {
        'name': 'آزمون‌های حقوق',
        'tests': [
            {'id': 'payroll_abnormal_salary_test', 'name': 'حقوق نجومی', 'icon': '💰'},
            {'id': 'payroll_excessive_overtime_test', 'name': 'ساعات اضافی بالا', 'icon': '⏰'},
            {'id': 'payroll_ghost_employees_test', 'name': 'کارکنان جدید و منصرف‌شده', 'icon': '👻'},
            {'id': 'payroll_duplicate_numbers_test', 'name': 'ارقام تکراری', 'icon': '🔢'},
        ]
    },
    'banking': {
        'name': 'آزمون‌های بانک',
        'tests': [
            {'id': 'banking_outstanding_checks_test', 'name': 'چک‌های معلق', 'icon': '✅'},
            {'id': 'banking_unmatched_transfers_test', 'name': 'انتقالات بدون تطبیق', 'icon': '↔️'},
            {'id': 'banking_weekend_transactions_test', 'name': 'تراکنش‌های آخر هفته', 'icon': '📅'},
            {'id': 'banking_transparency_test', 'name': 'شفافیت بانکی', 'icon': '🔍'},
        ]
    },
    'journal': {
        'name': 'آزمون‌های دفتر روزنامه',
        'tests': [
            {'id': 'journal_manual_entries_test', 'name': 'ثبت‌های دستی', 'icon': '✍️'},
            {'id': 'journal_unsupported_entries_test', 'name': 'ثبت‌های بدون سند', 'icon': '❌'},
            {'id': 'journal_period_end_entries_test', 'name': 'ثبت‌های آخر دوره', 'icon': '📆'},
            {'id': 'journal_unusual_combinations_test', 'name': 'ترکیب‌های نامعمول', 'icon': '🔀'},
        ]
    },
    'data_quality': {
        'name': 'آزمون‌های سلامت داده',
        'tests': [
            {'id': 'data_quality_missing_data_test', 'name': 'داده‌های خالی', 'icon': '⚠️'},
            {'id': 'data_quality_reasonableness_test', 'name': 'داده‌های غیرمعقول', 'icon': '❓'},
            {'id': 'data_quality_data_type_test', 'name': 'نوع داده', 'icon': '🔤'},
        ]
    },
    'advanced': {
        'name': 'آزمون‌های پیشرفته',
        'tests': [
            {'id': 'advanced_shell_company_test', 'name': 'شرکت کاغذی', 'icon': '🏢'},
            {'id': 'advanced_sequential_audit_test', 'name': 'ترتیب تراکنش', 'icon': '🔢'},
            {'id': 'advanced_network_analysis_test', 'name': 'تحلیل شبکه', 'icon': '🕸️'},
        ]
    },
    'fraud': {
        'name': 'آزمون‌های تقلب',
        'tests': [
            {'id': 'fraud_kiting_test', 'name': 'آزمون Kiting', 'icon': '🪁'},
            {'id': 'fraud_lapping_test', 'name': 'آزمون Lapping', 'icon': '🔄'},
            {'id': 'fraud_skimming_test', 'name': 'آزمون Skimming', 'icon': '💳'},
        ]
    },
    'anomaly': {
        'name': 'آزمون‌های ناهنجاری',
        'tests': [
            {'id': 'anomaly_gap_analysis_test', 'name': 'تحلیل فاصله‌ها', 'icon': '📊'},
            {'id': 'anomaly_spike_detection_test', 'name': 'تشخیص رشد ناگهانی', 'icon': '📈'},
        ]
    },
    'trend': {
        'name': 'آزمون‌های روند',
        'tests': [
            {'id': 'trend_seasonal_variance_test', 'name': 'واریانس فصلی', 'icon': '🌦️'},
        ]
    },
    'ratio': {
        'name': 'آزمون‌های نسبت مالی',
        'tests': [
            {'id': 'ratio_quick_ratio_test', 'name': 'نسبت آنی', 'icon': '⚡'},
            {'id': 'ratio_debt_to_equity_test', 'name': 'نسبت بدهی به حقوق', 'icon': '⚖️'},
        ]
    },
    'compliance': {
        'name': 'آزمون‌های انطباق',
        'tests': [
            {'id': 'compliance_segregation_duties_test', 'name': 'تفکیک وظایف', 'icon': '👥'},
        ]
    },
    'accounting': {
        'name': 'آزمون‌های حسابداری',
        'tests': [
            {'id': 'accounting_footing_test', 'name': 'آزمون مجموع', 'icon': '➕'},
            {'id': 'cutoff_analysis_test', 'name': 'تحلیل برش', 'icon': '✂️'},
        ]
    },
    'ai': {
        'name': 'آزمون‌های هوش مصنوعی',
        'tests': [
            {'id': 'ai_benford_advanced_test', 'name': 'بنفورد پیشرفته', 'icon': '🤖'},
            {'id': 'ai_contextual_anomaly_test', 'name': 'ناهنجاری متنی', 'icon': '🔍'},
            {'id': 'ai_isolation_forest_test', 'name': 'جنگل ایزوله', 'icon': '🌲'},
            {'id': 'ai_kmeans_clustering_test', 'name': 'خوشه‌بندی K-Means', 'icon': '🎯'},
        ]
    },
    'ar': {
        'name': 'آزمون‌های حسابهای دریافتنی',
        'tests': [
            {'id': 'ar_confirmation_analysis_test', 'name': 'تحلیل تایید مشتریان', 'icon': '✉️'},
        ]
    },
    'sampling': {
        'name': 'آزمون‌های نمونه‌گیری',
        'tests': [
            {'id': 'sampling_monetary_unit_test', 'name': 'نمونه‌گیری واحد پولی', 'icon': '💵'},
            {'id': 'sampling_stratified_test', 'name': 'نمونه‌گیری طبقه‌بندی شده', 'icon': '📊'},
        ]
    }
}

# نگاشت آزمون‌ها به زیرسیستم‌های حسابداری
# هر آزمون می‌تواند در چندین زیرسیستم قابل اجرا باشد
SUBSYSTEM_MAPPING = {
    'cash_and_bank': {
        'name': 'نقد و بانک',
        'icon': '🏦',
        'tests': [
            # Benford - applicable to cash transactions
            'benford_first_digit_test', 'benford_first_two_digits_test', 
            'benford_last_two_digits_test', 'benford_difference_test',
            # Threshold - applicable to cash amounts
            'variance_threshold_test', 'statistical_upper_limit_test', 'high_value_transaction_test',
            # Duplicate - check for duplicate transactions
            'duplicate_transaction_test', 'duplicate_check_test',
            # Statistical - cash flow analysis
            'statistical_zscore_test', 'statistical_iqr_test',
            # Seasonal - cash flow patterns
            'seasonal_cash_flow_test',
            # Reconciliation - bank reconciliation
            'reconciliation_bank_test',
            # Zero tests - applicable to cash amounts
            'zero_three_zeros_test', 'zero_round_amounts_test', 'zero_digit_frequency_test',
            # Banking specific
            'banking_outstanding_checks_test', 'banking_unmatched_transfers_test',
            'banking_weekend_transactions_test', 'banking_transparency_test',
            # Journal entries
            'journal_manual_entries_test', 'journal_unsupported_entries_test',
            'journal_period_end_entries_test', 'journal_unusual_combinations_test',
            # Data quality
            'data_quality_missing_data_test', 'data_quality_reasonableness_test', 'data_quality_data_type_test',
            # Advanced
            'advanced_sequential_audit_test', 'advanced_network_analysis_test',
            # Fraud
            'fraud_kiting_test', 'fraud_lapping_test',
            # Anomaly
            'anomaly_gap_analysis_test', 'anomaly_spike_detection_test',
            # Trend
            'trend_seasonal_variance_test',
            # Accounting
            'accounting_footing_test', 'cutoff_analysis_test',
            # AI
            'ai_benford_advanced_test', 'ai_contextual_anomaly_test',
            'ai_isolation_forest_test', 'ai_kmeans_clustering_test',
            # Sampling
            'sampling_monetary_unit_test', 'sampling_stratified_test',
        ]
    },
    'inventory': {
        'name': 'انبار',
        'icon': '📦',
        'tests': [
            # Benford - applicable to inventory values
            'benford_first_digit_test', 'benford_first_two_digits_test',
            'benford_last_two_digits_test', 'benford_difference_test',
            # Threshold
            'variance_threshold_test', 'statistical_upper_limit_test', 'high_value_transaction_test',
            # Duplicate
            'duplicate_transaction_test', 'duplicate_names_test',
            # Statistical - price volatility
            'statistical_zscore_test', 'statistical_iqr_test',
            'statistical_price_volatility_test',
            # Seasonal - inventory patterns
            'seasonal_inventory_pattern_test',
            # Reconciliation - inventory consumption
            'reconciliation_inventory_consumption_test',
            # Zero tests
            'zero_three_zeros_test', 'zero_round_amounts_test', 'zero_digit_frequency_test',
            # Inventory specific
            'inventory_one_dollar_items_test', 'inventory_slow_moving_test',
            'inventory_valuation_test', 'inventory_price_frequency_test',
            # Journal
            'journal_manual_entries_test', 'journal_unsupported_entries_test',
            'journal_period_end_entries_test', 'journal_unusual_combinations_test',
            # Data quality
            'data_quality_missing_data_test', 'data_quality_reasonableness_test', 'data_quality_data_type_test',
            # Advanced
            'advanced_sequential_audit_test', 'advanced_network_analysis_test', 'advanced_shell_company_test',
            # Anomaly
            'anomaly_gap_analysis_test', 'anomaly_spike_detection_test',
            # Trend
            'trend_seasonal_variance_test',
            # Accounting
            'accounting_footing_test', 'cutoff_analysis_test',
            # AI
            'ai_benford_advanced_test', 'ai_contextual_anomaly_test',
            'ai_isolation_forest_test', 'ai_kmeans_clustering_test',
            # Sampling
            'sampling_monetary_unit_test', 'sampling_stratified_test',
        ]
    },
    'payroll': {
        'name': 'حقوق و دستمزد',
        'icon': '👔',
        'tests': [
            # Benford - applicable to salary amounts
            'benford_first_digit_test', 'benford_first_two_digits_test',
            'benford_last_two_digits_test', 'benford_difference_test',
            # Threshold
            'variance_threshold_test', 'statistical_upper_limit_test', 'high_value_transaction_test',
            # Duplicate
            'duplicate_transaction_test', 'duplicate_names_test',
            # Statistical
            'statistical_zscore_test', 'statistical_iqr_test',
            # Reconciliation - payroll and attendance
            'reconciliation_payroll_attendance_test',
            # Zero tests
            'zero_three_zeros_test', 'zero_round_amounts_test', 'zero_digit_frequency_test',
            # Payroll specific
            'payroll_abnormal_salary_test', 'payroll_excessive_overtime_test',
            'payroll_ghost_employees_test', 'payroll_duplicate_numbers_test',
            # Journal
            'journal_manual_entries_test', 'journal_unsupported_entries_test',
            'journal_period_end_entries_test', 'journal_unusual_combinations_test',
            # Data quality
            'data_quality_missing_data_test', 'data_quality_reasonableness_test', 'data_quality_data_type_test',
            # Advanced
            'advanced_sequential_audit_test', 'advanced_network_analysis_test', 'advanced_shell_company_test',
            # Fraud
            'fraud_lapping_test',
            # Anomaly
            'anomaly_gap_analysis_test', 'anomaly_spike_detection_test',
            # Trend
            'trend_seasonal_variance_test',
            # Compliance
            'compliance_segregation_duties_test',
            # Accounting
            'accounting_footing_test', 'cutoff_analysis_test',
            # AI
            'ai_benford_advanced_test', 'ai_contextual_anomaly_test',
            'ai_isolation_forest_test', 'ai_kmeans_clustering_test',
            # Sampling
            'sampling_monetary_unit_test', 'sampling_stratified_test',
        ]
    },
    'sales': {
        'name': 'فروش',
        'icon': '🛒',
        'tests': [
            # Benford - applicable to sales amounts
            'benford_first_digit_test', 'benford_first_two_digits_test',
            'benford_last_two_digits_test', 'benford_difference_test',
            # Threshold
            'variance_threshold_test', 'statistical_upper_limit_test', 'high_value_transaction_test',
            # Duplicate
            'duplicate_transaction_test', 'duplicate_names_test', 'duplicate_sales_pattern_test',
            # Statistical - profit margin
            'statistical_zscore_test', 'statistical_iqr_test',
            'statistical_profit_margin_test',
            # Seasonal - sales patterns
            'seasonal_sales_pattern_test',
            # Reconciliation - customer confirmation
            'reconciliation_customer_confirmation_test',
            # Zero tests
            'zero_three_zeros_test', 'zero_round_amounts_test', 'zero_digit_frequency_test',
            # Sales specific
            'sales_abnormal_discount_test', 'sales_markup_analysis_test',
            'sales_customer_employee_test', 'sales_pareto_analysis_test',
            # Journal
            'journal_manual_entries_test', 'journal_unsupported_entries_test',
            'journal_period_end_entries_test', 'journal_unusual_combinations_test',
            # Data quality
            'data_quality_missing_data_test', 'data_quality_reasonableness_test', 'data_quality_data_type_test',
            # Advanced
            'advanced_sequential_audit_test', 'advanced_network_analysis_test', 'advanced_shell_company_test',
            # Fraud
            'fraud_skimming_test', 'fraud_lapping_test',
            # Anomaly
            'anomaly_gap_analysis_test', 'anomaly_spike_detection_test',
            # Trend
            'trend_seasonal_variance_test',
            # Ratio
            'ratio_quick_ratio_test',
            # Accounting
            'accounting_footing_test', 'cutoff_analysis_test',
            # AI
            'ai_benford_advanced_test', 'ai_contextual_anomaly_test',
            'ai_isolation_forest_test', 'ai_kmeans_clustering_test',
            # AR
            'ar_confirmation_analysis_test',
            # Sampling
            'sampling_monetary_unit_test', 'sampling_stratified_test',
        ]
    },
    'fixed_assets': {
        'name': 'دارایی ثابت',
        'icon': '🏢',
        'tests': [
            # Benford - applicable to asset values
            'benford_first_digit_test', 'benford_first_two_digits_test',
            'benford_last_two_digits_test', 'benford_difference_test',
            # Threshold
            'variance_threshold_test', 'statistical_upper_limit_test', 'high_value_transaction_test',
            # Duplicate
            'duplicate_transaction_test', 'duplicate_names_test',
            # Statistical
            'statistical_zscore_test', 'statistical_iqr_test',
            # Zero tests
            'zero_three_zeros_test', 'zero_round_amounts_test', 'zero_digit_frequency_test',
            # Inventory tests (asset valuation)
            'inventory_one_dollar_items_test', 'inventory_valuation_test',
            # Journal
            'journal_manual_entries_test', 'journal_unsupported_entries_test',
            'journal_period_end_entries_test', 'journal_unusual_combinations_test',
            # Data quality
            'data_quality_missing_data_test', 'data_quality_reasonableness_test', 'data_quality_data_type_test',
            # Advanced
            'advanced_sequential_audit_test', 'advanced_shell_company_test',
            # Anomaly
            'anomaly_gap_analysis_test', 'anomaly_spike_detection_test',
            # Trend
            'trend_seasonal_variance_test',
            # Ratio
            'ratio_debt_to_equity_test',
            # Compliance
            'compliance_segregation_duties_test',
            # Accounting
            'accounting_footing_test', 'cutoff_analysis_test',
            # AI
            'ai_benford_advanced_test', 'ai_contextual_anomaly_test',
            'ai_isolation_forest_test', 'ai_kmeans_clustering_test',
            # Sampling
            'sampling_monetary_unit_test', 'sampling_stratified_test',
        ]
    },
    'procurement': {
        'name': 'تدارکات',
        'icon': '🛍️',
        'tests': [
            # Benford - applicable to purchase amounts
            'benford_first_digit_test', 'benford_first_two_digits_test',
            'benford_last_two_digits_test', 'benford_difference_test',
            # Threshold
            'variance_threshold_test', 'statistical_upper_limit_test', 'high_value_transaction_test',
            # Duplicate
            'duplicate_transaction_test', 'duplicate_names_test',
            # Statistical - price volatility
            'statistical_zscore_test', 'statistical_iqr_test',
            'statistical_price_volatility_test',
            # Zero tests
            'zero_three_zeros_test', 'zero_round_amounts_test', 'zero_digit_frequency_test',
            # Inventory related (procurement affects inventory)
            'inventory_one_dollar_items_test', 'inventory_price_frequency_test',
            # Journal
            'journal_manual_entries_test', 'journal_unsupported_entries_test',
            'journal_period_end_entries_test', 'journal_unusual_combinations_test',
            # Data quality
            'data_quality_missing_data_test', 'data_quality_reasonableness_test', 'data_quality_data_type_test',
            # Advanced
            'advanced_sequential_audit_test', 'advanced_network_analysis_test', 'advanced_shell_company_test',
            # Fraud
            'fraud_skimming_test',
            # Anomaly
            'anomaly_gap_analysis_test', 'anomaly_spike_detection_test',
            # Trend
            'trend_seasonal_variance_test',
            # Compliance
            'compliance_segregation_duties_test',
            # Accounting
            'accounting_footing_test', 'cutoff_analysis_test',
            # AI
            'ai_benford_advanced_test', 'ai_contextual_anomaly_test',
            'ai_isolation_forest_test', 'ai_kmeans_clustering_test',
            # Sampling
            'sampling_monetary_unit_test', 'sampling_stratified_test',
        ]
    }
}


@app.route('/')
def index():
    """صفحه اصلی"""
    # Build subsystems with full test details
    subsystems = {}
    for subsystem_id, subsystem_info in SUBSYSTEM_MAPPING.items():
        subsystems[subsystem_id] = {
            'name': subsystem_info['name'],
            'icon': subsystem_info['icon'],
            'tests': []
        }
        
        # Find full test details for each test_id
        for test_id in subsystem_info['tests']:
            # Search through all categories to find the test
            for category_id, category in AUDIT_TESTS.items():
                for test in category['tests']:
                    if test['id'] == test_id:
                        subsystems[subsystem_id]['tests'].append(test)
                        break
    
    return render_template('index.html', 
                         audit_tests=AUDIT_TESTS, 
                         subsystems=subsystems)


@app.route('/test-requirements/<test_id>')
def get_test_requirements_api(test_id):
    """دریافت نیازمندی‌های داده یک آزمون"""
    try:
        requirements = get_test_requirements(test_id)
        return jsonify({'success': True, 'requirements': requirements})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/tests-requirements', methods=['POST'])
def get_tests_requirements():
    """دریافت نیازمندی‌های داده برای چند آزمون"""
    try:
        test_ids = request.json.get('test_ids', [])
        all_files = get_all_required_files(test_ids)
        return jsonify({'success': True, 'files': all_files})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/test-description/<test_id>')
def get_test_description(test_id):
    """دریافت توضیحات آزمون از فایل MD"""
    try:
        md_path = os.path.join('queries', f'{test_id}.md')
        if os.path.exists(md_path):
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({'success': True, 'description': content})
        else:
            return jsonify({'success': False, 'error': 'فایل توضیحات یافت نشد'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/upload', methods=['POST'])
def upload_file():
    """آپلود فایل اکسل و وارد کردن به دیتابیس"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'فایلی انتخاب نشده است'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'فایلی انتخاب نشده است'}), 400
        
        if not file.filename.endswith(('.xlsx', '.xls')):
            return jsonify({'error': 'فقط فایل‌های اکسل مجاز هستند'}), 400
        
        # ذخیره فایل
        filename = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # خواندن فایل اکسل
        df = pd.read_excel(filepath)
        
        # تبدیل نام ستون‌ها
        column_mapping = {
            'Id': 'Id',
            'تاریخ': 'DocumentDate',
            'شماره سند': 'DocumentNumber',
            'کد حساب': 'AccountCode',
            'بدهکار': 'Debit',
            'بستانکار': 'Credit',
            'شرح': 'Description'
        }
        
        df.rename(columns=column_mapping, inplace=True)
        
        # وارد کردن به دیتابیس
        session = get_write_session()
        
        try:
            # پاک کردن داده‌های قبلی (اختیاری)
            # session.query(Transaction).delete()
            
            records_added = 0
            for _, row in df.iterrows():
                transaction = Transaction(
                    DocumentDate=pd.to_datetime(row.get('DocumentDate')),
                    DocumentNumber=int(row.get('DocumentNumber', 0)),
                    AccountCode=str(row.get('AccountCode', '')),
                    Debit=float(row.get('Debit', 0)),
                    Credit=float(row.get('Credit', 0)),
                    Description=str(row.get('Description', ''))
                )
                session.add(transaction)
                records_added += 1
            
            session.commit()
            
            return jsonify({
                'success': True,
                'message': f'{records_added} رکورد با موفقیت وارد شد',
                'records': records_added
            })
        
        except Exception as e:
            session.rollback()
            return jsonify({'error': f'خطا در وارد کردن داده: {str(e)}'}), 500
        
        finally:
            session.close()
    
    except Exception as e:
        return jsonify({'error': f'خطا: {str(e)}'}), 500


@app.route('/run-test/<test_id>', methods=['POST'])
def run_test(test_id):
    """اجرای یک آزمون خاص"""
    try:
        # بارگذاری ماژول آزمون
        module_path = f'queries.{test_id}'
        test_module = importlib.import_module(module_path)
        
        # دریافت پارامترها از request (اختیاری)
        try:
            params = request.get_json(silent=True) or {}
        except:
            params = {}
        
        # اجرای آزمون
        session = get_db()
        
        try:
            results = test_module.execute(session)
            
            return jsonify({
                'success': True,
                'test_id': test_id,
                'results': results,
                'count': len(results)
            })
        
        finally:
            session.close()
    
    except Exception as e:
        return jsonify({
            'error': f'خطا در اجرای آزمون: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500


@app.route('/run-all-tests', methods=['POST'])
def run_all_tests():
    """اجرای همه آزمون‌ها"""
    results = {}
    
    for category_id, category in AUDIT_TESTS.items():
        for test in category['tests']:
            try:
                module_path = f'queries.{test["id"]}'
                test_module = importlib.import_module(module_path)
                
                session = get_db()
                try:
                    test_results = test_module.execute(session)
                    results[test['id']] = {
                        'success': True,
                        'name': test['name'],
                        'count': len(test_results),
                        'data': test_results[:10]  # فقط 10 رکورد اول
                    }
                finally:
                    session.close()
            
            except Exception as e:
                results[test['id']] = {
                    'success': False,
                    'name': test['name'],
                    'error': str(e)
                }
    
    return jsonify({
        'success': True,
        'results': results
    })


@app.route('/export/<test_id>')
def export_test(test_id):
    """خروجی اکسل از نتایج آزمون"""
    try:
        module_path = f'queries.{test_id}'
        test_module = importlib.import_module(module_path)
        
        session = get_db()
        
        try:
            results = test_module.execute(session)
            
            # تبدیل به DataFrame
            df = pd.DataFrame(results)
            
            # ذخیره به اکسل
            output_filename = f'{test_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            
            df.to_excel(output_path, index=False)
            
            return send_file(output_path, as_attachment=True)
        
        finally:
            session.close()
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # ایجاد جداول دیتابیس
    if not db._initialized:
        db._initialize()
    if db.engine:
        Base.metadata.create_all(db.engine)
    
    # اجرای سرور
    app.run(debug=True, host='0.0.0.0', port=5000)
