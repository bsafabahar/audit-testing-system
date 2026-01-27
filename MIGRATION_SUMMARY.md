# Migration Summary: Old Tests → International Standard Tests

## Overview
This document summarizes the replacement of 6 locally-named audit tests with internationally-recognized standard tests following ISA (International Standards on Auditing) and AICPA guidelines.

## Date
January 27, 2024

## Changes Made

### 1. Threshold Tests Category
**Old Tests Removed:**
- `threshold_fifty_percent_test` (آزمون ۵۰ درصد)
- `threshold_one_and_half_test` (آزمون یک‌ونیم برابر)
- `threshold_double_test` (آزمون دو برابر)

**New Tests Added:**
- `variance_threshold_test` (تحلیل آستانه واریانس)
  - Enhanced with configurable variance threshold parameter
  - Z-Score statistical analysis
  - References: ISA 520, AICPA AU-C Section 520
  
- `statistical_upper_limit_test` (حد بالای آماری)
  - Configurable multiplier (default 1.5)
  - Two calculation methods: mean-based and stdev-based
  - References: ISA 530, ACL Analytics Guide
  
- `high_value_transaction_test` (تحلیل تراکنش‌های با ارزش بالا)
  - Multiple threshold methods: multiplier, percentile, standard deviation
  - Four-level risk categorization (Low, Medium, High, Critical)
  - References: ISA 530, AICPA Audit Sampling Guide

### 2. Seasonal Pattern Tests Category (formerly "Cyclical Tests")
**Old Tests Removed:**
- `cyclical_sales_test` (الگوی سینوسی فروش)
- `cyclical_cash_flow_test` (الگوی سینوسی صندوق)
- `cyclical_inventory_test` (الگوی سینوسی موجودی)

**New Tests Added:**
- `seasonal_sales_pattern_test` (تحلیل الگوی فصلی فروش)
  - Time series decomposition
  - Moving average analysis
  - Seasonal index calculation
  - References: ISA 520 (Analytical Procedures)
  
- `seasonal_cash_flow_test` (تحلیل فصلی جریان نقدی)
  - Cash flow trend analysis
  - Volatility analysis
  - Separate inflow/outflow tracking
  - References: ISA 570 (Going Concern)
  
- `seasonal_inventory_pattern_test` (تحلیل الگوی فصلی موجودی)
  - Inventory turnover analysis
  - Seasonal fluctuation detection
  - Abnormal pattern identification
  - References: ISA 501 (Inventory Audit)

### 3. Category Name Changes
- **Old**: "آزمون‌های سینوسی" (Cyclical Tests)
- **New**: "آزمون‌های الگوی فصلی" (Seasonal Pattern Tests)

The term "سینوسی" (sinusoidal) has been completely removed from the system as it's a local/Persian term not recognized in international auditing standards.

## Files Modified

### Configuration Files
1. `web_ui.py`
   - Updated AUDIT_TESTS dictionary
   - Updated SUBSYSTEM_MAPPING for 6 subsystems
   - Changed category name from "سینوسی" to "الگوی فصلی"

2. `test_data_requirements.py`
   - Updated all 6 test entries with new names and descriptions

3. `لیست_آزمون‌های_حسابرسی.md`
   - Updated threshold tests section
   - Updated seasonal pattern tests section
   - Updated category count table

4. `queries/README_DOCS_FA.md`
   - Updated threshold tests section
   - Renamed cyclical tests to seasonal pattern tests

5. `TEST_LIST_SUMMARY.md`
   - Changed "Cyclical" category to "Seasonal Pattern"

### Files Deleted (12 files)
- `queries/threshold_fifty_percent_test.py`
- `queries/threshold_fifty_percent_test.md`
- `queries/threshold_one_and_half_test.py`
- `queries/threshold_one_and_half_test.md`
- `queries/threshold_double_test.py`
- `queries/threshold_double_test.md`
- `queries/cyclical_sales_test.py`
- `queries/cyclical_sales_test.md`
- `queries/cyclical_cash_flow_test.py`
- `queries/cyclical_cash_flow_test.md`
- `queries/cyclical_inventory_test.py`
- `queries/cyclical_inventory_test.md`

### Files Created (12 files)
- `queries/variance_threshold_test.py` (5.4 KB)
- `queries/variance_threshold_test.md` (11 KB)
- `queries/statistical_upper_limit_test.py` (4.6 KB)
- `queries/statistical_upper_limit_test.md` (12 KB)
- `queries/high_value_transaction_test.py` (5.6 KB)
- `queries/high_value_transaction_test.md` (16 KB)
- `queries/seasonal_sales_pattern_test.py` (8.7 KB)
- `queries/seasonal_sales_pattern_test.md` (16 KB)
- `queries/seasonal_cash_flow_test.py` (9.9 KB)
- `queries/seasonal_cash_flow_test.md` (16 KB)
- `queries/seasonal_inventory_pattern_test.py` (13.3 KB)
- `queries/seasonal_inventory_pattern_test.md` (16 KB)

## Key Improvements

### Enhanced Features
1. **Configurable Parameters**: All new tests have adjustable parameters instead of fixed values
2. **Statistical Rigor**: Added Z-Score, standard deviation, and statistical significance calculations
3. **Risk Assessment**: Multi-level risk categorization (Low, Medium, High, Critical)
4. **Flexible Methods**: Multiple analysis methods (mean-based, stdev-based, percentile, etc.)
5. **Comprehensive Output**: Enhanced output schemas with more analytical fields

### International Standards Compliance
All new tests reference international auditing standards:
- ISA 520: Analytical Procedures
- ISA 530: Audit Sampling
- ISA 501: Inventory Audit
- ISA 570: Going Concern
- AICPA AU-C Section 520
- ACL Analytics Guide
- AICPA Audit Sampling Guide

### Documentation Quality
- Each test has 11-16 KB of comprehensive Farsi documentation
- Includes practical examples and use cases
- Explains international standard references
- Provides interpretation guidelines
- Documents differences from old tests

## Verification

### Code Quality
✅ All 6 new Python files have valid syntax
✅ All files follow the established patterns
✅ No old test references remain in code files

### References Cleanup
✅ All old test IDs removed from configuration
✅ Term "سینوسی" (sinusoidal) removed from active code
✅ Category renamed to international standard terminology

### Backwards Compatibility Notes
The new tests are NOT backwards compatible with the old tests because:
- Different test IDs
- Enhanced parameters and schemas
- Different output structures

Any saved configurations or bookmarks referencing old tests will need to be updated.

## Testing Status
- ✅ Python syntax validation: PASSED
- ✅ File structure validation: PASSED
- ⏳ Runtime testing: Pending (requires database and dependencies)
- ⏳ UI testing: Pending (requires Flask server)

## Total Changes
- **Tests Replaced**: 6
- **Files Modified**: 5 configuration files
- **Files Deleted**: 12 (6 Python + 6 Markdown)
- **Files Created**: 12 (6 Python + 6 Markdown)
- **Lines of Code**: ~47 KB of new Python code
- **Documentation**: ~99 KB of new Farsi documentation

## Next Steps
1. Review and merge the pull request
2. Update any saved user configurations or favorites
3. Test all new tests with actual data
4. Train users on new test names and parameters
5. Archive old test documentation for reference

## Notes
The old test names are mentioned in the documentation of new tests in the "Differences from Previous Test" section for historical reference, which is acceptable and useful for users migrating from the old system.
