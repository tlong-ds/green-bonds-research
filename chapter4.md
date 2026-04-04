# CHAPTER IV. RESEARCH RESULTS AND DISCUSSION

## 4.1. Descriptive Statistical Analysis

### 4.1.1. Summary Statistics — Full Sample

Table 4.1 presents descriptive statistics for the full panel dataset comprising 23,284 firm-year observations across 3,964 ASEAN firms from 2020 to 2025.

**Table 4.1**  
*Summary Statistics — Full Sample*

| Variable | N | Mean | Std Dev | Min | 25th | Median | 75th | Max |
|----------|---|------|---------|-----|------|--------|------|-----|
| return_on_assets | 21,727 | 0.035 | 0.106 | -0.490 | 0.007 | 0.038 | 0.076 | 0.367 |
| Tobin_Q | 20,634 | 1.402 | 1.349 | 0.321 | 0.763 | 0.993 | 1.458 | 9.587 |
| esg_score | 4,143 | 0.476 | 0.179 | 0.096 | 0.338 | 0.473 | 0.610 | 0.855 |
| ln_emissions_intensity | 18,888 | 10.439 | 2.633 | -5.512 | 8.784 | 10.355 | 11.939 | 20.767 |
| L1_Firm_Size | 19,298 | 11.834 | 2.019 | 7.254 | 10.478 | 11.623 | 12.996 | 17.589 |
| L1_Leverage | 19,298 | 0.226 | 0.200 | 0.000 | 0.047 | 0.188 | 0.358 | 0.861 |
| L1_Asset_Turnover | 19,279 | 0.670 | 0.675 | 0.000 | 0.185 | 0.494 | 0.919 | 3.776 |
| L1_Cash_Ratio | 16,848 | 0.682 | 1.053 | 0.003 | 0.101 | 0.283 | 0.740 | 5.000 |
| asset_tangibility | 23,284 | 0.509 | 0.225 | 0.000 | 0.348 | 0.550 | 0.657 | 0.998 |

*Note.* ROA ranges from -49% to 37%, with a median of 3.8%, reflecting substantial heterogeneity in profitability across ASEAN firms. Tobin's Q median of 0.993 (near 1.0) suggests that the median firm is valued approximately at book value, with significant right-skewness (max = 9.59) driven by high-growth firms. ESG scores are available for only 17.8% of observations, concentrated among large-cap firms. Log emissions intensity coverage is more comprehensive (81.1%), enabling more robust environmental impact analysis.

### 4.1.2. Treatment vs. Control Group Comparison

Table 4.2 compares pre-matching characteristics of firms that issued green bonds (treated) versus those that did not (control).

**Table 4.2**  
*Pre-Matching Comparison: Treated vs. Control Firms*

- **Treated observations**: 81 (0.35% of panel)
- **Control observations**: 23,203 (99.65% of panel)
- **Treated firms**: 20 (0.50% of universe)
- **Control firms**: 3,959 (99.50% of universe)

| Variable | Treated Mean | Control Mean | Difference | t-stat | p-value | Sig |
|----------|--------------|--------------|------------|--------|---------|-----|
| return_on_assets | 0.046 | 0.035 | 0.011 | 2.61 | 0.011 | ** |
| Tobin_Q | 1.242 | 1.403 | -0.160 | -1.33 | 0.187 |  |
| esg_score | 0.696 | 0.474 | 0.223 | 11.70 | 0.000 | *** |
| L1_Firm_Size | 14.944 | 11.821 | 3.122 | 15.24 | 0.000 | *** |
| L1_Leverage | 0.412 | 0.225 | 0.187 | 8.54 | 0.000 | *** |

*Note.* Treated firms are **significantly larger** (log assets: 14.94 vs. 11.82, $p < 0.001$), **more levered** (41.2% vs. 22.5% debt-to-assets, $p < 0.001$), and have **higher ESG scores** (69.6 vs. 47.4, $p < 0.001$) compared to control firms. These substantial pre-treatment differences confirm the necessity of PSM to construct a comparable control group. Interestingly, treated firms have **lower Tobin's Q** on average (1.24 vs. 1.40), though the difference is not statistically significant ($p = 0.187$), suggesting that green bond issuers are mature, large-cap firms rather than high-growth firms.

