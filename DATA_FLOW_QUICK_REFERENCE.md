# Data Flow Quick Reference: Which Dataset to Use

## Three Processed Datasets Available

```
Raw Data
   ↓
01_data_preparation.ipynb
   ↓
[1] CLEANED DATA
    ├─ Missing values handled
    ├─ Outliers winsorized
    ├─ Categories encoded
    └─ File: processed_data/data_cleaned.csv

[2] ENGINEERED DATA ← USE THIS FOR PSM-DiD
    ├─ All from Cleaned (above)
    ├─ Feature engineering added:
    │  ├─ Lagged variables (t-1, t-2, t-3)
    │  ├─ Ratio features (efficiency metrics)
    │  └─ Interaction terms
    └─ File: processed_data/data_engineered.csv

02_feature_selection.ipynb
   ↓
[3] SELECTED FEATURES (Automatic selection)
    ├─ All from Engineered (above)
    ├─ Filtered by:
    │  ├─ Correlation with outcome (r > 0.05)
    │  ├─ Lasso coefficients (non-zero)
    │  ├─ VIF < 10 (low multicollinearity)
    │  └─ Statistical significance
    ├─ Reduced dimensions
    └─ File: processed_data/data_selected_features.csv
```

## When to Use Each

### Use [1] CLEANED
- ✅ Basic exploratory data analysis
- ✅ Data quality diagnostics
- ✅ Summary statistics
- ✅ Initial regression checks

**Load code:**
```python
df = data.load_processed_data(which='cleaned')
```

---

### Use [2] ENGINEERED ← **FOR CAUSAL INFERENCE**
- ✅ PSM-DiD analysis (YOUR USE CASE)
- ✅ Event studies
- ✅ Dynamic effects (uses lags)
- ✅ Heterogeneous treatment effects
- ✅ Panel regressions with rich specifications
- ❌ NOT automatic variable selection

**Load code:**
```python
df = data.load_processed_data(which='engineered')  # ← Currently used in 03
```

**Why:** All features available for theory-driven selection. You manually choose variables based on:
- Causal theory
- Identification requirements
- Matching logic (for PSM)
- Parallel trends (for DiD)

---

### Use [3] SELECTED FEATURES
- ✅ Predictive modeling (ML, forecasting)
- ✅ High-dimensional problems
- ✅ Exploratory feature importance analysis
- ✅ Robustness checks (compare with engineered)
- ❌ NOT for causal inference (primary analysis)

**Load code:**
```python
df = data.load_processed_data(which='selected_features')
```

**Why:** Optimized for prediction accuracy, not causal identification.

---

## Your Analysis Status

### 03_methodology_and_results.ipynb
**Current:** ✅ Using ENGINEERED data
```python
df = data.load_processed_data(which='engineered')
```

**Assessment:** CORRECT for econometric modeling
- ✓ Includes all feature engineering
- ✓ Allows manual variable specification
- ✓ Appropriate for PSM-DiD identification
- ✓ Follows econometric best practices

**Explanation comment to add:**
```python
# Load engineered features (not auto-selected)
# Reason: PSM-DiD requires theory-driven variable specification
# Automatic selection optimizes prediction accuracy, not causal effects
df = data.load_processed_data(which='engineered')
```

---

## Decision Tree

```
What are you doing?

├─ Causal inference (PSM-DiD, IV, RDD)?
│  └─ Use [2] ENGINEERED ✓
│     └─ Manually select variables by theory
│
├─ Predictive modeling (classification, forecasting)?
│  └─ Use [3] SELECTED FEATURES ✓
│     └─ Use automatic selection (optimized for accuracy)
│
├─ Exploratory analysis (understand correlations)?
│  └─ Use [2] ENGINEERED ✓
│     └─ Look at relationships, not causality
│
└─ Comparison/Robustness checks?
   ├─ Main results: [2] ENGINEERED
   └─ Robustness check: [3] SELECTED FEATURES
```

---

## FAQ

**Q: Why NOT use selected features for PSM-DiD?**
A: Automatic selection removes low-correlation variables that may be:
- Essential for matching (geographic location, sector)
- Necessary for identification (confounders, instrumental variables)
- Important for controlling bias (pre-treatment characteristics)

**Q: Can I use selected features and still get valid causal inference?**
A: Potentially risky because:
- May violate unconfoundedness assumption
- Could introduce omitted variable bias
- Might fail parallel trends check
- But good for robustness testing

**Q: Should I modify notebook 02 (feature selection)?**
A: No - keep it as is. It's valuable for:
- Exploratory analysis
- Predictive modeling
- Robustness checks
- Understanding variable importance

**Q: Is feature selection step useless?**
A: Not useless - different use case:
- 02: For prediction accuracy
- 03: For causal inference
- Comparing them: shows specification stability

---

## Summary

| Aspect | Your Current Approach | Verdict |
|--------|----------------------|---------|
| Data loaded | 'engineered' | ✅ CORRECT |
| Variable selection method | Manual (theory-driven) | ✅ CORRECT |
| Methodology | PSM-DiD | ✅ CORRECT |
| Feature selection usage | Not forced on causal inference | ✅ CORRECT |

**Bottom line:** Your current setup is methodologically sound. Keep using engineered data with manual variable specification for causal inference.
