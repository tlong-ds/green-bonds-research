# Diagnostic Feature Selection Guide

## What Changed

Feature selection module has been **refactored for diagnostic purpose**, not for primary model specification.

### Old Understanding ❌
> "Use selected_features for your PSM-DiD model"

### New Understanding ✅
> "Use selected_features to VALIDATE your theory-driven PSM-DiD specification"

---

## New Diagnostic API

### 1. **diagnose_multicollinearity()**
Check VIF (Variance Inflation Factor) for your theory-driven variables.

```python
from asean_green_bonds.data.feature_selection import diagnose_multicollinearity

# Your theory-driven variables
theory_vars = ['firm_size', 'leverage', 'sector', 'profitability']

# Diagnose multicollinearity
vif_report = diagnose_multicollinearity(df, theory_vars)
print(vif_report)
```

**Output:**
```
Variable       VIF    Status
firm_size     2.3    ✓ OK
leverage      1.8    ✓ OK
profitability 3.1    ✓ OK
sector        1.5    ✓ OK
```

**Interpretation:**
- VIF < 5: ✓ OK (low multicollinearity)
- VIF 5-10: ⚠️ Warning (moderate collinearity)
- VIF > 10: ❌ High (possible multicollinearity issues)

---

### 2. **validate_specification()**
Comprehensive diagnostic of your specification against data-driven filters.

```python
from asean_green_bonds.data.feature_selection import validate_specification

# Define your theory-driven specification
theory_vars = ['firm_size', 'leverage', 'sector', 'profitability']

# Validate specification
report = validate_specification(
    df,
    theory_vars=theory_vars,
    outcome_col='esg_score',
    control_cols=theory_vars,
    lagged_cols=[]
)

print(report)
```

**Output includes:**

1. **Overlap Analysis**
   ```
   theory_vars: 4
   auto_selected: 47
   overlap: 3 (75%)
   missing_from_auto: ['sector']
   ```
   - ✓ Good: Most your variables are in auto-selection
   - ⚠️ Watch: 'sector' is low-signal but essential confounder

2. **Multicollinearity (VIF)**
   - Shows VIF for your theory-driven variables
   - Flags issues (> 10 VIF)

3. **Variable Importance Ranking**
   ```
   Variable       Correlation  Ranking  Signal
   profitability  0.25         1        ✓ Strong
   firm_size      0.18         2        ✓ Strong
   leverage       0.12         3        ⚠️ Weak
   sector         0.03         4        ⚠️ Weak
   ```
   - Shows where your variables rank by importance
   - Validates that essential variables aren't completely ignored

4. **Data Quality**
   ```
   total_vars: 4
   missing_pct: {firm_size: 0.0, leverage: 0.0, sector: 0.0, profitability: 0.0}
   zero_variance_vars: []
   ```

5. **Recommendations**
   ```
   ✓ 1 theory vars NOT in auto-selection: ['sector'].
     These may be low-signal but essential confounders - KEEP THEM.
   
   ✓ This validation shows specification alignment with data.
     Proceed with theory-driven PSM-DiD specification.
   ```

---

### 3. **compare_specifications()**
Create a side-by-side comparison table.

```python
from asean_green_bonds.data.feature_selection import compare_specifications

comparison = compare_specifications(df, theory_vars, 'esg_score')
print(comparison)
```

**Output:**
```
Variable       In_Theory_Spec  In_Auto_Selected  Correlation
profitability  ✓               ✓                 0.25
firm_size      ✓               ✓                 0.18
leverage       ✓               ✓                 0.12
sector         ✓                                 0.03
extra_var_1                     ✓                 0.05
extra_var_2                     ✓                 0.02
```

**Use for:**
- Showing results are robust to variable selection method
- Identifying which auto-selected variables you're NOT using
- Robustness checks in appendix

---

## Recommended Workflow for PSM-DiD

### Step 1: Define Theory-Driven Specification
```python
# Based on causal theory, NOT data
theory_vars_psm = [
    'firm_size',           # Size affects issuance capacity
    'leverage',            # Debt affects market access
    'sector',              # Industry characteristics
    'profitability',       # Financial performance
    'issuer_track_record', # Experience signal
]

# For DiD, add pre-treatment characteristics
theory_vars_did = theory_vars_psm + [
    'lagged_esg_score',    # Pre-treatment environmental profile
    'lagged_profitability', # Pre-treatment trend
]
```

### Step 2: Run Diagnostic Validation
```python
from asean_green_bonds.data.feature_selection import validate_specification

# Validate PSM specification
psm_report = validate_specification(
    df,
    theory_vars=theory_vars_psm,
    outcome_col='esg_score',
)

print("PSM SPECIFICATION VALIDATION:")
print(psm_report)

# Check for issues
if psm_report.warnings:
    print("\n⚠️  Issues found:")
    for w in psm_report.warnings:
        print(f"  {w}")
else:
    print("\n✅ No multicollinearity issues found")
```

