# Methodology Data Flow Analysis: Feature Selection in Econometric Modeling

## Issue 1: Data Loading in 03_methodology_and_results.ipynb

### Current State
Cell 1 loads:
```python
df = data.load_processed_data(which='engineered')
```

This loads the **engineered features** (after feature engineering), NOT the **selected features** (after automatic feature selection from 02_feature_selection.ipynb).

### Available Data Versions
The pipeline produces 3 data versions:
1. **'cleaned'** - Basic data cleaning (missing values, outliers)
2. **'engineered'** (currently used) - Feature engineering (lags, interactions, ratios)
3. **'selected_features'** - After automatic feature selection (correlation, lasso, VIF filtering)

### Is This Correct?

✅ **YES - This is the CORRECT approach for econometric modeling.**

**Reasoning:**
- Feature selection from 02_feature_selection.ipynb uses **statistical/ML criteria** (correlation, lasso, VIF)
- PSM-DiD modeling requires **theoretically-informed model specification** from domain knowledge
- Automatically selected features may miss important causal variables
- Features excluded by statistical criteria might be crucial for matching/identification

---

## Issue 2: Do We Need Feature Selection for PSM-DiD?

### Short Answer
**❌ NO - Feature selection from 02_feature_selection.ipynb is NOT necessary for PSM-DiD econometric modeling.**

### Why Not?

#### 1. **Different Objectives**
| Step | Objective | Approach |
|------|-----------|----------|
| Feature Selection (02) | Maximize prediction accuracy | Data-driven statistical filters |
| PSM-DiD (03) | Estimate causal effects | Theory-driven model specification |

#### 2. **PSM-DiD Has Its Own Variable Selection Logic**

**Propensity Score Matching:**
- Uses a **matching specification** to estimate P(Treatment \| Covariates)
- You manually choose which covariates determine treatment assignment
- This is theory-driven, not data-driven

**DiD Specification:**
- You manually define:
  - Outcome variable(s)
  - Treatment variable
  - Fixed effects structure
  - Control variables
- Model is specified by researcher, not selected by algorithm

#### 3. **Risk of Automatic Feature Selection**

Automatic filters can **remove theoretically important variables**:

❌ **Removed but important** (low correlation but essential for identification):
- Geographic location (determines policy exposure)
- Industry sector (structural differences, not correlation with outcome)
- Institutional characteristics (governance, track record)
- Temporal controls (phase-in effects, regulatory changes)

❌ **Included but spurious** (high correlation but not causal):
- Lagged outcomes (mechanical correlation)
- Industry averages (not firm-specific effects)
- Collinear variables (multicollinearity problems)

---

## Recommended Data Flow for Your Analysis

### Current Notebooks
```
01_data_preparation.ipynb
    ↓ (engineered data)
02_feature_selection.ipynb ← Produces engineered + selected_features
    ↓
03_methodology_and_results.ipynb
    ↓ Uses: data.load_processed_data(which='engineered')
```

### Why Use 'engineered' Instead of 'selected_features'?

#### For PSM-DiD, you want:
1. ✅ **All engineered features** (01 → 02)
   - Lags for dynamic analysis
   - Ratios for standardization
   - Interactions for heterogeneity

2. ✅ **Manual variable selection** (in 03)
   - Based on causal theory
   - Domain expertise on green bonds
   - Econometric identification requirements

3. ❌ **NOT automatic feature selection** (from 02)
   - Could remove identification variables
   - Optimizes for prediction, not causality
   - May violate parallel trends assumption

### Recommended Code for 03_methodology_and_results.ipynb

**Current (correct):**
```python
df = data.load_processed_data(which='engineered')
```

**You can keep this.** Then define variables explicitly:

