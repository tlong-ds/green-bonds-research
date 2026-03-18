# Consolidated Authenticity Attributes Summary

## Overview
Successfully consolidated all authenticity attributes from 6 independent data sources into a single comprehensive DataFrame containing all 333 ASEAN green bonds with 59 columns of attributes.

## Output Files Generated

### 1. **consolidated_authenticity_attributes.csv** (Main Output)
- **Location:** `data/consolidated_authenticity_attributes.csv`
- **Size:** 227 KB
- **Records:** 333 (100% of bonds)
- **Columns:** 59
- **Primary Key:** Deal PermID (unique, non-null)

### 2. **CONSOLIDATED_ATTRIBUTES_COLUMN_MAPPING.json**
- Detailed JSON mapping of all 59 columns
- Includes: section, description, data type, non-null counts
- Machine-readable format for downstream analysis

### 3. **CONSOLIDATION_DATA_QUALITY_REPORT.txt**
- Comprehensive data quality report
- Merge validation metrics
- Completeness analysis by category
- Authenticity score statistics
- Missing data analysis

## Data Sources Consolidated

| Source | Records | Columns | Key Attributes |
|--------|---------|---------|-----------------|
| green_bonds_authentic.csv | 333 | 37 | Original bond fields, is_authentic, esg_improvement, esg_pvalue |
| bonds_with_icma_certification.csv | 333 | 35 | is_cbi_certified, is_icma_certified, icma_confidence |
| green_bonds_with_esg_scores.csv | 333 | 40 | esg_score_pre/issuance/post, environmental_investment, esg coverage |
| green_bonds_with_issuer_fields.csv | 333 | 37 | issuer_nation, issuer_sector, issuer_type, has_green_framework |
| green_bonds_with_authenticity_score.csv | 333 | 19 | authenticity_score, authenticity_category, score components |
| green_bonds_with_certification.csv | 333 | 32 | is_certified general flag |

## Column Structure (59 Columns)

### Original Bond Fields (11)
- Deal PermID, Package Identifier, Master Deal Type Code, Issue Date, Issuer Name, Issuer PermID, Issue Type, Transaction Status, Issuer Nation, etc.

### Market & Transaction Fields (16)
- Proceeds, Offering Price, Stock Exchange, Security Type, Offering Technique, Gross Spread, Business Sector, Economic Sector, etc.

### Decoded Reference Fields (3)
- Master Deal Type, All New Issues Manager Roles, Manager's Role

### Authenticity Assessment (ESG DiD) (5)
- **is_authentic:** Binary flag (1=authentic via DiD, 0=not)
- **esg_improvement:** ESG improvement estimand
- **esg_pvalue:** P-value for significance test
- **n_pre_obs, n_post_obs:** Pre/post observation counts

### Certification Status (4)
- **is_cbi_certified:** CBI certification status (328/333 = 98.5%)
- **is_icma_certified:** ICMA certification status (326/333 = 97.9%)
- **icma_confidence:** Confidence score (0-1)
- **is_certified:** Any certification (328/333 = 98.5%)

### ESG Scores & Impact (8)
- esg_score_pre_issuance, esg_score_issuance_year, esg_score_post_issuance
- environmental_investment, has_esg_data, esg_data_source, esg_matching_company, esg_coverage_years

### Issuer Verification (5)
- **issuer_nation:** Issuer country
- **issuer_sector:** Sector classification
- **issuer_type:** Issuer type (sovereign/corporate/financial/etc)
- **issuer_track_record:** Green financing track record score
- **has_green_framework:** Framework availability flag

### Authenticity Score Components (5)
- **esg_component:** ESG authenticity component (0-100)
- **cert_component:** Certification authenticity component (0-100)
- **issuer_component:** Issuer authenticity component (0-100)
- **authenticity_score:** Composite score (0-100)
- **authenticity_category:** Category (High/Low/Unverified)

### Data Quality (1)
- **data_quality:** Data completeness indicator

## Key Statistics

