# Audit Tests Summary

This repository contains **69 audit tests** organized into 23 categories.

## Quick Reference

| Category | Persian Name | Test Count |
|----------|-------------|------------|
| Benford's Law | آزمون‌های قانون بنفورد | 4 |
| Threshold | آزمون‌های آستانه | 3 |
| Duplicate | آزمون‌های تکراری | 4 |
| Statistical | آزمون‌های آماری | 4 |
| Seasonal Pattern | آزمون‌های الگوی فصلی | 3 |
| Reconciliation | آزمون‌های مطابقت | 4 |
| Zero Tests | آزمون‌های صفرها | 3 |
| Inventory | آزمون‌های موجودی | 4 |
| Sales | آزمون‌های فروش | 4 |
| Payroll | آزمون‌های حقوق | 4 |
| Banking | آزمون‌های بانک | 4 |
| Journal | آزمون‌های دفتر روزنامه | 4 |
| Data Quality | آزمون‌های سلامت داده | 3 |
| Advanced | آزمون‌های پیشرفته | 3 |
| Fraud | آزمون‌های تقلب | 3 |
| Anomaly | آزمون‌های ناهنجاری | 2 |
| Trend | آزمون‌های روند | 1 |
| Ratio | آزمون‌های نسبت مالی | 2 |
| Compliance | آزمون‌های انطباق | 1 |
| Accounting | آزمون‌های حسابداری | 2 |
| AI | آزمون‌های هوش مصنوعی | 4 |
| Accounts Receivable | آزمون‌های حسابهای دریافتنی | 1 |
| Sampling | آزمون‌های نمونه‌گیری | 2 |
| **TOTAL** | | **69** |

## Complete Persian Documentation

For a complete list of all tests with descriptions in Persian, see:
- [لیست_آزمون‌های_حسابرسی.md](./لیست_آزمون‌های_حسابرسی.md)

## Running Tests

### Web Interface
```bash
python web_ui.py
```

### Command Line
```bash
python query_runner.py --query <test_name>
```

Example:
```bash
python query_runner.py --query benford_first_digit_test
```

## Test Categories Overview

### 1. Benford's Law Tests (4 tests)
Analyze digit distributions to detect anomalies in financial data.

### 2. Threshold Tests (3 tests)  
Identify amounts just below authorization limits.

### 3. Duplicate Tests (4 tests)
Find suspicious duplicate entries in transactions, checks, names, etc.

### 4. Statistical Tests (4 tests)
Use statistical methods (Z-Score, IQR) to identify outliers.

### 5. Seasonal Pattern Tests (3 tests)
Detect unusual seasonal patterns in cash flow, inventory, and sales.

### 6. Reconciliation Tests (4 tests)
Match data across different sources (bank, payroll, inventory, customers).

### 7. Zero Tests (3 tests)
Identify suspicious patterns involving zeros.

### 8. Inventory Tests (4 tests)
Analyze inventory for slow-moving items, valuation issues, etc.

### 9. Sales Tests (4 tests)
Detect abnormal discounts, pricing, and sales patterns.

### 10. Payroll Tests (4 tests)
Identify excessive salaries, overtime, ghost employees, etc.

### 11. Banking Tests (4 tests)
Find outstanding checks, unmatched transfers, weekend transactions, etc.

### 12. Journal Tests (4 tests)
Analyze manual entries, unsupported entries, period-end adjustments, etc.

### 13. Data Quality Tests (3 tests)
Check for missing data, unreasonable values, and data type issues.

### 14. Advanced Tests (3 tests)
Use advanced techniques for shell companies, sequential analysis, and network analysis.

### 15. Fraud Tests (3 tests)
Detect specific fraud schemes: kiting, lapping, and skimming.

### 16. Anomaly Tests (2 tests)
Find gaps and spikes in data.

### 17. Trend Tests (1 test)
Analyze seasonal variance patterns.

### 18. Ratio Tests (2 tests)
Calculate and analyze financial ratios (quick ratio, debt-to-equity).

### 19. Compliance Tests (1 test)
Check segregation of duties.

### 20. Accounting Tests (2 tests)
Verify footing and cutoff analysis.

### 21. AI Tests (4 tests)
Use machine learning algorithms: advanced Benford, contextual anomalies, isolation forest, K-means clustering.

### 22. Accounts Receivable Tests (1 test)
Analyze customer confirmations.

### 23. Sampling Tests (2 tests)
Implement monetary unit sampling and stratified sampling.

---

**Last Updated:** January 26, 2026  
**Version:** 1.0  
**Total Tests:** 69