### Step 3: Run PSM-DiD Model
```python
# Use your theory-driven specification (NOT selected_features)
results = analysis.run_psm_did(
    df,
    ps_vars=theory_vars_psm,
    did_controls=theory_vars_did,
    entity_fe=True,
    time_fe=True
)
```

### Step 4: (Optional) Robustness Check
```python
from asean_green_bonds.data import loader

# Load automatically selected features
df_selected = loader.load_processed_data(which='selected_features')

# Re-run model with auto-selected features
robust_results = analysis.run_psm_did(
    df_selected,
    ps_vars=auto_selected_features,
    did_controls=auto_selected_features,
)

# Compare
effect_diff = abs(results['ate'] - robust_results['ate'])
print(f"Effect size difference: {effect_diff:.4f}")
print(f"Results robust: {effect_diff < 0.05 * abs(results['ate'])}")
```

---

## Migration Guide (If Using Old API)

### Old Code ❌
```python
selected_features, report = compile_selected_features(df, outcome_cols=['esg_score'])
df_selected = df[selected_features]
# Use selected features in PSM-DiD ← WRONG!
```

### New Code ✅
```python
# Define theory-driven specification
theory_vars = ['firm_size', 'leverage', 'sector']

# Validate with diagnostics
diagnostic_report = validate_specification(df, theory_vars, 'esg_score')
print(diagnostic_report)

# Use engineered data with manual selection
df_engineered = loader.load_processed_data(which='engineered')
# Use theory_vars in PSM-DiD ← CORRECT!
```

---

## When to Use Each Function

### use diagnose_multicollinearity() when:
- You want to check VIF for your specific variables
- You want to understand multicollinearity in your specification
- You're writing methods section (need to document checks)

### Use validate_specification() when:
- You want comprehensive diagnostic of your specification
- You want to validate theory-driven selection against data
- You want recommendations for model specification
- You're presenting results to collaborators

### Use compare_specifications() when:
- You're doing robustness checks
- You want to show that results don't depend on feature selection method
- You're writing appendix comparing multiple specifications

---

## ⚠️  Important Warnings

### ❌ DON'T: Use selected_features for primary PSM-DiD specification
```python
# WRONG
df_selected = df[selected_features]
results = analysis.run_psm_did(df_selected, ...)  # ❌ Biased!
```

### ✅ DO: Use engineered data with manual specification
```python
# RIGHT
df_engineered = load_processed_data(which='engineered')
results = analysis.run_psm_did(
    df_engineered,
    ps_vars=theory_driven_vars,  # ✅ Unbiased
    ...
)
```

### ✅ DO: Use diagnostics to validate your specification
```python
# RIGHT
report = validate_specification(df, theory_vars, 'esg_score')
print(report)  # Validates specification, shows robustness
```

---

## Example: Complete Workflow

```python
import pandas as pd
from asean_green_bonds.data import loader, analysis
from asean_green_bonds.data.feature_selection import validate_specification

# Step 1: Load engineered data
df = loader.load_processed_data(which='engineered')

# Step 2: Define theory-driven specification
ps_vars = ['firm_size', 'leverage', 'sector', 'profitability', 'issuer_track_record']
did_controls = ps_vars + ['lagged_esg_score', 'lagged_profitability']

# Step 3: Validate specification with diagnostics
print("=" * 60)
print("SPECIFICATION VALIDATION")
print("=" * 60)

report = validate_specification(
    df,
    theory_vars=ps_vars,
    outcome_col='esg_score',
    control_cols=ps_vars
)
print(report)

# Check for critical issues
if any(v > 10 for v in report.multicollinearity['VIF']):
    print("❌ Critical: VIF > 10. Review specification.")
else:
    print("✅ Specification validated. Proceeding with PSM-DiD.")

# Step 4: Run PSM-DiD
print("\n" + "=" * 60)
print("PSM-DiD ESTIMATION")
print("=" * 60)

results = analysis.run_psm_did(
    df,
    ps_vars=ps_vars,
    did_controls=did_controls,
    entity_fe=True,
    time_fe=True
)

print(f"Treatment effect: {results['ate']:.4f}")
print(f"95% CI: [{results['ci_lower']:.4f}, {results['ci_upper']:.4f}]")
```

---

## Summary

**Key Change:** Feature selection is now a **diagnostic tool** for validating theory-driven specifications, not a method for generating model specifications.

**Use diagnostic functions to:**
- ✅ Validate your theory-driven PSM-DiD variables
- ✅ Check data quality and multicollinearity
- ✅ Understand variable importance rankings
- ✅ Show robustness to alternative specifications
- ✅ Build methodological rigor

**NOT to:**
- ❌ Replace theory-driven variable selection
- ❌ Generate primary model specifications
- ❌ Substitute for domain expertise

This reflects econometric best practices where models are specified from **knowledge** (causal theory), not from **data** (statistical filters).
