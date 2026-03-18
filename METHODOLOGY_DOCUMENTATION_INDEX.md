# Methodology Documentation Index

## Quick Answer: Your Questions

### Q1: Does 03_methodology load processed data or selected features?
**A: ✅ CORRECT - Loads engineered (processed) data, not auto-selected features**
- Code: `df = data.load_processed_data(which='engineered')`
- Why: Preserves all variables for theory-driven PSM-DiD specification
- Best practice: Exactly what econometric modeling requires

### Q2: Do we need feature selection for PSM-DiD?
**A: ❌ NO - Feature selection (02) is NOT required for causal inference (03)**
- Feature selection: Optimizes for prediction accuracy
- PSM-DiD: Requires theory-driven variable specification
- Risk of auto-selection: Could remove confounders → biased estimates
- Recommendation: Keep notebook 02 for exploratory analysis, robustness checks

---

## Documentation Files (Start Here)

### 1. **METHODOLOGY_SUMMARY.txt** ← START HERE
**Best for:** Quick overview in plain text
- 2-minute read
- Direct answers to both questions
- Key econometric principles
- Visual comparison table
- Bottom line: Your approach is correct

**File size:** 8 KB

---

### 2. **METHODOLOGY_CHECK_SUMMARY.md** ← SECOND BEST
**Best for:** Detailed but concise markdown format
- Answers with supporting evidence
- Assessment of current approach
- Proper use of each notebook
- Optional robustness improvements
- Recommended comments to add

**File size:** 6.1 KB

---

### 3. **DATA_FLOW_QUICK_REFERENCE.md**
**Best for:** Visual learners, decision making
- Three dataset comparison
- Decision tree ("What are you doing?")
- When to use each dataset
- FAQ section
- Summary table

**File size:** 4.9 KB

---

### 4. **METHODOLOGY_DATA_FLOW_ANALYSIS.md** ← MOST DETAILED
**Best for:** Deep understanding, implementation guidance
- Complete technical framework
- Risk analysis of automatic feature selection
- Recommended code structure for 03
- How to use 02 output properly
- Sensitivity analysis patterns

**File size:** 8.3 KB

---

### 5. **CAUSAL_INFERENCE_BEST_PRACTICES.md** ← FOR THEORY
**Best for:** Econometric methodology, literature background
- Fundamental distinction (feature selection vs specification)
- Omitted variable bias explanation
- PSM-DiD specification logic
- Literature references (Angrist, Pearl, etc.)
- Advanced robustness patterns

**File size:** 8.3 KB

---

## The Three Datasets Explained

```
[1] CLEANED DATA
    └─ From: 01_data_preparation.ipynb
    ├─ Handles: missing values, outliers, categories
    └─ Use for: EDA, diagnostics, baseline checks

[2] ENGINEERED DATA ← YOU ARE USING THIS (CORRECT)
    └─ From: 01_data_preparation.ipynb (feature engineering step)
    ├─ Adds: lags, ratios, interactions
    ├─ All variables preserved (no filtering)
    └─ Use for: Causal inference (PSM-DiD) via theory-driven selection

[3] SELECTED FEATURES
    └─ From: 02_feature_selection.ipynb
    ├─ Filters: correlation, lasso, VIF
    ├─ Optimized for: prediction accuracy
    └─ Use for: ML models, exploratory analysis, robustness checks
                (NOT primary analysis for causal inference)
```

---

## Quick Decision Guide

**Are you doing causal inference (PSM-DiD)?**
- ✅ YES → Use ENGINEERED data
- ✅ Manually select variables by theory
- ✅ You're on the right track

**Are you doing predictive modeling (ML/forecasting)?**
- ✅ YES → Use SELECTED FEATURES data
- ✅ Use automatic feature selection
- ✅ Optimize for prediction accuracy

**Are you doing robustness checks?**
- ✅ Main spec: Use ENGINEERED data with theory-driven selection
- ✅ Robustness: Use SELECTED FEATURES for comparison
- ✅ Compare results to show stability

---

## Key Econometric Principles

### Principle 1: Knowledge-Based Specification
> Econometric models are specified from KNOWLEDGE, not from DATA

**Implication:**
- PSM covariates: Choose based on theory of treatment assignment
- DiD controls: Choose based on parallel trends assumption
- NOT: "Which variables have high correlation?"

### Principle 2: Confounder Definition
> A variable is a confounder if it affects both treatment AND outcome

**Implication:**
- Low-correlation confounders still cause bias
- Auto-selection can remove critical confounders
- Must use theory to identify confounders, not correlation

### Principle 3: Identification vs Accuracy
> Feature selection optimizes accuracy; causal inference requires identification

**Implication:**
- Fewer variables → Better predictions (ML)
- More (correct) variables → Unbiased estimates (causal)
- Different optimization goals → Different variable selection logic

---

## Your Current Status

### ✅ Correct
- Data source: Engineered (preserved all variables)
- Variable selection: Manual (theory-driven, not auto)
- Methodology: PSM-DiD (econometric, not ML)
- Feature selection role: Exploratory + robustness (not primary)

### Optional Improvements
1. Add explanatory comment in 03 Cell 1 explaining data choice
2. Implement robustness check comparing engineered vs selected features
3. Document variable selection rationale by economic theory

### No Changes Required
Your approach already follows best practices for rigorous econometric research.

---

## How to Use These Documents

### For Quick Reference
→ Read **METHODOLOGY_SUMMARY.txt** (5 min)

### For Implementation
→ Read **DATA_FLOW_QUICK_REFERENCE.md** (10 min)

### For Understanding the Logic
→ Read **METHODOLOGY_DATA_FLOW_ANALYSIS.md** (15 min)

### For Deep Theoretical Background
→ Read **CAUSAL_INFERENCE_BEST_PRACTICES.md** (20 min)

### For Detailed Answers
→ Read **METHODOLOGY_CHECK_SUMMARY.md** (12 min)

---

## Files Reference

| Document | Size | Best For | Read Time |
|----------|------|----------|-----------|
| METHODOLOGY_SUMMARY.txt | 8 KB | Quick overview | 5 min |
| DATA_FLOW_QUICK_REFERENCE.md | 4.9 KB | Visual guide | 10 min |
| METHODOLOGY_CHECK_SUMMARY.md | 6.1 KB | Detailed answers | 12 min |
| METHODOLOGY_DATA_FLOW_ANALYSIS.md | 8.3 KB | Deep understanding | 15 min |
| CAUSAL_INFERENCE_BEST_PRACTICES.md | 8.3 KB | Econometric theory | 20 min |

**Total documentation:** ~35 KB, ~1 hour to read all

---

## Bottom Line

✅ **Your current approach is methodologically correct.**

You have appropriately distinguished between:
- Feature selection (optimize prediction accuracy)
- Econometric specification (estimate unbiased causal effects)

This shows sophisticated understanding of econometric methodology and reflects best practices in causal inference research.

**Proceed with confidence with 03_methodology_and_results.ipynb using engineered data and theory-driven variable selection.**

---

## Next Steps

1. **Immediate:** Review METHODOLOGY_SUMMARY.txt (5 min)
2. **Before running 03:** Read DATA_FLOW_QUICK_REFERENCE.md (10 min)
3. **Optional:** Add comment to 03 Cell 1 explaining data choice
4. **After getting results:** Consider robustness check with selected features
5. **When writing up:** Reference CAUSAL_INFERENCE_BEST_PRACTICES.md for methodology section

---

Created: 2026-03-18
Status: Complete and ready for use
Confidence: High (follows econometric best practices)
