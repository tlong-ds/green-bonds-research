# Review: Root-Level Python Scripts vs Package Functionality

## Executive Summary

**11 root scripts totaling 2,433 lines** mostly duplicate or complement functionality that should be in the `asean_green_bonds` package. The codebase has **GOOD quality** but **needs consolidation**.

---

## 1. DUPLICATE PACKAGE FUNCTIONALITY

### A. **esg_merge_module.py** (535 lines) ⭐ HIGHEST PRIORITY
- **Issue**: Largest standalone script with highly reusable code
- **Duplicates**: 
  - `normalize_company_name()` also in `bias_detection_tools.py` (verbatim copy)
  - Core matching logic not in package
- **Status**: Should be `asean_green_bonds/data/esg_merge.py`
- **Quality**: ⭐⭐⭐⭐⭐ Excellent code (fuzzy matching, logging, error handling)

### B. **authenticity_score.py** (287 lines)
- **Issue**: Implements composite authenticity scoring
- **Duplicates**: Partially complements `asean_green_bonds/authenticity.py`
- **Status**: Should expand package's `authenticity.py` module
- **Quality**: ⭐⭐⭐⭐ Well-documented, good NaN handling

### C. **issuer_verification.py** (254 lines)
- **Issue**: Overlaps with `asean_green_bonds/data/feature_engineering.py`
- **Functions**: issuer track record, type classification, framework detection
- **Status**: Needs integration evaluation
- **Quality**: ⭐⭐⭐⭐⭐ Excellent organization and validation

### D. **bias_detection_tools.py** (183 lines) ⚠️ FRAGMENTED
- **Issue**: Mixes unrelated concerns + code duplication
- **Contents**:
  - `detect_survivorship_bias()` - niche, can stay standalone
  - `normalize_company_name()` - **DUPLICATED** in esg_merge_module.py
  - `apply_authenticity_proxy()` - should be in package
- **Quality**: ⭐⭐⭐⭐ Good statistical testing

---

## 2. SHOULD MIGRATE INTO PACKAGE

### **prepare_data.py** (280 lines)
- **Purpose**: Extracts Refinitiv Excel export → structured CSVs
- **Status**: Data pipeline script (periodic/one-time)
- **Issues**: 
  - Hard-coded sheet names, country codes, WC field mappings
  - mode='a' (append) when rebuilding CSVs - fragile
- **Recommendation**: Migrate as `asean_green_bonds/data/excel_parser.py`
  - ✅ Parameterize configuration
  - ✅ Use existing `config.py`

### **greenbonds.py** (165 lines)
- **Purpose**: LSEG Refinitiv API batched data retrieval
- **Status**: Infrastructure script
- **Quality**: ⭐⭐⭐⭐ Good batch management, session handling
- **Recommendation**: Migrate as `asean_green_bonds/data/lseg_retrieval.py`
  - ✅ Make it reusable for periodic updates
  - ✅ No security concerns (session-based auth)

### **regenerate_data.py** (75 lines)
- **Purpose**: Orchestrates complete data pipeline
- **Status**: Already imports package (good!)
- **Recommendation**: Move to package as `asean_green_bonds/data/__main__.py` or CLI entry point

---

## 3. ONE-OFF UTILITIES - REMOVE OR ARCHIVE

### A. **calculate_tobin_q.py** (54 lines) ❌
- **Purpose**: Add Tobin's Q metric to panel data
- **Issue**: Simple transformation, one-time script
- **Recommendation**: 
  - DELETE (already done via feature engineering), OR
  - Add as function to `asean_green_bonds/data/feature_engineering.py`

### B. **check_data_columns.py** (74 lines) ❌
- **Purpose**: Inspect available columns for debugging
- **Issue**: Diagnostic script, one-time use
- **Recommendation**: DELETE (not needed in production)

### C. **validate_greenbonds_output.py** (104 lines) ⬜
- **Purpose**: QA validation of LSEG retrieval
- **Issue**: Testing script, not part of main flow
- **Recommendation**: Move to `tests/` directory

### D. **NOTEBOOK_FIX.py** (18 lines) ❌
- **Issue**: Temporary documentation, not executable code
- **Recommendation**: DELETE (should be in PR notes, not a file)

