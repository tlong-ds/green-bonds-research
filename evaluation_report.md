# Code Evaluation Report: ASEAN Green Bonds Research (2015-2025)

## 1. Executive Summary
This report evaluates the data preparation and econometric modeling pipeline for the research project "The Impact of Green Bond Issuance on Corporate Financial Performance in ASEAN Listed Companies." While the pipeline demonstrates strong technical foundations in panel data handling and statistical integrity (clustered errors, fixed effects), there are critical "handicaps" regarding selection bias control and greenwashing differentiation that must be addressed to ensure academic rigor.

---

## 2. Bias Detection & Data Integrity

### 2.1 Survivorship Bias
- **Finding:** The data extraction script (`prepare_data.py`) processes companies from a static Excel file (`data2802.xlsx`). 
- **Handicap:** If the source Excel file contains only currently listed firms (as of 2025/2026), the dataset suffers from **Survivorship Bias**. Firms that were active in 2015 but were delisted, went bankrupt, or were acquired before the data was pulled are likely excluded. This can lead to overestimating the positive impact of green bonds if only "survivors" are analyzed.
- **Recommendation:** Verify if the source list includes historical constituents. If not, acknowledge this limitation in the methodology.

### 2.2 Greenwashing Bias
- **Finding:** The model treats all green bond issuances as a single "Treatment" group (`is_issuer`).
- **Handicap:** The research outline emphasizes the importance of **Certification (CBI)** to differentiate between high-integrity bonds and "self-labeled" ones. The current code lacks a dummy variable for certified bonds. This prevents testing whether the "Greenium" or financial performance benefits are restricted to certified issuers, which is a core hypothesis (H3) in the outline.
- **Recommendation:** Integrate the Climate Bonds Initiative (CBI) certification status into `greenbonds.csv` and add a `is_certified` dummy to the DiD model.

---

## 3. Model Robustness & Econometrics

### 3.1 PSM Matching Quality
- **Finding:** In `methodology-and-result.ipynb`, the Propensity Score Matching (PSM) code is currently **commented out** (Cell 2). The model uses the full sample (`df_matched = df`) instead of a matched control group.
- **Handicap:** This leaves the results highly vulnerable to **Selection Bias**. Green bond issuers are likely larger and more profitable *before* issuance. Without matching, the DiD estimator may capture pre-existing trends rather than the treatment effect.
- **Recommendation:** Uncomment and finalize the PSM implementation. Specifically, audit the "common support" region and provide a balance table (Standardized Mean Differences) to prove matching quality.

### 3.2 Feature Selection (Lasso)
- **Strength:** The use of **LassoCV with GroupKFold** (`feature_selection_refined.py`) to select lagged covariates is an excellent approach to avoid overfitting and address endogeneity.
- **Strength:** Mean-centering of interaction terms (Firm Size x GB) effectively reduced VIF, ensuring the reliability of interaction coefficients.

---

## 4. Statistical Integrity

### 4.1 Clustered Standard Errors
- **Finding:** The regression models in `methodology-and-result.ipynb` correctly utilize **Clustered Standard Errors at the firm level** (`cov_type='clustered'`).
- **Impact:** This accounts for serial correlation within panel units, preventing the artificial deflation of p-values. This is a high-signal indicator of statistical rigor.

### 4.2 ESG Disclosure "Handicap"
- **Finding:** The sparse nature of ESG disclosures across ASEAN markets (e.g., Vietnam vs. Singapore) is addressed via an `esg_disclosure` dummy.
- **Observation:** Currently, the `esg_score` target in the DiD model shows insignificant results. This is expected given the inconsistent reporting rates identified in the exploratory data analysis.

---

## 5. Conclusion & Actionable Next Steps

| Priority | Task | Rationale |
| :--- | :--- | :--- |
| **High** | **Re-enable PSM** | Essential to control for selection bias between issuers and non-issuers. |
| **High** | **Certification Dummy** | Critical to address the Greenwashing hypothesis and validate H3. |
| **Medium** | **Survivorship Check** | Ensure the firm list isn't biased towards 2025 survivors. |
| **Medium** | **Dynamic DiD Plot** | Generate an Event Study plot with coefficients for years $T-3$ to $T+3$ to formally test Parallel Trends. |

**Final Verdict:** The codebase provides a solid infrastructure for panel analysis, but the causal claims are currently weakened by the lack of matched controls and the absence of greenwashing diagnostics. Addressing these two points will significantly elevate the research's credibility.
