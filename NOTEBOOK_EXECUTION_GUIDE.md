# Notebook Execution Guide - Complete Working Solution

**Issue**: KeyError: "['did'] not in index" in Cell 9 (VIF calculation)  
**Root Cause**: DiD variables created too late in execution flow  
**Status**: ✅ FIXED

---

## The Problem

Cell 9 (VIF multicollinearity check) was trying to access the `did` variable:
```python
features_to_check = ['L1_Firm_Size', 'L1_Leverage', 'L1_Asset_Turnover', 'L1_Capital_Intensity', 'did']
vif_data = df_matched[features_to_check].dropna()  # ❌ ERROR: 'did' doesn't exist yet
```

But `did` wasn't created until Cell 14 (DiD Estimation section). This caused consistent KeyError failures.

## The Solution

Moved DiD variable creation from Cell 14 to Cell 3 (right after PSM matching completes).

### Variables Created in Cell 3

```python
# Create 'post' indicator
df_matched['issue_year'] = df_matched.apply(
    lambda x: x['Year'] if x['green_bond_issue'] > 0 else np.nan, axis=1
)
df_matched['first_issue_year'] = df_matched.groupby('company')['issue_year'].transform('min')
df_matched['post'] = (df_matched['Year'] >= df_matched['first_issue_year']).fillna(0).astype(int)

# Create DiD (Treatment × Post interaction)
df_matched['did'] = df_matched['is_issuer'].astype(int) * df_matched['post'].astype(int)

# Create certified vs non-certified DiD (for H3 testing)
df_matched['did_certified'] = df_matched['did'] * df_matched['certified_bond_active'].astype(int)
df_matched['did_non_certified'] = df_matched['did'] * (1 - df_matched['certified_bond_active']).astype(int)
```

## Corrected Execution Order

```
Cell 1:  Load data, create treatment indicators (is_issuer, certified_bond_active)
         ↓
Cell 3:  PSM Matching + ✅ CREATE DiD VARIABLES (NEW LOCATION)
         - post: Years >= first issuance
         - did: Treatment × post interaction
         - did_certified: Certified bonds DiD
         - did_non_certified: Non-certified bonds DiD
         ↓
Cell 4:  Balance Table (compares treated vs control baseline chars)
         ↓
Cell 9:  VIF Multicollinearity Check (NOW WORKS - 'did' exists)
         ↓
Cell 11: DiD Regression (uses existing 'did' variables)
         ↓
Remaining cells: Event study, sensitivity analysis, etc.
```

## Verification

✅ **Data Quality**
- Post-issuance observations: 168
- Treated × Post (did): 168
- All variables successfully created

✅ **VIF Results** (from actual run)
```
          variables      VIF
       L1_Firm_Size 2.986467
        L1_Leverage 2.541026
  L1_Asset_Turnover 1.244064
 L1_Capital_Intensity 1.310978
                 did 1.009499
```

All VIF < 5.0, indicating acceptable multicollinearity levels.

✅ **No Errors**
- Cell 9 VIF calculation: ✅ PASSES
- All downstream cells: ✅ WORK

## How to Run Successfully

### Option 1: Run All Cells Sequentially (Recommended)
```
Jupyter: Select "Run All" or press Ctrl+Shift+Enter
```

### Option 2: Run Specific Cells
1. **Run Cell 1 first** (creates is_issuer, certified_bond_active)
2. **Run Cell 3 second** (creates DiD variables)
3. **Run any subsequent cells** (all dependencies satisfied)

### Option 3: Run from Command Line
```bash
cd /Users/bunnypro/Projects/refinitiv-search
jupyter nbconvert --to notebook --execute notebooks/methodology-and-result.ipynb --output notebooks/methodology-and-result.ipynb
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| KeyError: "['did'] not in index" | Make sure Cell 3 ran (creates DiD variables) |
| KeyError: 'is_issuer' | Make sure Cell 1 ran (creates is_issuer) |
| FileNotFoundError: ../processed_data | Verify working directory is notebooks/ or parent |
| ModuleNotFoundError: fix_critical_issues | Make sure Cell 1 ran (sets up sys.path) |

## Key Takeaway

**DiD variables are now created immediately after PSM matching (Cell 3), not during regression estimation (Cell 14).** This ensures they're available for all downstream diagnostic checks and analyses.

---

## Files Modified

- `notebooks/methodology-and-result.ipynb`
  - Cell 3: Added DiD variable creation code block

## Testing Summary

- ✅ DiD variables create without errors
- ✅ VIF calculation passes (N=35,566 valid observations)
- ✅ All 4 DiD variables available for regression: `did`, `did_certified`, `did_non_certified`, `post`
- ✅ Notebook runs end-to-end without KeyError

---

**Status**: ✅ Notebook now fully functional. No more KeyError when running VIF calculation.
