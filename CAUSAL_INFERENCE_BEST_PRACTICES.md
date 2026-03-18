# Causal Inference Best Practices: Why Feature Selection ≠ Econometric Specification

## The Fundamental Distinction

### Feature Selection (Statistical/ML Approach)
```
Goal: Maximize Prediction Accuracy
Method: Data-driven filtering
Criteria: Correlation, lasso coefficients, VIF, statistical significance
Output: Minimalist model (only high-signal features)
Best for: ML, forecasting, classification
```

### Econometric Specification (Theory-Driven Approach)
```
Goal: Estimate Unbiased Causal Effects
Method: Theory-guided variable selection
Criteria: Causal theory, identification requirements, domain knowledge
Output: Rich model (all necessary causal variables)
Best for: Causal inference, policy evaluation, mechanism understanding
```

---

## Key Principle: Omitted Variable Bias vs Overfitting

### Feature Selection Problem
Automatically selected models can remove important variables:

```
Low-correlation variables removed: 
❌ Geographic location (policy exposure)
❌ Industry sector (structural differences)
❌ Pre-treatment characteristics (parallel trends)
❌ Instrumental variables (identification)

Result: OMITTED VARIABLE BIAS in causal estimates
```

### Econometric Specification Problem
Including too many variables causes:

```
High-dimensional noise included:
❌ Mechanical correlations (lagged outcome)
❌ Collinear variables (multicollinearity)
❌ Post-treatment variables (bad controls)

Result: INEFFICIENCY and BIAS in causal estimates
```

**Solution:** Balance is domain-specific, not data-driven.

---

## Your Three-Notebook Pipeline

### Notebook 01: Data Preparation
```
Cleaned Data (foundation)
├─ Handle missing values
├─ Winsorize outliers
├─ Encode categories
├─ Check distributions
└─ ✅ Ready for both feature selection AND econometric modeling
```

### Notebook 02: Feature Selection
```
Engineered Data → Automatic Filtering → Selected Features Data
├─ Feature engineering (lags, ratios, interactions)
├─ Correlation filtering (remove low-signal variables)
├─ Lasso (remove zero-coefficient variables)
├─ VIF check (remove multicollinear variables)
└─ Output: Optimized for prediction accuracy
   ├─ Useful for: ML models, predictive tasks
   ├─ Good for: Exploratory analysis, variable importance
   └─ ⚠️ Risky for: Causal inference (could remove confounders)
```

### Notebook 03: Causal Inference (YOUR ANALYSIS)
```
Engineered Data → Manual Variable Selection → Causal Models
├─ Keep all engineered features (lags, ratios, interactions)
├─ Manually select by causal theory:
│  ├─ PSM specification: confounders only
│  ├─ DiD specification: pre-treatment characteristics + confounders
│  └─ Event study: control variables for market effects
├─ Output: Unbiased causal effects
└─ NOT using automatic feature selection:
   ├─ Preserves all confounders
   ├─ Maintains identification assumptions
   └─ Follows econometric best practices
```

---

## Specific Recommendation: Your PSM-DiD Analysis

### ✅ DO: Theory-Driven Variable Selection

**For Propensity Score Matching:**
```python
# Manual selection based on theory
# "What variables determine treatment assignment?"
ps_variables = [
    'firm_size',           # Financial capacity
    'profitability',       # Market access
    'leverage',            # Debt constraints
    'prior_bonds',         # Experience
    'sector',              # Industry characteristics
    'nation',              # Country policy
    'has_esg_framework',   # Commitment signal
]

# Estimate propensity score with your chosen variables
df['ps'] = estimate_propensity_score(
    df,
    covariates=ps_variables,
    treatment='issued_green_bond'
)
```

**For Difference-in-Differences:**
```python
# Manual selection based on theory
# "What pre-treatment characteristics ensure parallel trends?"
did_controls = [
    'lagged_esg_score',      # Pre-treatment environmental profile
    'lagged_profitability',  # Pre-treatment performance trend
    'firm_size',             # Scale effects
    'leverage',              # Financial structure
    'volatility',            # Risk profile
]

# Estimate treatment effect controlling for confounders
results = run_did(
    df,
    outcome='esg_score',
    treatment='issued_green_bond',
    controls=did_controls,
    entity_fe=True,
    time_fe=True
)
```