---

## 4. CODE QUALITY ASSESSMENT

| Aspect | Status | Details |
|--------|--------|---------|
| **Overall Quality** | ⭐⭐⭐⭐ GOOD | Mostly 7-8/10, well-structured |
| **Security** | ✅ SAFE | No hardcoded credentials, proper session mgmt |
| **Data Handling** | ✅ GOOD | NaN handling, type conversion, error checks |
| **Testing** | ⚠️ LIMITED | No unit tests, test files separate |
| **Documentation** | ✅ EXCELLENT | Good docstrings, comments, type hints |

### Specific Concerns

**Security** ✅ No issues found
- No API keys/credentials hardcoded
- LSEG Workspace session-based authentication (best practice)
- No injection vulnerabilities

**Data Quality** ✅ Generally good
- Most scripts handle missing values properly
- File path validation present in some scripts
- **⚠️ Main issue**: Hard-coded relative paths (`'data/'`, `'processed_data/'`)
  - **Fix**: Use existing `asean_green_bonds/config.py` instead

**Notable Issues**
- `prepare_data.py` uses `mode='a'` (append) for CSV rebuilds - fragile, risk of duplicates
- `normalize_company_name()` duplicated between 2 scripts
- Inconsistent date parsing across scripts

---

## 5. RECOMMENDED MIGRATION STRATEGY

### PHASE 1 (High Impact)
1. **esg_merge_module.py** (535 lines)
   - Create `asean_green_bonds/data/esg_merge.py`
   - Extract `normalize_company_name()` → `asean_green_bonds/utils/normalize.py`
   - Excellent code, low risk migration

2. **Extract shared utilities**
   - Move `normalize_company_name()` to shared module (eliminates duplication)
   - Move `parse_issue_date()` to `utils/date_utils.py`

3. **Evaluate issuer_verification.py** (254 lines)
   - Compare with `feature_engineering.py` for overlaps
   - Either merge or create `asean_green_bonds/data/issuer_verification.py`

### PHASE 2 (Medium Impact)
4. **authenticity_score.py** → Expand `asean_green_bonds/authenticity.py`
   - Add `compute_authenticity_score()` function
   - Integrate with CBI/ICMA certification functions

5. **prepare_data.py** → `asean_green_bonds/data/excel_parser.py`
   - Parameterize hard-coded values
   - Fix append mode CSV building

6. **regenerate_data.py** → Package entry point
   - Move to `asean_green_bonds/data/__main__.py`
   - Or create CLI via setup.py

### PHASE 3 (Cleanup)
7. **Remove/archive**
   - Delete: `calculate_tobin_q.py`, `check_data_columns.py`, `NOTEBOOK_FIX.py`
   - Move to tests/: `validate_greenbonds_output.py` + `test_*.py` files

---

## 6. ESTIMATED IMPACT

| Metric | Impact |
|--------|--------|
| **Lines to migrate** | ~1,600 (66% of root scripts) |
| **Code duplication eliminated** | ~100 lines (normalize_company_name, etc.) |
| **Package modules created** | 5-6 new modules |
| **Root scripts remaining** | 2-3 (diagnostics, one-offs) |
| **Complexity** | Low-Medium (mostly copy/paste + parameterization) |
| **Risk Level** | LOW (good code quality, clear functionality) |

---

## 7. KEY FILES FOR REVIEW

**Read these first:**
1. **esg_merge_module.py** - Excellent documentation, ready to migrate
2. **issuer_verification.py** - Check for overlaps with feature_engineering.py
3. **prepare_data.py** - Document Excel structure before parameterizing
4. **asean_green_bonds/config.py** - Current config patterns to follow

---

## QUICK ACTION ITEMS

- [ ] **Migrate esg_merge_module.py** to package (highest ROI)
- [ ] **Deduplicate normalize_company_name()** to shared module
- [ ] **Evaluate issuer_verification.py** against feature_engineering.py
- [ ] **Parameterize prepare_data.py** hard-coded paths
- [ ] **Delete NOTEBOOK_FIX.py** - not executable code
- [ ] **Move tests to tests/ directory** (test_*.py files)
- [ ] **Update README** post-migration

