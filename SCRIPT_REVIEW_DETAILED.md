# Detailed Script-by-Script Analysis Matrix

## Legend
- ✅ SAFE (no concerns)
- ⚠️ WARNING (caution needed)
- ❌ ISSUE (problematic)
- 🔄 REFACTOR (needs improvement)

---

## Detailed Breakdown

### 1. authenticity_score.py
```
Lines:              287
Complexity:         Medium
Code Quality:       ⭐⭐⭐⭐
Status:             DUPLICATE (package has partial implementation)
```
| Aspect | Assessment |
|--------|------------|
| **Functionality** | `compute_authenticity_score()`, `generate_authenticity_report()`, `print_authenticity_report()` |
| **Package Equivalent** | `asean_green_bonds/authenticity.py` has `extract_cbi_certification()`, `extract_icma_certification()` but NOT composite score |
| **Dependencies** | pandas, numpy (minimal, good) |
| **Security** | ✅ SAFE - reads from local CSV |
| **Data Handling** | ✅ GOOD - explicit NaN handling, proper fill values |
| **Hard-coded Paths** | ⚠️ WARNING: `'data/green_bonds_*.csv'`, `'processed_data/'` |
| **Recommendation** | MIGRATE - Add `compute_authenticity_score()` to `asean_green_bonds/authenticity.py` |
| **Effort** | LOW (just function extraction) |

---

### 2. bias_detection_tools.py
```
Lines:              183
Complexity:         Medium
Code Quality:       ⭐⭐⭐⭐
Status:             FRAGMENTED (mixes multiple concerns)
```
| Aspect | Assessment |
|--------|------------|
| **Functionality** | `detect_survivorship_bias()`, `normalize_company_name()`, `apply_authenticity_proxy()` |
| **Issues** | ❌ `normalize_company_name()` DUPLICATED in esg_merge_module.py (lines 31-45 vs 20-45) |
| **Dependencies** | pandas, numpy, scipy.stats (good for hypothesis testing) |
| **Security** | ✅ SAFE |
| **Data Handling** | ✅ GOOD - statistical testing, proper window definitions |
| **Hard-coded Paths** | ⚠️ WARNING: `'data/panel_data.csv'`, `'data/green-bonds.csv'`, outputs to `'data/'` |
| **Code Duplication** | ❌ `normalize_company_name()` is VERBATIM copy |
| **Recommendation** | SPLIT: (1) Keep `detect_survivorship_bias()` as one-off, (2) Move `apply_authenticity_proxy()` to package, (3) Extract `normalize_company_name()` to utils |
| **Effort** | MEDIUM (deduplication + extraction) |

---

### 3. calculate_tobin_q.py
```
Lines:              54
Complexity:         Low
Code Quality:       ⭐⭐⭐
Status:             ONE-OFF UTILITY
```
| Aspect | Assessment |
|--------|------------|
| **Functionality** | Adds `Tobin_Q` column to panel data |
| **Purpose** | Financial metric calculation (one-time transformation) |
| **Dependencies** | pandas, numpy (minimal) |
| **Security** | ✅ SAFE |
| **Data Handling** | ✅ GOOD - winsorizes outliers, handles missing values |
| **Hard-coded Paths** | ⚠️ WARNING: `'processed_data/final_engineered_panel_data.csv'` |
| **Reusability** | ❌ LOW - very specific use case |
| **Recommendation** | DELETE (likely already applied via `feature_engineering.py`) OR extract as function to package |
| **Effort** | MINIMAL (delete or 5-min refactor) |

---

### 4. check_data_columns.py
```
Lines:              74
Complexity:         Low
Code Quality:       ⭐⭐⭐
Status:             DIAGNOSTIC (debug utility)
```
| Aspect | Assessment |
|--------|------------|
| **Functionality** | Inspects column names and data availability |
| **Purpose** | Debugging/validation script (one-time use) |
| **Dependencies** | pandas only |
| **Security** | ✅ SAFE |
| **Data Handling** | ✅ GOOD - proper introspection |
| **Hard-coded Paths** | ⚠️ WARNING: `'processed_data/final_engineered_panel_data.csv'` |
| **Reusability** | ❌ LOW - diagnostic only |
| **Recommendation** | DELETE (not needed in production) |
| **Effort** | MINIMAL (delete) |

---