### Merge Validation
- ✓ All 333 bonds consolidated (100% coverage)
- ✓ Deal PermID unique and non-null (333/333)
- ✓ No duplicate records
- ✓ No conflicts in merged columns

### Authenticity Classification
- **High Authenticity:** 13 bonds (3.9%)
- **Low Authenticity:** 314 bonds (94.3%)
- **Unverified:** 6 bonds (1.8%)

### Certification Coverage
- **CBI Certified:** 328 bonds (98.5%)
- **ICMA Certified:** 326 bonds (97.9%)
- **Both Certified:** 326 bonds (97.9%)
- **At Least One:** 328 bonds (98.5%)

### ESG Authenticity (DiD Assessment)
- **Authentic (Significant ESG improvement):** 13 bonds (3.9%)
- **Not Authentic:** 320 bonds (96.1%)

### Authenticity Score Distribution
- **Mean:** 53.81 (std: 9.90)
- **Median:** 55.00
- **Range:** 10.00 - 95.00
- **Interquartile Range:** 55.00 (25th-75th percentile)

## Data Completeness

| Category | Completeness | Notes |
|----------|-------------|-------|
| Original Bond Fields | 100% | All primary identifiers complete |
| Authenticity Fields | 100% | All core authenticity measures complete |
| Certification Fields | 100% | All certification flags complete |
| ESG Score Fields | 17.1% | Limited ESG data availability (expected) |
| Issuer Verification | 100% | All issuer attributes complete |

### Missing Data Analysis
- **Complete data:** 46 columns (78% of total)
- **Minimal missing (0-7%):** 8 columns
- **Moderate missing (47-83%):** 5 columns (mostly ESG-related, expected sparsity)

## Merge Strategy

1. **Base DataFrame:** Started with green_bonds_authentic.csv (333 × 37 columns)
2. **Merge Order:**
   - Added ICMA certification attributes (3 columns)
   - Added ESG scores (8 columns)
   - Added issuer verification (5 columns)
   - Added authenticity score components (5 columns)
   - Added general certification flag (1 column)
3. **Consolidation:** All merges performed on Deal PermID key
4. **Duplicate Handling:** No duplicates found; all 333 records preserved

## Data Quality Assessment

### Strengths
- ✓ 100% coverage for all 333 bonds
- ✓ Complete authenticity classification
- ✓ Strong certification coverage (98%+)
- ✓ No duplicate records or primary key conflicts
- ✓ Consistent data types across columns
- ✓ All critical authenticity fields complete

### Limitations
- ESG score data limited to ~17% coverage (expected, as not all issuers have comparable ESG ratings)
- 22 records missing Issuer/Borrower PermID (6.6%, pre-existing in source data)
- Some stock exchange and offering technique data sparse (expected for ASEAN bonds)

## Ready for Analysis

The consolidated DataFrame is now ready for:
1. **Econometric Analysis:** Panel data with all authenticity dimensions
2. **Machine Learning:** Comprehensive feature set with authenticity labels
3. **Causal Analysis:** Event study design with pre/post ESG scores
4. **Portfolio Analysis:** Bond-level authenticity metrics for investment decisions
5. **Reporting:** Complete dataset for stakeholder communication

## Files Location

```
/Users/bunnypro/Projects/refinitiv-search/
├── data/
│   └── consolidated_authenticity_attributes.csv     (Main output)
├── CONSOLIDATED_ATTRIBUTES_COLUMN_MAPPING.json      (Column mapping)
├── CONSOLIDATION_DATA_QUALITY_REPORT.txt            (Detailed QA report)
└── CONSOLIDATION_SUMMARY.md                          (This file)
```

## Next Steps

1. Load `consolidated_authenticity_attributes.csv` for analysis
2. Reference `CONSOLIDATED_ATTRIBUTES_COLUMN_MAPPING.json` for column definitions
3. Use authenticity components (esg_component, cert_component, issuer_component) for decomposition analysis
4. Filter by authenticity_category for segmented analysis

---
**Generated:** 2026-03-18
**Status:** ✓ Complete and Validated