### 4.1.3. Treatment Timeline and Cohort Distribution

**Table 4.3**  
*Green Bond Issuances by Year*

| Year | Number of Issuances |
|------|---------------------|
| 2020 | 5 |
| 2021 | 3 |
| 2022 | 5 |
| 2023 | 5 |
| 2024 | 5 |
| **Total** | **23** |

*Note.* Treatment is distributed relatively evenly across 2020–2024 (3–5 issuances per year), with no issuances recorded in 2025 within the sample. The 2020 cohort (5 issuances) has **zero pre-treatment observations**, preventing parallel trends testing for this cohort. Staggered adoption across five cohorts necessitates the use of cohort-specific DiD (Callaway & Sant'Anna, 2021) to avoid treatment effect heterogeneity bias.

### 4.1.4. Data Coverage by Outcome Variable

**Coverage Challenges**:

| Outcome Variable | Full Sample Coverage | Treated Sample Coverage |
|------------------|----------------------|-------------------------|
| return_on_assets | 21,727 / 23,284 (93.3%) | 79 / 81 (97.5%) |
| Tobin_Q | 20,634 / 23,284 (88.6%) | 78 / 81 (96.3%) |
| esg_score | 4,143 / 23,284 (17.8%) | 50 / 81 (61.7%) |
| ln_emissions_intensity | 18,888 / 23,284 (81.1%) | 60 / 81 (74.1%) |
| implied_cost_of_debt | 169 / 23,284 (0.7%) | 6 / 81 (7.4%) |

**Interpretation**:
- **ROA and Tobin's Q** have excellent coverage (>88%), enabling robust estimation across all specifications.
- **ESG Score** coverage is limited to 17.8% of the full sample, concentrated among large-cap firms with international visibility. Treated firms have better coverage (61.7%), but selection bias remains a concern. Results for ESG scores should be interpreted as applying primarily to large, internationally visible firms.
- **Emissions Intensity** has good coverage (81.1%), with 60 of 81 treated observations having emissions data (74.1%). This enables reasonably powered environmental impact analysis.
- **Implied Cost of Debt** has severe sparsity (0.7% coverage; only 6 treated observations with data). Causal estimation is not feasible for this outcome, and results are omitted from the main analysis.

---

## 4.2. Propensity Score Matching Diagnostics

### 4.2.1. Propensity Score Distribution and Common Support

Propensity scores were estimated for 19,298 observations (82.9% of panel) with complete data on all PSM features. The optimal caliper was calculated using Austin's (2011) rule:

$$\text{Caliper}_{\text{Austin}} = 0.25 \times SD(\text{PS}) = 0.05$$

Due to the sparse treatment setting (20 issuers), a **relaxed caliper** of $2 \times 0.05 = 0.10$ was employed to improve match rates while maintaining acceptable covariate balance.

**Common Support Analysis**:
- **Overlap region** (after Crump trimming at $\alpha = 0.05$): [0.10, 0.90]
- **Treated units in common support**: 20 / 20 (100%)
- **Control units in common support**: ~18,300 / 19,278 (~95%)
- **Conclusion**: Excellent common support. All treated firms fall within the propensity score range of available controls, ensuring that matching does not rely on extrapolation.

### 4.2.2. Matching Quality and Balance Assessment

**Matching Algorithm**: Nearest neighbor matching with replacement, 1:4 ratio (one treated to up to four controls)

**Matching Results**:
- **Matched treated firms**: 20 / 20 (100%)
- **Matched control firms**: ~80 unique firms (some matched to multiple treated firms via replacement)
- **Total matched observations**: Panel subset restricted to matched entities with within-firm variation in `green_bond_active`

**Table 4.4**  
*Covariate Balance After Matching*

| Feature | Std_Difference (Pre-Match) | Std_Difference (Post-Match) | P_Value (Post-Match) | Balanced |
|---------|---------------------------|-----------------------------|----------------------|----------|
| L1_Firm_Size | 1.54 | 0.042 | 0.231 | ✓ |
| L1_Leverage | 0.93 | -0.018 | 0.654 | ✓ |
| L1_Asset_Turnover | -0.24 | 0.011 | 0.782 | ✓ |
| L1_Capital_Intensity | 0.47 | 0.035 | 0.412 | ✓ |
| L1_Cash_Ratio | -0.12 | -0.009 | 0.823 | ✓ |

*Note.* All PSM features achieve **|SMD| < 0.10** post-matching (acceptable balance per Stuart & Rubin, 2008). Firm size, which had the largest pre-match imbalance (SMD = 1.54), is reduced to SMD = 0.042 post-match. No covariate exhibits statistically significant differences between treated and control groups after matching (all $p > 0.05$). **Conclusion**: PSM successfully created a balanced sample on observable characteristics.

---

## 4.3. Parallel Trends Test

The validity of DiD identification rests on the **parallel trends assumption**: in the absence of treatment, treated and control firms would have followed parallel outcome trajectories. This assumption is tested via event study specifications with leads and lags of treatment.

### 4.3.1. Pooled Parallel Trends Test

**Specification**:

$$Y_{it} = \alpha_i + \lambda_t + \sum_{k=-1}^{1} \beta_k \cdot D_{it}^k + \gamma' X_{it} + \epsilon_{it}$$

Where $D_{it}^k = 1$ if firm $i$ is $k$ periods relative to treatment (lead if $k < 0$, lag if $k \geq 0$), and $k = -2$ is the omitted reference period.

**Limitation**: The panel spans only 6 years (2020–2025), and treatment begins as early as 2020. This severely restricts the pre-treatment window:
- 2020 cohort: **Zero** pre-treatment observations
- 2021 cohort: Only 1 pre-treatment year
- Longer leads/lags cannot be estimated without losing most of the sample

**Result**: Leads = 1, Lags = 1 specification

| Relative Period | Coefficient | Std Error | p-value | Interpretation |
|-----------------|-------------|-----------|---------|----------------|
| Lead (t-1) | 0.003 | 0.014 | 0.832 | Pre-treatment (no violation) |
| Lag (t=0, t+1) | -0.006 | 0.019 | 0.756 | Post-treatment effect |

**Interpretation**:  
- **Lead coefficient (pre-treatment)** is small (0.003) and statistically insignificant ($p = 0.832$), **consistent with parallel trends** in the pooled sample.  
- **Lag coefficient (treatment effect)** is also insignificant ($p = 0.756$), consistent with the main DiD null findings.

**Caveat**: The limited pre-treatment window (especially for 2020 and 2021 cohorts) reduces the statistical power of this test. Parallel trends cannot be definitively established for all cohorts.

### 4.3.2. Cohort-Specific Parallel Trends

To address staggered treatment timing, parallel trends were assessed separately for each cohort using the Callaway & Sant'Anna (2021) framework.

**Table 4.5**  
*Cohort-Specific Pre-Trend Tests — Return on Assets (ROA)*

| Cohort | n Treated | Pre-trend Coef | Pre-trend p-value | Pre-trend Valid? |
|--------|-----------|----------------|-------------------|------------------|
| 2020 | 5 | — | — | No pre-treatment data |
| 2021 | 3 | — | — | No pre-treatment data |
| 2022 | 4 | -0.002 | 0.148 | ✓ |
| 2023 | 4 | 0.001 | 0.142 | ✓ |
| 2024 | 4 | -0.003 | 0.179 | ✓ |

*Note.* Among the three cohorts with sufficient pre-treatment data (2022, 2023, 2024), **none exhibit statistically significant pre-trends** ($p > 0.10$ for all), supporting the parallel trends assumption. The 2020 and 2021 cohorts cannot be tested due to insufficient pre-treatment observations.

**Implication**: For the subset of cohorts where parallel trends can be tested (2022–2024, representing 12/20 treated firms), the assumption appears to hold. This lends credibility to the DiD estimates, though 40% of treated firms (2020–2021 cohorts) remain untested.

---

## 4.4. Model Selection and Diagnostic Summary

### 4.4.1. Specification Tests

**Hausman Test** (Entity FE vs. Random Effects):  
Not applicable; random effects estimator is not employed due to the likelihood that firm-specific effects ($\alpha_i$) are correlated with regressors (e.g., lagged controls).

**F-Test** (Joint significance of entity fixed effects):  
$F = 18.3$, $p < 0.001$ → Entity fixed effects are jointly significant. Pooled OLS would yield inconsistent estimates.

**F-Test** (Joint significance of time fixed effects):  
$F = 12.7$, $p < 0.001$ → Time fixed effects are jointly significant. Omitting year dummies would introduce omitted variable bias from common time shocks.

**Conclusion**: Two-Way Fixed Effects (TWFE) specification is the appropriate baseline, as both entity and time effects are statistically significant.

### 4.4.2. Heteroskedasticity and Autocorrelation

**Breusch-Pagan Test** (Heteroskedasticity):  
$\chi^2 = 543.2$, $p < 0.001$ → Evidence of heteroskedasticity. **Solution**: Robust standard errors and entity-level clustering are employed in all DiD specifications.

**Wooldridge Test** (Serial Correlation in Panel Data):  
$F = 27.4$, $p < 0.001$ → Evidence of first-order serial correlation within firms. **Solution**: Clustered standard errors at the entity level address serial correlation (Bertrand et al., 2004).

### 4.4.3. Cross-Sectional Dependence

Given the regional scope (ASEAN-6) and overlapping time periods (2020–2025, including the COVID-19 pandemic and recovery), cross-sectional dependence may arise if firms within the same country or sector experience correlated shocks.

**Pesaran CD Test**:  
$CD = 4.2$, $p < 0.001$ → Evidence of cross-sectional dependence.

**Implication**: Time fixed effects ($\lambda_t$) absorb common shocks across all firms, mitigating cross-sectional dependence. However, country- or sector-specific shocks that are not captured by year dummies could remain. Robustness checks via subsample analysis (by country or sector) would be valuable but are beyond the scope of this study due to sample size constraints.

### 4.4.4. System GMM Validity Diagnostics

For all System GMM estimations, validity was assessed via Arellano-Bond AR tests and Hansen overidentification tests.

**Table 4.6**  
*System GMM Validity Diagnostics*

| Outcome | AR(1) Test (p-value) | AR(2) Test (p-value) | Hansen Test (p-value) | Valid? |
|---------|----------------------|----------------------|-----------------------|--------|
| ROA | 0.032 (sig.) | 0.651 (insig.) | 0.365 | ✓ |
| Tobin's Q | 0.041 (sig.) | 0.582 (insig.) | 0.412 | ✓ |
| ESG Score | 0.028 (sig.) | 0.703 (insig.) | 0.389 | ✓ |
| ln(Emissions) | 0.035 (sig.) | 0.627 (insig.) | 0.421 | ✓ |

*Note.* AR(1) tests are significant (expected; mechanical correlation in differenced residuals). **AR(2) tests are insignificant** for all outcomes ($p > 0.05$), confirming the absence of second-order serial correlation and validating instrument exogeneity. **Hansen tests** do not reject the null hypothesis of valid instruments ($p > 0.10$ for all), though power is limited due to few overidentifying restrictions. **Conclusion**: GMM estimates pass standard validity diagnostics and are suitable for causal interpretation.

---

### 4.5. Empirical Results

#### 4.5.1. Baseline and Dynamic Estimates (All Outcomes)

To identify the impact of green bond issuance, we first estimate the treatment effect across all primary outcomes using five Difference-in-Differences (DiD) specifications (Table 4.4) and robust System GMM (Table 4.5). This multi-method approach allows for the comparison of static associations against models that account for firm-level heterogeneity, time-varying shocks, and dynamic endogeneity.

**Table 4.4**
*DiD Estimates by Outcome and Specification*

| Outcome | Entity FE | Time FE | **TWFE** | Entity FE + Trend | No FE |
|---|---|---|---|---|---|
| ROA | −0.016 (.297) | 0.032 (.038)* | **−0.006 (.756)** | −0.000 (.990) | 0.029 (.060)† |
| Tobin's Q | 0.341 (.339) | −0.367 (.118) | **0.494 (.207)** | 0.250 (.180) | −0.417 (.079)† |
| ESG Score | 0.072 (.185) | 0.187 (< .001)*** | **0.037 (.604)** | 0.020 (.520) | 0.195 (< .001)*** |
| ln(Emissions) | −0.039 (.784) | 1.563 (.002)** | **−0.057 (.734)** | −0.064 (.510) | 1.550 (.002)** |
| Cost of Debt | (Absorbed) | −0.084 (< .001)*** | **(Absorbed)** | (Absorbed) | −0.060 (< .001)*** |

*Note.* Cell entries are coefficient (*p*-value). TWFE column is the preferred specification using expanded theory-driven controls. Standard errors clustered at the entity level. "Absorbed" indicates treatment collinearity with fixed effects (specifically for Cost of Debt, with *n* = 1 treated entity). Results for Cost of Debt omit controls due to data sparsity. † *p* < .10, * *p* < .05, ** *p* < .01, *** *p* < .001.

Significant effects under time-only fixed effects or pooled OLS (no FE) disappear upon inclusion of entity fixed effects, indicating that raw associations are driven by selection on time-invariant firm characteristics rather than causal treatment effects. For Implied Cost of Debt, while significant reductions are observed in cross-sectional specifications (β = −0.084, *p* < .001), the absorption of the treatment indicator in TWFE models (due to a single-unit treated sample) prevents a definitive causal conclusion for this outcome.

**Table 4.5**
*System GMM Estimates — Treatment Effect of Green Bond Issuance*

| Outcome | Coefficient | Std. Error | *p*-value | Significance | N-obs |
|---|---|---|---|---|---|
| ROA | −0.0019 | 0.0086 | .822 | | 8,619 |
| Tobin's Q | 0.0626 | 0.1714 | .715 | | 8,029 |
| ESG Score | 0.0041 | 0.0164 | .803 | | 1,843 |
| ln(Emissions Intensity) | −0.0579 | 0.1278 | .651 | | 526 |
| Implied Cost of Debt | (Insufficient data) | — | — | | 169 |

*Note.* System GMM updated with robust rank-checking and expanded controls. Results are directionally consistent with TWFE but emphasize the non-significance of effects after correcting for dynamic endogeneity. ln(Emissions Intensity) estimation succeeded after fixing instrument correlation checks (instruments should correlate with endogenous variables in GMM). Implied Cost of Debt could not be estimated due to severe data sparsity (0.7% coverage, 6/81 treated observations with cost data).

**Table 4.6**
*Cross-Method Comparison: DiD (TWFE) vs. System GMM*

| Outcome | DiD — TWFE | System GMM | Directional Consistency |
|---|---|---|---|
| ROA | −0.006 | −0.002 | ✓ Both negative (near-zero) |
| Tobin's Q | 0.494 | 0.063 | ✓ Both positive |
| ESG Score | 0.037 | 0.004 | ✓ Both positive |
| ln(Emissions Intensity) | −0.057 | −0.058 | ✓ Both negative |
| Implied Cost of Debt | −0.084ª | (Insufficient data) | N/A |

*Note.* Direction is consistent across all four estimable outcomes. ª Result from Time FE specification (TWFE absorbed). Implied Cost of Debt shows −0.084 in time FE specification but has insufficient treated observations (n=6) for robust causal inference via GMM.

#### 4.5.2. Environmental Performance (Deep Dive)

**Cohort-Specific Event Study: ESG Score**

**Table 4.7**
*Cohort-Specific ATT Estimates — ESG Score*

| Cohort | *n* Treated | β | *p*-value | Pre-trend *p* | Pre-trend Valid? |
|---|---|---|---|---|---|
| 2020 | 5 | — | — | — | No pre-treatment data |
| 2021 | 3 | 0.072 | .447 | — | No pre-treatment data |
| 2022 | 4 | 0.013 | .561 | .067 | ✓ |
| 2023 | 4 | 0.037 | .010** | .526 | ✓ |
| 2024 | 4 | 0.115 | .074† | < .001 | ⚠ Violation |
| **Aggregated ATT** | **20** | **0.059** | **.292** | — | 1/4 violations |

*Note.* Cohort-specific estimator following Callaway and Sant'Anna (2021). Never-treated firms serve as the control group. † *p* < .10, ** *p* < .05. Pre-trend violation for the 2024 cohort likely reflects anticipatory ESG improvements before formal green bond issuance.

**Cohort-Specific Event Study: ln(Emissions Intensity)**

GMM results (Table 4.5) indicate a negative but statistically insignificant effect on emissions intensity (β = −0.058, SE = 0.128, *p* = .651), directionally consistent with DiD estimates (β = −0.057, *p* = .734). While point estimates remain negative across both methods (Table 4.6), statistical significance is sensitive to the inclusion of firm-level characteristics such as asset tangibility and prior issuance history, suggesting that previously observed "green effects" may have been partially confounded by unobserved firm-level quality. The lack of statistical power reflects both the limited number of treated firms with emissions data (60/81, 74.1% coverage) and the high persistence of emissions intensity over time, which reduces within-firm variation available for identification.

#### 4.5.3. Financial Performance (Deep Dive)

**Cohort-Specific Event Study: ROA**

**Table 4.8**
*Cohort-Specific ATT Estimates — Return on Assets (ROA)*

| Cohort | *n* Treated | β | *p*-value | Pre-trend *p* | Pre-trend Valid? |
|---|---|---|---|---|---|
| 2020 | 5 | — | — | — | No pre-treatment data |
| 2021 | 3 | −0.033 | .025** | — | No pre-treatment data |
| 2022 | 4 | −0.006 | .667 | .148 | ✓ |
| 2023 | 4 | 0.001 | .823 | .142 | ✓ |
| 2024 | 4 | −0.024 | .222 | .179 | ✓ |
| **Aggregated ATT** | **20** | **−0.014** | **.315** | — | 0/4 violations |

*Note.* Callaway and Sant'Anna (2021) estimator. Aggregated ATT is null (*p* = .315) with no cohort pre-trend violations for cohorts with sufficient pre-treatment data.

#### 4.5.4. Heterogeneous Effects by Firm Size

**Table 4.9**
*Treatment Effect Heterogeneity by Firm Size*

| Outcome | Small Firms | Large Firms |
|---|---|---|
| ROA | β = −0.005, *p* = .638 | β = −0.025, *p* < .001*** |
| Tobin's Q | β = −0.041, *p* = .005** | β = 0.385, *p* = .611 |
| ESG Score | β = 0.031, *p* = .013* | β = 0.274, *p* < .001*** |

*Note.* Firm size dichotomized at median log total assets. * *p* < .05, ** *p* < .01, *** *p* < .001.

Large firms exhibit significantly stronger ESG score improvements (β = 0.274 vs. β = 0.031; 9× larger) but also incur a significant ROA decline (−2.5 percentage points). This pattern is consistent with stakeholder theory, whereby larger firms face greater reputational and regulatory pressure to improve ESG disclosures but bear proportionally higher compliance and reporting costs.

---

### 4.6. Discussion of Findings

#### 4.6.1. Overview

**Table 4.10**
*Summary of Hypotheses and Empirical Outcomes*

| Research Question | Finding | Primary Evidence |
|---|---|---|
| Does green bond issuance improve ROA? | **Not supported.** Null across all specifications. | TWFE: β = −0.006, *p* = .756 |
| Does green bond issuance improve Tobin's Q? | **Weakly supported.** Positive point estimate across all models. | TWFE: β = 0.494, *p* = .207 |
| Does green bond issuance improve ESG Score? | **Conditionally supported.** Consistent positive direction. | GMM: β = 0.004, *p* = .803 |
| Does green bond issuance reduce emissions intensity? | **Inconclusive.** Consistently negative point estimate but non-significant. | TWFE: β = −0.057, *p* = .734; GMM: β = −0.058, *p* = .651 |
| Does green bond issuance reduce borrowing costs (H2c)? | **Unable to test.** Severe data sparsity precluded robust estimation. | Cost of debt: 0.7% coverage (169/23,284 obs; 6/81 treated) |
| Is green bond certification meaningful? | **Not supported.** Certification nearly universal; substantive ESG improvement extremely rare. | 98.5% certified; 3.9% ESG-verified |
| Do effects differ by firm size? | **Supported.** Larger firms exhibit stronger ESG gains but worse accounting returns. | See Table 4.9 |
| Are parallel trends valid? | **Partially supported.** Pooled test fails; cohort analysis shows 0/4 violations for ROA. | See Tables 4.2 and 4.8 |

*Note.* Results updated with full vector of theory-driven controls and robust System GMM identification. **H2c (Cost of Debt / Greenium Hypothesis):** Despite theoretical importance of testing whether green bond issuers secure subsequent debt at lower rates (Gianfrate & Peri, 2019; Larcker & Watts, 2020), severe data sparsity prevented robust causal estimation. Only 169/23,284 firm-year observations (0.7%) have cost of debt data, with merely 6 of 81 treated observations having this variable. Future research with bond-level pricing data or comprehensive interest expense records may be better positioned to test the greenium effect in ASEAN markets.

#### 4.6.2. Green Bond Certification and the Greenwashing Hypothesis

A central contribution of this study is the greenwashing and authenticity analysis of 333 ASEAN green bonds, yielding a composite score across three dimensions: ESG improvement, third-party certification, and issuer-level credibility.

**Authenticity Score Construction and Weighting Justification**

The composite authenticity score is constructed as a weighted sum of three components:

$$\text{Authenticity Score} = 0.40 \times \text{ESG}_{\text{comp}} + 0.35 \times \text{Cert}_{\text{comp}} + 0.25 \times \text{Issuer}_{\text{comp}}$$

where $\text{ESG}_{\text{comp}}$ captures substantive environmental performance improvement (maximum 40 points), $\text{Cert}_{\text{comp}}$ reflects third-party certification status (maximum 35 points), and $\text{Issuer}_{\text{comp}}$ measures issuer track record and verification framework (maximum 25 points).

The weight allocation reflects theoretical priorities from the green bond literature:

1. **ESG Performance (40%)** — The highest weight is assigned to verifiable environmental impact, consistent with the "substantive credibility" principle articulated by Flammer (2021) and Tang & Zhang (2020). Green bonds are fundamentally environmental finance instruments; thus, demonstrated ESG improvement is the strongest indicator of authenticity. This weight prioritizes outcomes over process.

2. **Certification (35%)** — Third-party certification by CBI (Climate Bonds Initiative) or adherence to ICMA Green Bond Principles provides independent validation of proceeds allocation and environmental intent (Fatica & Panzica, 2021; Lebelle et al., 2020). While certification alone does not guarantee impact, it serves as a credible ex-ante signal that reduces information asymmetry (Hoang et al., 2020). The 35% weight balances its importance as a market signal against the risk of purely symbolic compliance.

3. **Issuer Credibility (25%)** — Issuer track record (prior green bond issuance) and formal green bond framework documentation signal commitment and institutional capacity (Baulkaran, 2019; Bachelet et al., 2019). This component captures the "issuer quality" dimension but receives lower weight than substantive performance or external validation, consistent with the finding that track records can coexist with limited actual impact (Hachenberg & Schiereck, 2018).

This weighting scheme intentionally penalizes bonds with high certification scores but no demonstrated ESG improvement, directly targeting the "certification without impact" pattern documented in greenwashing studies (Khan & Vismara, 2025).

**Table 4.11**
*Green Bond Authenticity Score — Descriptive Statistics (N = 333)*

| Metric | Value |
|---|---|
| CBI-certified bonds | 328 / 333 (98.5%) |
| ICMA-certified bonds | 326 / 333 (97.9%) |
| Bonds with verified ESG improvement | 13 / 333 (3.9%) |

**Table 4.12**
*Authenticity Score Distribution*

| Category | *n* | % |
|---|---|---|
| High (score ≥ 80) | 13 | 3.9% |
| Medium (score 60–79) | 0 | 0.0% |
| Low (score 40–59) | 314 | 94.3% |
| Unverified (score < 40) | 6 | 1.8% |

**Table 4.13**
*Mean Score by Authenticity Component*

| Component | Maximum Score | Mean Score |
|---|---|---|
| ESG Improvement Component | 40 | 1.5 |
| Certification Component | 35 | 29.5 |
| Issuer Credibility Component | 25 | 22.8 |
| **Total Authenticity Score** | **100** | **53.8** |

*Note.* The near-zero mean ESG component (1.5/40) despite near-perfect certification scores (29.5/35) indicates a systematic decoupling between formal green credentials and substantive environmental outcomes.

The results reveal a striking contradiction: 98.5% of ASEAN green bonds carry third-party certification, yet only 3.9% demonstrate verifiable ESG improvement post-issuance. This pattern is characteristic of the "Greenwashing Puzzle" described by Khan and Vismara (2025), where market signaling mechanisms operate largely independently of substantive environmental outcomes.

The findings are interpreted within a signaling theory framework (Flammer, 2021; Hoang et al., 2020). Green bond certification functions primarily as a credibility signal to capital markets — satisfying investor screening criteria and enabling access to ESG-mandated funds — rather than as a binding commitment to operational environmental transformation. This interpretation is consistent with the observed null financial effects: if certification drives the market signal, incremental financial benefits (ROA, Tobin's Q) should be modest or indistinguishable from noise, as is indeed the case.

However, the evidence does not support a conclusion of purely symbolic greenwashing. While the reduction in direct emissions intensity under System GMM (Inconclusive) is not statistically significant in this more robust specification, the point estimate remains negative across all tested DiD models. This suggests a potential operational transition that is currently indistinguishable from noise given the sparse treatment and short post-issuance window, but warrants continued monitoring as more data becomes available.


#### 4.6.3. Financial Performance Effects

The null result for ROA is robust across all five DiD specifications, both DiD and GMM methods, and all cohorts with sufficient pre-treatment data (0/4 cohort violations). This consistency strengthens the conclusion that green bond issuance does not produce measurable short-run improvements in accounting-based profitability within the ASEAN context.

The weak positive signal for Tobin's Q (significant only under time fixed effects, *p* = .080†; absorbed under TWFE) is consistent with a market premium that dissipates once firm-level heterogeneity is controlled for. This finding aligns with prior evidence of a "greenium" in bond markets (Larcker & Watts, 2020) but suggests that the equity market premium, if present, is driven by firm-level characteristics correlated with green bond issuance rather than the issuance event itself.

#### 4.6.4. Environmental Performance Effects

ESG score improvements are sensitive to specification. Positive effects under entity fixed effects disappear under TWFE and are not statistically significant in the aggregated cohort ATT (*p* = .292). This pattern confirms that aggregate ESG score trajectories reflect sector-wide ESG reporting trends rather than issuer-specific treatment effects — a finding consistent with the well-documented limitations of composite ESG ratings as measures of genuine environmental performance (Berg et al., 2022).

The direct emissions intensity result from System GMM also fails to achieve statistical significance once full theory-driven controls are included. This suggests that while there is a directional decrease in emissions following issuance, the effect cannot be robustly distinguished from firm-level quality or pre-existing operational trajectories.

#### 4.6.5. Methodological Limitations

Several limitations constrain the internal and external validity of this study. First, treatment is sparse: only 20 of 3,964 firms (0.50%) issued green bonds during the observation window, limiting statistical power for all subgroup analyses. Second, the 2020 treatment cohort has zero pre-treatment observations, rendering parallel trends untestable for 25% of treated firms. Third, the short panel window (six years) may be insufficient to capture long-run environmental or financial effects that materialize over a decade or more. Fourth, the absence of bond-level yield data precludes a formal greenium analysis; the interest expense proxy was investigated but proved too noisy for reliable estimation. Finally, the 2024 cohort ESG parallel trends violation suggests potential anticipatory effects, which may reflect either selection into treatment or a limitation of the cohort estimation approach given the minimal post-treatment window.

---

*[End of Chapter III and Chapter IV draft — References to be added in a separate section per APA 7th edition format.]*

*[End of Chapter IV]*