### 5. esg_merge_module.py ⭐ PRIORITY 1
```
Lines:              535 (LARGEST)
Complexity:         High
Code Quality:       ⭐⭐⭐⭐⭐ (EXCELLENT)
Status:             SHOULD BE IN PACKAGE
```
| Aspect | Assessment |
|--------|------------|
| **Functionality** | Complete ESG score merging pipeline with fuzzy matching |
| **Key Functions** | `normalize_and_match_issuers()` (113 lines), `merge_esg_scores()` (107 lines), `create_esg_coverage_report()` |
| **Algorithms** | Multi-strategy fuzzy name matching (exact → prefix → keyword), forward/backward fill for missing years |
| **Dependencies** | pandas, numpy, re, logging (all standard) |
| **Security** | ✅ SAFE |
| **Data Handling** | ✅ EXCELLENT - comprehensive error handling, logging, null handling |
| **Code Duplication** | ❌ `normalize_company_name()` DUPLICATED in bias_detection_tools.py |
| **Documentation** | ✅ EXCELLENT - detailed docstrings, type hints |
| **Hard-coded Paths** | ❌ ISSUE: None detected (reads from parameters) ✓ |
| **Recommendation** | MIGRATE - Create `asean_green_bonds/data/esg_merge.py` (minimal changes needed) |
| **Effort** | LOW (copy + deduplicate utils + update imports) |
| **Complexity** | Low migration risk (self-contained, well-tested logic) |

---

### 6. greenbonds.py
```
Lines:              165
Complexity:         Medium
Code Quality:       ⭐⭐⭐⭐
Status:             INFRASTRUCTURE (periodic/one-time)
```
| Aspect | Assessment |
|--------|------------|
| **Functionality** | LSEG Refinitiv API batched data retrieval |
| **Purpose** | Data refresh pipeline (infrastructure) |
| **API Used** | refinitiv.data (rd) - requires LSEG Workspace session |
| **Dependencies** | refinitiv.data, pandas, time |
| **Security** | ✅ SAFE - No hardcoded credentials, uses session auth |
| **Authentication** | ✓ Session-based (best practice for LSEG) |
| **Batch Strategy** | ✓ Good - 5 batches, 1.5s delays between requests |
| **Error Handling** | ✅ GOOD - try/except for each batch, graceful degradation |
| **Documentation** | ✅ GOOD - documents field validation, removals, corrections |
| **Hard-coded Paths** | ⚠️ WARNING: `'data/green_bonds_lseg_full.csv'` output |
| **Recommendation** | MIGRATE - Create `asean_green_bonds/data/lseg_retrieval.py` (reusable periodic script) |
| **Effort** | LOW (straightforward extraction) |
| **Reusability** | HIGH (useful for data updates) |

---

### 7. issuer_verification.py ⭐ NEEDS EVALUATION
```
Lines:              254
Complexity:         Medium-High
Code Quality:       ⭐⭐⭐⭐⭐ (EXCELLENT)
Status:             POSSIBLE DUPLICATE
```
| Aspect | Assessment |
|--------|------------|
| **Functionality** | Extract issuer verification attributes (track record, type, framework, sector) |
| **Key Functions** | `compute_issuer_track_record()` (45 lines), `extract_issuer_verification_fields()`, `validate_issuer_fields()`, `generate_field_statistics()` |
| **Package Equivalent** | `asean_green_bonds/data/feature_engineering.py` - NEEDS COMPARISON |
| **Dependencies** | pandas, numpy, typing (all standard) |
| **Security** | ✅ SAFE |
| **Data Handling** | ✅ EXCELLENT - validates required columns, comprehensive reporting |
| **Documentation** | ✅ EXCELLENT - detailed docstrings, validation, stats reporting |
| **Hard-coded Paths** | ✅ SAFE (none detected) |
| **Validation** | ✅ GOOD - `validate_issuer_fields()` checks completeness |
| **Recommendation** | EVALUATE (1) Check overlap with `feature_engineering.py`, (2) If no overlap, migrate as specialized module, (3) If overlap, merge carefully |
| **Effort** | MEDIUM (requires comparative analysis first) |
| **Risk** | MEDIUM (need to verify no functionality loss if merging) |

---

### 8. prepare_data.py
```
Lines:              280
Complexity:         High
Code Quality:       ⭐⭐⭐⭐
Status:             DATA PIPELINE (periodic)
```
| Aspect | Assessment |
|--------|------------|
| **Functionality** | Extract Refinitiv Excel export → structured CSVs |
| **Input** | `data2802.xlsx` (hard-coded!) |
| **Output** | `data/panel_data.csv`, `data/esg_panel_data.csv`, `data/series_data.csv` |
| **Dependencies** | pandas, openpyxl, numpy |
| **Security** | ✅ SAFE |
| **Data Handling** | ✅ GOOD - filters ERROR rows, proper pivoting |
| **Hard-coded Values** | ❌ ISSUE - Multiple hard-coded constants: |
|  | • `ATTRIBUTE_COLUMNS` (22 items, lines 5-28) |
|  | • `ESG_ATTRIBUTE_COLUMNS` (6 items, lines 30-38) |
|  | • `WORLDSCOPE_TO_ATTRIBUTE` mapping (21 items) |
|  | • `COUNTRIES` list (7 countries) |
|  | • Sheet names (`TS_SHEET_NAME`, `SERIES_SHEET_NAME`, `ESG_SHEET_NAME`) - order matters! |
|  | • File name: `DATA_FILE = "data2802.xlsx"` |
| **Fragility** | ⚠️ WARNING - Sheet order matters (swapped for Philippines/Indonesia) - comments explain but brittle |
| **CSV Append Mode** | ❌ CONCERN - Uses `mode='a'` (append) after deleting old files. Risk of duplicates if script fails mid-run |
| **Recommendation** | MIGRATE - Create `asean_green_bonds/data/excel_parser.py` with: |
|  | ✅ Parameterized mapping dictionaries |
|  | ✅ Config-driven sheet names |
|  | ✅ Use proper pandas.concat() instead of append mode |
|  | ✅ Document Excel structure requirements |
| **Effort** | MEDIUM (refactoring for parameterization) |
| **Risk** | MEDIUM (Excel structure is tightly coupled) |