```python
# CAUSAL SPECIFICATION (theory-driven, not data-driven)

# Outcomes for impact analysis
outcome_vars = [
    'return_on_assets',     # Firm performance
    'Tobin_Q',              # Market valuation
    'esg_score',            # Environmental performance
    'carbon_intensity'      # Environmental impact
]

# Propensity score covariates (variables affecting treatment assignment)
ps_covariates = [
    'firm_size',            # Size affects issuance capacity
    'profitability',        # Profitability affects market access
    'asset_tangibility',    # Tangible assets as collateral
    'leverage',             # Debt levels
    'issuer_track_record',  # Previous bond issuance
    'has_green_framework',  # ESG commitment signaling
    'issuer_sector',        # Industry environmental relevance
    'issuer_nation'         # Country policy environment
]

# DiD parallel trends controls (pre-treatment characteristics)
did_controls = ps_covariates + [
    'lagged_esg_score',     # Pre-treatment environmental profile
    'lagged_roa',           # Pre-treatment performance trend
    'volatility',           # Risk profile
]

# Model specifications to try
specifications = {
    'psm_kernel': 'kernel matching with bandwidth selection',
    'psm_nn1': '1-to-1 nearest neighbor matching',
    'psm_nn5': '5-to-1 nearest neighbor matching',
    'did_fe': 'Two-way fixed effects (entity + time)',
    'did_wls': 'Weighted least squares on matched sample',
}
```

---

## What Should Notebook 02 (Feature Selection) Be Used For?

Feature selection IS valuable for:

### ✅ **Predictive Models** (ML/Forecasting)
- Predicting bond returns
- Forecasting ESG scores
- Machine learning classification (authentic vs greenwashed)

### ✅ **Exploratory Analysis**
- Understanding which variables correlate with outcomes
- Data quality diagnostics
- Reducing dimensionality for visualization

### ✅ **Sensitivity Analysis**
- Check robustness to alternative variable sets
- Compare causal results with/without selected features
- Test specification stability

### Current Use Case
Your 02_feature_selection.ipynb provides:
```python
selected_features, report = data.compile_selected_features(
    df,
    outcome_cols=outcomes,
    control_cols=controls,
    lagged_cols=lagged,
    selection_method='union'
)
```

**Best practice:** Use this for **robustness check** in 03:
```python
# Main specification (theory-driven)
results_main = analysis.run_multiple_outcomes(
    df[causal_variables],  # Manual selection
    outcomes=outcome_vars
)

# Robustness: Using automatically selected features
results_data_driven = analysis.run_multiple_outcomes(
    df[selected_features],  # From 02_feature_selection
    outcomes=outcome_vars
)

# Compare to show results are stable
```

---

## Summary & Recommendations

### ✅ Correct Approach (Current)
```
03 Uses: df = data.load_processed_data(which='engineered')
```
- ✓ Includes all feature engineering (lags, ratios, interactions)
- ✓ Does NOT force automatic feature selection
- ✓ Allows manual, theory-driven model specification
- ✓ Appropriate for causal inference (PSM-DiD)

### Recommended Changes

**In 03_methodology_and_results.ipynb:**
```python
# Current (correct)
df = data.load_processed_data(which='engineered')

# Optional: Document why you're NOT using selected_features
# This shows you understand the distinction between:
# - Feature selection (for prediction accuracy)
# - Model specification (for causal inference)

print("✓ Using engineered features (not automatically selected)")
print("  Reason: PSM-DiD requires theory-driven variable specification")
print("  Automatic selection optimizes prediction, not causality")
```

**In 02_feature_selection.ipynb:**
```python
# Add this section explaining when to use the output
print("""
FEATURE SELECTION OUTPUT USAGE:

For Predictive Models:
  df_selected = load_processed_data(which='selected_features')
  
For Causal Inference (PSM-DiD):
  df_engineered = load_processed_data(which='engineered')
  # Then manually specify variables based on theory
  
For Robustness Checks:
  # Compare causal results with/without automatically selected features
""")
```

---

## Conclusion

**Your current approach is correct.** The methodology notebook appropriately:
- ✅ Loads engineered data (not auto-selected)
- ✅ Uses manual variable specification
- ✅ Applies causal inference methods (PSM-DiD)
- ✅ Follows econometric best practices

The feature selection notebook (02) is still valuable for exploratory analysis and robustness checks, but should not be the primary data source for causal inference.
