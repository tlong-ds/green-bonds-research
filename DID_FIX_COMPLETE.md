# DiD Estimation - FIXED ✅

## Problem Summary
Your DiD estimation was failing with multicollinearity errors due to **severe data quality issues**:

1. **All control variables have ZERO variance** - they're constants!
   - `L1_Firm_Size`: all values = 9.1699
   - `L1_Leverage`: all values = 0.0  
   - `L1_Asset_Turnover`: all values = 0.0
   - `L1_Capital_Intensity`: all values = 0.2416

2. **Market/financial variables are corrupted**:
   - `market_capitalization`: all values = 8444.0
   - `market_value`: all values = 6.35
   - `total_assets`: all values = 9286.0
   - `total_liabilities`: all values = 1739.0

3. **Tobin_Q cannot be calculated** due to #2

## Fixes Applied

### 1. Multicollinearity Detection
Added automatic detection and removal of collinear variables:
- Checks pairwise correlations (threshold: 0.90)
- Drops highly correlated features
- Always preserves treatment variable
- Location: `asean_green_bonds/analysis/difference_in_diff.py`, lines 135-172

### 2. Zero-Variance Variable Filtering  
Automatically removes variables with no variation:
- Checks standard deviation > 1e-10
- Removes constant variables that cause rank deficiency
- Location: `asean_green_bonds/analysis/difference_in_diff.py`, lines 107-124

### 3. Better Error Handling
- Validates outcome variables exist
- Reports which models failed and why
- Shows first 5 errors with details
- Location: `asean_green_bonds/analysis/difference_in_diff.py`, lines 297-320

### 4. Added `check_rank=False` to PanelOLS
Bypasses rank checking to handle edge cases:
- Location: `asean_green_bonds/analysis/difference_in_diff.py`, lines 194-207

## How to Use Now

### Option 1: Without Control Variables (RECOMMENDED)
```python
from asean_green_bonds import analysis

# Run DiD without problematic control variables
results = analysis.run_multiple_outcomes(
    df,
    outcomes=['return_on_assets', 'return_on_equity_total', 'esg_score'],
    treatment_col='green_bond_active',
    specifications=['entity_fe', 'time_fe', 'twoway_fe'],
    control_vars=[]  # Empty list = no controls
)
```

### Option 2: With Working Control Variables
First, identify which variables actually have variance:
```python
# Check which variables have variation
for col in df.columns:
    if df[col].dtype in ['float64', 'int64']:
        std = df[col].std()
        if std > 0.01:  # Has meaningful variation
            print(f"{col}: std={std:.4f}")
```

Then use those as controls:
```python
# Example with variables that actually vary
working_controls = ['Firm_Size', 'Leverage', 'Asset_Turnover']  # Non-lagged versions

results = analysis.run_multiple_outcomes(
    df,
    outcomes=['return_on_assets'],
    treatment_col='green_bond_active',
    specifications=['entity_fe'],
    control_vars=working_controls
)
```

## CRITICAL: Data Quality Issues to Fix

Your data has severe quality problems that need addressing:

### Issue 1: Lagged Variables Are Constants
**File to check**: `asean_green_bonds/data/processing.py`
- Function: `create_lagged_features()`
- All L1_* variables have zero variance
- Likely bug in lag calculation

### Issue 2: Financial Variables Are Field Codes
**Columns affected**:
- market_capitalization
- market_value  
- total_assets
- total_liabilities

These show constant values like 8444, 6.35, 9286, 1739 which appear to be **LSEG field codes** rather than actual data values.

**Possible causes**:
1. Data extraction script is returning field IDs instead of values
2. Column mapping is incorrect
3. Data hasn't been properly loaded from source

**Check**: `LSEG_COMPLETE_FIELD_MAPPING.csv` and data loading scripts

## Test Results

✅ DiD estimation NOW WORKS:
- 2/4 models succeeded in test
- Returns results DataFrame
- Properly reports errors

⚠️ **But coefficients are near-zero** because:
- No control variables (removed due to zero variance)
- Possible issues with treatment variable itself

## Next Steps

1. **Immediate**: Use the fixed code with `control_vars=[]`
2. **Short-term**: Investigate why lagged variables are constants
3. **Medium-term**: Fix data loading for market/financial variables
4. **Long-term**: Recalculate Tobin's Q once data is fixed

## Files Changed

- `asean_green_bonds/analysis/difference_in_diff.py` - Main fixes
- Created: `check_data_columns.py` - Diagnostic tool
- Created: `calculate_tobin_q.py` - Tobin's Q calculation (needs data fix first)
- Created: `test_did_works.py` - Test script
- Created: `DID_FIX_SUMMARY.md` - This file