---

### 9. regenerate_data.py
```
Lines:              75
Complexity:         Low-Medium
Code Quality:       ⭐⭐⭐⭐
Status:             ORCHESTRATOR (uses package)
```
| Aspect | Assessment |
|--------|------------|
| **Functionality** | Runs complete data engineering pipeline with validation |
| **Strategy** | Calls package functions from `asean_green_bonds.config` and `asean_green_bonds.data` |
| **Dependencies** | asean_green_bonds package (GOOD - already integrated!) |
| **Security** | ✅ SAFE |
| **Data Handling** | ✅ GOOD - validates output at each step |
| **Hard-coded Paths** | ✅ SAFE (uses config.py) |
| **Recommendation** | MOVE TO PACKAGE - Become entry point: |
|  | • Option A: `asean_green_bonds/data/__main__.py` (for `python -m asean_green_bonds.data`) |
|  | • Option B: CLI entry in setup.py (for `regenerate-data` command) |
|  | • Better: Both for flexibility |
| **Effort** | LOW (just relocation) |
| **Value** | HIGH (useful for data pipeline automation) |

---

### 10. validate_greenbonds_output.py
```
Lines:              104
Complexity:         Low-Medium
Code Quality:       ⭐⭐⭐⭐
Status:             QA/TESTING
```
| Aspect | Assessment |
|--------|------------|
| **Functionality** | Validates LSEG retrieval output completeness |
| **Purpose** | Testing/QA script (not part of main pipeline) |
| **Dependencies** | pandas, pathlib (standard) |
| **Security** | ✅ SAFE |
| **Validation Checks** | ✓ File existence, record count, field completeness, missing value analysis, batch coverage |
| **Data Handling** | ✅ GOOD |
| **Hard-coded Paths** | ⚠️ WARNING: `'data/green_bonds_lseg_full.csv'` |
| **Recommendation** | MOVE - Create `tests/test_greenbonds_output.py` |
| **Effort** | MINIMAL (just move + refactor to pytest) |

---

### 11. NOTEBOOK_FIX.py
```
Lines:              18
Complexity:         None (not executable)
Code Quality:       N/A
Status:             TEMPORARY DOCUMENTATION
```
| Aspect | Assessment |
|--------|------------|
| **Content** | Example code showing Tobin_Q → return_on_equity_total substitution |
| **Purpose** | Quick reference for notebook fix |
| **Recommendation** | DELETE - This is documentation, not executable code |
|  | ✅ Keep the fix in the actual code |
|  | ✅ If needed, document in CHANGELOG.md or commit message |
| **Effort** | MINIMAL (delete) |

---

## Summary Statistics

| Category | Count | Lines | Recommendation |
|----------|-------|-------|-----------------|
| **MIGRATE to Package** | 6 | ~1,600 | High priority |
| **REMOVE/DELETE** | 3 | ~156 | Quick cleanup |
| **EVALUATE** | 1 | 254 | Needs analysis |
| **KEEP as-is** | 1 | 75 | Already uses package |

---

## Risk Matrix

```
                HIGH CODE      MEDIUM CODE      LOW CODE
                QUALITY        QUALITY          QUALITY
┌────────────────────────────────────────────────────────┐
│ HIGH PRIORITY │ esg_merge    │ prepare_data   │        │
│ DUPLICATE     │ (535)        │ (280)          │        │
├────────────────────────────────────────────────────────┤
│ MEDIUM        │ issuer_verify│ authenticity   │        │
│ DUPLICATE     │ (254)        │ bias_detect    │        │
│              │              │ (287+183)      │        │
├────────────────────────────────────────────────────────┤
│ LOW IMPACT    │              │ greenbonds     │ calc_  │
│ ONE-OFF       │              │ regen          │ q check│
│              │              │ (165+75)       │(128)   │
└────────────────────────────────────────────────────────┘
```

**Key**: Migrate high-quality scripts first (low risk, high value)

