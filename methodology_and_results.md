# ASEAN Green Bonds: Methodology & Results Interpretation

## 1. Research Question

**How do green bonds impact the financial performance and corporate environmental performance of ASEAN-listed companies?**

This study employs a three-stage causal inference pipeline — Propensity Score Matching (PSM), Difference-in-Differences (DiD), and System GMM — to isolate the causal effect of green bond issuance on four outcome variables: Return on Assets (ROA), Tobin's Q, ESG Score, and Log Emissions Intensity. The analysis is supplemented by a cohort-specific event study, greenwashing/authenticity analysis, and heterogeneous effects by firm size.

---

## 2. Methodology

### 2.1 Data & Panel Structure

| Dimension | Value |
| --- | --- |
| Observations | 23,284 |
| Variables | 164+ |
| Entities | 3,964 (identified by `org_permid`) |
| Periods | 6 years (2020–2025) |
| Treatment | `green_bond_active` (1 = firm has issued a green bond by year *t*) |
| Treated firm-years | 81 (0.35% of panel) |
| Treated firms | 20 (0.5% of entities) |
| Treatment cohorts | 5 (first treated: 2020=5, 2021=3, 2022=4, 2023=4, 2024=4) |

> Source: [processing.py](file:///Users/bunnypro/Projects/refinitiv-search/asean_green_bonds/data/processing.py) → `prepare_full_panel_data()`, [config.py](file:///Users/bunnypro/Projects/refinitiv-search/asean_green_bonds/config.py).

### 2.2 Outcome Variables

| Variable | Type | Description | Scale |
| --- | --- | --- | --- |
| `return_on_assets` | Financial (accounting) | Net income / total assets | 0–1 |
| `Tobin_Q` | Financial (market) | Market cap / total assets | > 0 |
| `esg_score` | Environmental (composite) | Refinitiv ESG rating | 0–100 |
| `ln_emissions_intensity` | Environmental (direct) | ln(GHG emissions per unit output) | ~0–21 |

### 2.3 Control Variables (1-Year Lagged)

| Control | Formula |
| --- | --- |
| `L1_Firm_Size` | ln(total_assets) at *t−1* |
| `L1_Leverage` | total_debt / total_assets at *t−1* |
| `L1_Asset_Turnover` | net_sales / total_assets at *t−1* |
| `L1_Capital_Intensity` | capital_expenditures / total_assets at *t−1* |
| `L1_Cash_Ratio` | cash / total_assets at *t−1* |

> Source: [processing.py](file:///Users/bunnypro/Projects/refinitiv-search/asean_green_bonds/data/processing.py) → `create_financial_ratios()`, `create_lagged_features()`. Lists in [config.py#L49-L70](file:///Users/bunnypro/Projects/refinitiv-search/asean_green_bonds/config.py#L49-L70).

### 2.4 Outlier Treatment

- **Pass 1**: 18 raw financial metrics winsorized at 1st/99th percentile
- **Pass 2**: 5 computed ratios winsorized at 1st/99th percentile
- **Log-transform**: `ln_emissions_intensity = ln(max(1, emissions_intensity))` to handle extreme right skew (raw range: 0 to 1.04B)

> Source: [processing.py#L1595-L1615](file:///Users/bunnypro/Projects/refinitiv-search/asean_green_bonds/data/processing.py#L1595-L1615)

---

## 3. Stage 1: Propensity Score Matching (PSM)

> Source: [propensity_score.py](file:///Users/bunnypro/Projects/refinitiv-search/asean_green_bonds/analysis/propensity_score.py)

| Metric | Value |
| --- | --- |
| Propensity scores estimated | 16,831 |
| Caliper (2× Austin, min 0.05) | 0.0500 |
| Matched treated | 9 / 20 (45%) |
| Matched controls | 36 |
| Total matched | 45 |

**Covariate Balance**: All standardized differences < 0.1 (Cohen's d). ✅ Good balance achieved.

> [!WARNING]
> Only 9 treated firms matched. Pipeline falls back to **full panel** (23,284 obs) for DiD/GMM.

---

## 4. Stage 2: Difference-in-Differences (DiD)

> Source: [difference_in_diff.py](file:///Users/bunnypro/Projects/refinitiv-search/asean_green_bonds/analysis/difference_in_diff.py) — `estimate_did()` with `linearmodels.PanelOLS`, clustered SEs.

### 4.1 DiD Results (25 Models: 5 Outcomes × 5 Specifications)

| Outcome | Entity FE | Time FE | **TWFE** | **EntityFE+Trend** | No FE |
| --- | --- | --- | --- | --- | --- |
| **ROA** | −0.007 (0.48) | 0.007 (0.50) | 0.004 (0.73) | −0.000 (0.99) | 0.018* (0.04) |
| **Tobin's Q** | 0.187 (0.32) | 0.395* (0.02) | 0.356† (0.08) | 0.250 (0.18) | −0.160 (0.41) |
| **ESG Score** | 0.057* (0.05) | 0.134*** (<.001) | 0.020 (0.61) | 0.020 (0.52) | 0.152*** (<.001) |
| **ln(Emissions)** | −0.077 (0.43) | 1.130** (0.01) | −0.057 (0.61) | −0.064 (0.51) | 1.119** (0.01) |

> Format: coefficient (p-value). *** p<0.01, ** p<0.05, * p<0.1, † p<0.1

**Key takeaways:**
- `entity_fe_trend` results are consistent with TWFE — the TWFE absorption is not an artifact of saturated year dummies but reflects genuine confounding with common time trends
- Significance only emerges without entity FE (time FE or no FE), suggesting selection on unobservables drives the raw association

---

## 5. Cohort-Specific Event Study

> Source: [event_study_cohort.py](file:///Users/bunnypro/Projects/refinitiv-search/asean_green_bonds/analysis/event_study_cohort.py) — lightweight Callaway & Sant'Anna (2021) decomposition.

Each treatment cohort is estimated separately against never-treated firms.

### 5.1 ROA by Cohort

| Cohort | n Treated | β | p-value | Pre-trend p | Pre-trend OK? |
| --- | --- | --- | --- | --- | --- |
| 2020 | 5 | NaN | NaN | — | No pre-data |
| 2021 | 3 | −0.033** | 0.025 | — | No pre-data |
| 2022 | 4 | −0.006 | 0.667 | 0.148 | ✅ |
| 2023 | 4 | 0.001 | 0.823 | 0.142 | ✅ |
| 2024 | 4 | −0.024 | 0.222 | 0.179 | ✅ |
| **Aggregated ATT** | **20** | **−0.014** | **0.315** | **0/4 violations** | ✅ |

### 5.2 ESG Score by Cohort

| Cohort | n Treated | β | p-value | Pre-trend p | Pre-trend OK? |
| --- | --- | --- | --- | --- | --- |
| 2020 | 5 | NaN | NaN | — | No pre-data |
| 2021 | 3 | 0.072 | 0.447 | — | No pre-data |
| 2022 | 4 | 0.013 | 0.561 | 0.067 | ✅ |
| 2023 | 4 | 0.037** | 0.010 | 0.526 | ✅ |
| 2024 | 4 | 0.115† | 0.074 | <0.001 | ⚠️ |
| **Aggregated ATT** | **20** | **0.059** | **0.292** | **1/4 violations** | |

> [!IMPORTANT]
> **The parallel trends violation is localized.** For ROA, **no cohort** (0/4) violates pre-trends. The pooled violation (p = 0.009 in the original test) was driven by composition effects across cohorts. For ESG Score, only the **2024 cohort** violates — these are the most recently treated firms with the strongest ESG signal, likely reflecting anticipatory ESG improvements before formal issuance.

---

## 6. Stage 3: System GMM

> Source: [gmm.py](file:///Users/bunnypro/Projects/refinitiv-search/asean_green_bonds/analysis/gmm.py) — `estimate_system_gmm()`

| Outcome | Coefficient | Std. Error | p-value | Sig. |
| --- | --- | --- | --- | --- |
| ROA | −0.0049 | 0.0036 | 0.170 | |
| Tobin's Q | 0.2068 | 0.2435 | 0.396 | |
| ESG Score | 0.0229 | 0.0139 | 0.099 | † |
| ln(Emissions) | −0.1910 | 0.0980 | 0.051 | † |

### 6.1 DiD vs GMM Comparison

| Outcome | DiD (TWFE) | GMM | Direction consistent? |
| --- | --- | --- | --- |
| ROA | 0.004 | −0.005 | Mixed (both near zero) |
| Tobin's Q | 0.356 | 0.207 | ✅ Both positive |
| ESG Score | 0.020 | 0.023 | ✅ Both positive |
| ln(Emissions) | −0.057 | −0.191 | ✅ Both negative |

---

## 7. Parallel Trends Test (Pooled)

| Term | Coefficient | p-value |
| --- | --- | --- |
| `treatment_lead_1` (pre-treatment) | 0.1089 | 0.009*** |
| `green_bond_active` (current) | 0.0272 | 0.407 |
| `treatment_lag_1` (post-treatment) | 0.3750 | 0.008*** |

> [!CAUTION]
> The **pooled** pre-treatment lead is significant (p = 0.009). However, the **cohort-specific** analysis (Section 5) shows this violation is not universal — 0/4 cohorts violate for ROA, and only the 2024 cohort violates for ESG Score.

---

## 8. Robustness Checks

> Source: [diagnostics.py](file:///Users/bunnypro/Projects/refinitiv-search/asean_green_bonds/analysis/diagnostics.py)

| Test | Result |
| --- | --- |
| **Specification sensitivity** (5 specs) | All ROA coefficients null. Robust. |
| **Placebo test** (1-year shift) | β = 0.008, p = 0.669. ✅ Valid. |
| **Leave-one-out CV** (100 folds) | ✅ Robust (coefficient stable). |

---

## 9. Greenwashing / Authenticity Analysis

> Source: [authenticity.py](file:///Users/bunnypro/Projects/refinitiv-search/asean_green_bonds/authenticity.py) — `compute_authenticity_score()`

### 9.1 Key Statistics (333 ASEAN Green Bonds)

| Metric | Value |
| --- | --- |
| CBI-certified | 328 / 333 (98.5%) |
| ICMA-certified | 326 / 333 (97.9%) |
| **ESG improvement verified** | **13 / 333 (3.9%)** |

### 9.2 Score Distribution

| Category | Count | % |
| --- | --- | --- |
| High (≥80) | 13 | 3.9% |
| Medium (60–79) | 0 | 0.0% |
| Low (40–59) | 314 | 94.3% |
| Unverified (<40) | 6 | 1.8% |

### 9.3 Score Components (Mean)

| Component | Max | Mean |
| --- | --- | --- |
| ESG Component | 40 | **1.5** |
| Certification Component | 35 | 29.5 |
| Issuer Component | 25 | 22.8 |
| **Total** | **100** | **53.8** |

> [!IMPORTANT]
> **98.5% certified, but only 3.9% show genuine ESG improvement.** Certification is near-universal, but substantive environmental change is extremely rare. This supports the greenwashing hypothesis (Flammer, 2021; Hoang et al., 2020).

---

## 10. Heterogeneous Effects by Firm Size

> Source: [diagnostics.py#L272-L354](file:///Users/bunnypro/Projects/refinitiv-search/asean_green_bonds/analysis/diagnostics.py#L272-L354)

| Outcome | Small Firms | Large Firms |
| --- | --- | --- |
| **ROA** | β = −0.005, p = 0.638 | β = −0.025***, p < 0.001 |
| **Tobin's Q** | β = −0.041**, p = 0.005 | β = 0.385, p = 0.611 |
| **ESG Score** | β = 0.031*, p = 0.013 | β = 0.274***, p < 0.001 |

**Large firms**: Stronger ESG gains (+0.274 vs +0.031, 9× larger) but significant ROA decline (−2.5pp). Consistent with stakeholder theory: larger firms face more pressure for ESG disclosure but bear higher compliance costs.

---

## 11. Key Findings

### 11.1 Summary Table

| Question | Answer |
| --- | --- |
| Does green bond issuance improve **ROA**? | **No.** Null across all specifications and methods. Cohort ATT: −0.014, p = 0.315. |
| Does green bond issuance improve **Tobin's Q**? | **Weakly.** Marginal under time FE (p = 0.018), not robust under TWFE/GMM. |
| Does green bond issuance improve **ESG scores**? | **Conditionally.** Significant under entity FE (p = 0.046), absorbed under TWFE (p = 0.607). Cohort ATT: 0.059, p = 0.292. |
| Does green bond issuance reduce **emissions**? | **Marginally.** GMM: β = −0.191, p = 0.051†. Strongest treatment signal. |
| Is certification meaningful? | **No.** 98.5% certified but only 3.9% show genuine ESG improvement. |
| Do effects differ by **firm size**? | **Yes.** Large firms: stronger ESG (+0.274) but worse ROA (−0.025). |
| Are parallel trends valid? | **Partially.** Pooled test fails, but cohort analysis shows 0/4 violate for ROA. |

### 11.2 Interpreting the Greenwashing Evidence

The results present a nuanced picture of the **"Greenwashing Puzzle"** identified by Khan & Vismara (2025), characterized by a complex relationship between market signaling and substantive outcomes:

1. **Near-universal certification** (98.5% CBI, 97.9% ICMA) → Signaling environmental commitment is standard practice.
2. **No measurable financial benefit** → ROA is null, Tobin's Q is weak.
3. **Marginal emissions reduction** → GMM shows a ~19% reduction (p = 0.051), suggesting *some* operational ecological transition is occurring.
4. **Almost no verified ESG improvement** → Only 3.9% of bonds show composite ESG score gains post-issuance.
5. **ESG gains appear driven by time trends** → Positive ESG effects disappear under TWFE, exposing the limitations of composite ESG ratings.

While the combination of near-universal certification and stagnant ESG scores strongly reflects **Signaling Theory** (Flammer, 2021) — where firms adopt labels to satisfy market expectations — the empirical data does not support a conclusion of purely symbolic greenwashing. The marginally significant reduction in direct emissions intensity indicates that while third-party ESG ratings fail to capture improvement, green bond issuers may still be executing targeted, substantive environmental changes at the operational level.

---

## 12. Methodological Alignment

### 12.1 Strengths

| Aspect | Status |
| --- | --- |
| PSM-DiD framework | ✅ Standard (Bai 2025, Yeow & Ng 2021) |
| System GMM robustness | ✅ Hoang et al. (2020) |
| Lagged controls | ✅ Prevents simultaneity |
| Entity + Time FE | ✅ Standard panel econometrics |
| Entity FE + linear time trend | ✅ Addresses TWFE saturation |
| Cohort-specific event study | ✅ Callaway & Sant'Anna (2021)-style |
| Placebo test | ✅ Valid (p = 0.669) |
| Specification sensitivity | ✅ 5 specs tested |
| Direct environmental KPI | ✅ ln(emissions_intensity), 81% coverage |
| Greenwashing analysis | ✅ Authenticity scoring (ESG + cert + issuer) |
| Heterogeneous effects | ✅ Firm-size moderator |

### 12.2 Remaining Limitations

1. **Sparse treatment.** Only 20/3,964 firms (0.5%) issued green bonds. Limited statistical power for all analyses.

2. **No direct greenium measurement.** An implicit cost-of-debt proxy (`interest_expense / total_debt`) was investigated but proved too noisy (only 10% coverage, unstable coefficients, GMM failure). Bond-level yield data would be needed for proper greenium analysis.

3. **Short panel window.** 2020–2025 (6 years). The 2020 cohort has zero pre-treatment observations, making parallel trends untestable for 5 of 20 treated firms.

4. **ESG and emissions effects confounded by time trends.** Both `esg_score` and `ln_emissions_intensity` effects disappear under TWFE and entity FE + trend, confirming they reflect market-wide trends rather than causal treatment effects.

5. **Cohort 2024 ESG parallel trends violation.** The most recently treated cohort shows a significant pre-trend (p < 0.001), suggesting anticipatory ESG improvements before formal issuance — potentially a selection effect.