### ❌ DON'T: Automatic Feature Selection for PSM-DiD

```python
# ⚠️ NOT RECOMMENDED for causal inference
selected_vars = compile_selected_features(df)  # From notebook 02

df['ps'] = estimate_propensity_score(
    df,
    covariates=selected_vars,  # ❌ Risky!
    treatment='issued_green_bond'
)
# Problems:
# - May exclude confounders (low correlation but necessary)
# - Could violate unconfoundedness assumption
# - Optimizes for prediction, not causal identification
# - No guarantee of parallel trends
```

---

## Why "Low-Correlation Variables" Can Be Critical Confounders

### Example: Green Bond Issuance

**Scenario:** Study whether issuing green bonds improves ESG scores

**Automatic Feature Selection says:**
```
correlation(issuer_sector, esg_improvement) = 0.03 (low)
→ Remove issuer_sector from model
```

**But causal theory says:**
```
issuer_sector → green_bond_issuance (companies in green industries
                                     more likely to issue)
issuer_sector → esg_improvement (structural industry differences
                                in ESG progress)

Result: issuer_sector is a CONFOUNDER
        Removing it → BIASED CAUSAL ESTIMATES
```

**PSM-DiD solution:** Include sector in both matching AND control variables

---

## Robustness Checks: Best Practices

### Main Specification (Theory-Driven)
```python
# Your primary results using manual variable selection
main_results = run_did(
    df_engineered,
    controls=['manual', 'theoretical', 'variables'],
    entity_fe=True,
    time_fe=True
)
print(f"Main effect: {main_results['ate']:.4f}")
```

### Robustness Check (Automatic Selection)
```python
# Compare against automatically selected features
# Shows your results are stable
robustness_results = run_did(
    df_selected_features,  # From notebook 02
    controls=selected_feature_list,
    entity_fe=True,
    time_fe=True
)
print(f"Robustness effect: {robustness_results['ate']:.4f}")

# Report both
print(f"Difference: {abs(main_results['ate'] - robustness_results['ate']):.4f}")
```

**Interpretation:**
- If effects similar: ✅ Results robust to variable selection
- If effects differ: ⚠️ Investigate why; update specification

---

## Summary: Your Analysis Approach

| Question | Your Approach | Assessment |
|----------|---------------|------------|
| **Data source?** | Engineered (not selected) | ✅ CORRECT |
| **Variable selection?** | Manual + theory-driven | ✅ CORRECT |
| **Methodology?** | PSM-DiD | ✅ CORRECT |
| **Follows econometric best practices?** | Yes | ✅ CORRECT |

### Green Light: You're good to proceed with 03_methodology_and_results.ipynb

Keep the current approach:
```python
df = data.load_processed_data(which='engineered')
# Then manually select variables based on causal theory
```

This is methodologically sound for econometric analysis.

---

## Additional Resources

### Literature Supporting This Approach
1. **Angrist & Pischke (2009)** "Mostly Harmless Econometrics"
   - Chapter on variable selection for causal inference
   - Why automatic selection is risky

2. **Rotnitzky & Vansteelandt (2010)**
   - Double robustness in causal inference
   - When to include variables vs exclude them

3. **Pearl (2009)** "Causality"
   - Causal graphs and variable selection
   - Backdoor criterion for confounder identification

### R/Python Implementation
- **causalml library**: Causal models (PSM, CATE, etc.)
- **statsmodels**: DiD and FE regression
- **econml library**: Heterogeneous treatment effects
- **linearmodels**: Panel data models with fixed effects

---

## Conclusion

✅ **Your current pipeline is methodologically correct.**

The distinction between:
- **Feature selection** (notebook 02): For prediction
- **Econometric specification** (notebook 03): For causal inference

...shows sophisticated understanding of econometric methodology.

Keep using engineered data with manual, theory-driven variable selection for PSM-DiD analysis. The feature selection notebook remains valuable for exploratory analysis and robustness checks.
