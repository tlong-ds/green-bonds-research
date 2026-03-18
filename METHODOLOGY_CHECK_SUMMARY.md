# Methodology Check Summary: Two Questions Answered

## Question 1: Does 03 Load Processed Data or Selected Features?

### Finding
✅ **Notebook 03 correctly loads PROCESSED (ENGINEERED) DATA, not selected features**

```python
# Cell 1 of 03_methodology_and_results.ipynb
df = data.load_processed_data(which='engineered')
```

### Verification
- ✅ Using `which='engineered'` (correct)
- ✅ NOT using `which='selected_features'` (appropriate)
- ✅ Includes all feature engineering (lags, ratios, interactions)
- ✅ Preserves all variables for manual, theory-driven selection

---

## Question 2: Do We Need Feature Selection for PSM-DiD?

### Short Answer
**❌ NO - Feature selection (02) is NOT necessary for econometric modeling (03)**

### Why Not?

#### 1. Different Objectives
| Notebook 02 | Notebook 03 |
|-------------|------------|
| **Feature Selection** | **Causal Inference (PSM-DiD)** |
| Goal: Predict accurately | Goal: Estimate unbiased effects |
| Method: Data-driven filtering | Method: Theory-driven specification |
| Removes low-correlation variables | Includes all theoretical confounders |
| Optimizes for ML accuracy | Optimizes for causal identification |

#### 2. Econometric Principle
**Econometric models are specified from KNOWLEDGE, not from DATA:**

```
PSM Specification: "Which variables determine treatment assignment?"
                    → Theory from green bond financing literature
                    → NOT from correlation analysis

DiD Specification: "What pre-treatment characteristics ensure parallel trends?"
                   → Theory from economic mechanism
                   → NOT from automatic feature selection

Result: Manual variable selection is CORRECT
        Automatic selection is RISKY (could remove confounders)
```

#### 3. Risk of Automatic Selection
Removing low-correlation variables can introduce **omitted variable bias**:

```
Example: Green bond issuance impact on ESG scores

Automatic selection says:
  correlation(issuer_sector, esg_improvement) = 0.03 → REMOVE

But causally:
  issuer_sector → treatment assignment (green industries more likely)
  issuer_sector → outcome (structural differences in ESG progress)
  
Result: issuer_sector is a CONFOUNDER
        Removing it → BIASED CAUSAL ESTIMATES
```

---

## Assessment: Your Current Approach

### 03_methodology_and_results.ipynb

| Aspect | Current | Verdict |
|--------|---------|---------|
| **Data source** | `which='engineered'` | ✅ CORRECT |
| **Variable selection** | Manual (theory-driven) | ✅ CORRECT |
| **Methodology** | PSM-DiD | ✅ CORRECT |
| **Feature selection usage** | Not forced on causal models | ✅ CORRECT |

**Conclusion: ✅ Methodologically Sound**

---

## Proper Use of Each Notebook

### Notebook 01: Data Preparation
**Output:** Cleaned data, Engineered data
**Use:** Foundation for both feature selection AND causal inference

### Notebook 02: Feature Selection
**Output:** Automatically selected features
**Proper use cases:**
- ✅ Predictive modeling (ML, forecasting, classification)
- ✅ Exploratory analysis (understand variable importance)
- ✅ Robustness checks (compare with main specification)
- ❌ PRIMARY data source for causal inference

**Note:** Keep this notebook! It's valuable for multiple purposes.

### Notebook 03: Causal Inference
**Input:** Engineered data from Notebook 01
**Variable selection:** Manual, based on causal theory
**Methodology:** PSM-DiD econometric modeling
**NOT using:** Automatic feature selection (by design)

---

## Recommended: Add Explanatory Comment

**In 03_methodology_and_results.ipynb, Cell 1:**

```python
# Load engineered features (not automatically selected)
# Reasoning:
# - PSM-DiD requires theory-driven variable specification
# - Automatic feature selection optimizes for prediction, not causality
# - Manually select confounders by economic theory, not by correlation
# - This preserves identification assumptions (unconfoundedness, parallel trends)

df = data.load_processed_data(which='engineered')
print(f"✓ Loaded engineered features: {df.shape[0]} observations, {df.shape[1]} variables")
print("  Using manual specification for PSM-DiD causal inference")
```

---

## Optional: Use Feature Selection for Robustness

**Advanced practice** (not required, but good for rigor):

```python
# Main specification (theory-driven)
main_results = analysis.run_psm_did(
    df_engineered,
    ps_covariates=['theory', 'based', 'variables'],
    did_controls=['pre_treatment', 'characteristics'],
)

# Robustness check (automatic selection)
robustness_results = analysis.run_psm_did(
    df_selected,  # From notebook 02
    ps_covariates=selected_features_list,
    did_controls=selected_features_list,
)

# Compare
effect_diff = abs(main_results['ate'] - robustness_results['ate'])
if effect_diff < 0.05 * abs(main_results['ate']):
    print("✓ Results robust to variable selection")
else:
    print("⚠️ Results sensitive to specification; investigate")
```

---

## Key Takeaway

You have correctly distinguished between:
1. **Feature Selection** (statistical optimization for prediction)
2. **Econometric Specification** (theory-driven identification)

Your pipeline reflects this understanding:
- Notebook 02: Produces selected features (valuable for multiple purposes)
- Notebook 03: Uses engineered features with manual selection (correct for causal inference)

This is **best practice** for rigorous econometric research.

---

## Files Created for Reference

1. **METHODOLOGY_DATA_FLOW_ANALYSIS.md** (8 KB)
   - Detailed comparison of feature selection vs causal inference
   - When to use each dataset
   - Recommended code structure

2. **DATA_FLOW_QUICK_REFERENCE.md** (5 KB)
   - Visual summary of three datasets
   - Decision tree for choosing datasets
   - FAQ section

3. **CAUSAL_INFERENCE_BEST_PRACTICES.md** (8 KB)
   - Theory vs data-driven specification
   - Why automatic selection is risky
   - Examples and literature references

4. **METHODOLOGY_CHECK_SUMMARY.md** (THIS FILE)
   - Direct answers to both questions
   - Assessment of current approach
   - Recommendations for next steps

**Recommendation:** Review METHODOLOGY_DATA_FLOW_ANALYSIS.md for detailed explanation.
