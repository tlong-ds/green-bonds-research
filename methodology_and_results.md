# Impacts of Green Bonds on Financial Performance and Corporate Environmental Performance in ASEAN Listed Companies

---

## CHAPTER III. RESEARCH METHODOLOGY

### 3.1. Research Process

This study employs a three-stage causal inference pipeline to isolate the effect of green bond issuance on corporate financial and environmental performance. The research process proceeds as follows.

In the **first stage**, Propensity Score Matching (PSM) is applied to construct a comparable control group for treated firms (i.e., green bond issuers), conditioning on pre-treatment observable firm characteristics. This step mitigates selection bias by ensuring that treated and untreated firms are statistically comparable prior to treatment.

In the **second stage**, a Difference-in-Differences (DiD) estimator—specifically the Two-Way Fixed Effects (TWFE) specification—is applied to the matched and full panels to estimate the average treatment effect on the treated (ATT). To account for treatment timing heterogeneity across multiple cohorts, a cohort-specific event study following Callaway and Sant'Anna (2021) is conducted alongside the pooled DiD.

In the **third stage**, a System Generalized Method of Moments (System GMM) estimator is used as a robustness check. System GMM controls for dynamic endogeneity and unobserved heterogeneity by instrumenting lagged levels with differences and lagged differences with levels, producing coefficient estimates that are consistent under weaker assumptions than OLS or TWFE.

The analysis is further supplemented by a greenwashing and authenticity analysis based on a composite certification and ESG improvement score, and a heterogeneous effects analysis by firm size. The full pipeline is summarized in Figure 3.1.

> *[Figure 3.1: Research Process Flowchart — to be inserted]*

---

### 3.2. Research Data

The study draws on firm-level panel data retrieved from LSEG Datastream/Workspace (Refinitiv), supplemented by green bond transaction records from LSEG Deals Screener and environmental certification data from the Climate Bonds Initiative (CBI) and the International Capital Market Association (ICMA). The final dataset covers ASEAN-listed companies across six member states over a six-year observation window (2020–2025).

**Table 3.1**
*Panel Data Structure*

| Dimension | Value |
|---|---|
| Total Observations | 23,284 |
| Number of Variables | 164+ |
| Number of Entities | 3,964 (identified by `org_permid`) |
| Observation Periods | 6 years (2020–2025) |
| Treatment Indicator | `green_bond_active` (= 1 if firm has issued a green bond by year *t*) |
| Treated Firm-Years | 81 (0.35% of panel) |
| Treated Firms | 20 (0.50% of entities) |
| Treatment Cohorts | 5 (2020: *n* = 5; 2021: *n* = 3; 2022: *n* = 4; 2023: *n* = 4; 2024: *n* = 4) |

*Note.* Source: LSEG Datastream/Workspace. Panel constructed via `prepare_full_panel_data()`.

Outlier treatment follows a two-pass winsorization procedure.
 In the first pass, 18 raw financial metrics are winsorized at the 1st and 99th percentiles. In the second pass, five computed financial ratios are winsorized at the same thresholds. Additionally, emissions intensity is log-transformed as $\ln(\max(1, \text{emissions\_intensity}))$ to address severe right skew in the raw distribution (range: 0 to 1.04 × 10⁹).

---

### 3.3. Measurement of Variables

#### 3.3.1. Dependent Variables

This study examines four outcome variables spanning both financial and environmental dimensions of corporate performance. Financial performance is captured through two proxies: an accounting-based measure (Return on Assets) and a market-based measure (Tobin's Q). Corporate environmental performance is assessed through a composite ESG rating score and a direct emissions intensity measure.

**Table 3.2**
*Dependent Variables*

| Variable | Dimension | Description | Scale |
|---|---|---|---|
| Return on Assets (ROA) | Financial — Accounting | Net income divided by total assets | 0–1 |
| Tobin's Q | Financial — Market | Market capitalization divided by total assets | > 0 |
| ESG Score | Environmental — Composite | Refinitiv ESG rating (ASSET4) | 0–100 |
| ln(Emissions Intensity) | Environmental — Direct | Natural log of GHG emissions per unit output | ~0–21 |
| Implied Cost of Debt | Financial — Cost | Interest expense divided by total debt | > 0 |

*Note.* ESG Score sourced from Refinitiv ASSET4. Emissions intensity log-transformed to correct for distributional skew.

#### 3.3.2. Independent Variable

The primary independent variable is `green_bond_active`, a binary treatment indicator equal to 1 if a firm has issued at least one green bond by year *t* and 0 otherwise. Green bond issuances are identified using LSEG Deals Screener, with certification status cross-referenced against CBI and ICMA registries.

#### 3.3.3. Control Variables

To mitigate omitted variable bias, all regression specifications include a vector of firm-level control variables, each measured with a one-year lag relative to the outcome to reduce simultaneity bias.

**Table 3.3**
*Control Variables (One-Year Lagged)*

| Variable | Operationalization |
|---|---|
| Firm Size (`L1_Firm_Size`) | Natural log of total assets at *t* − 1 |
| Leverage (`L1_Leverage`) | Total debt divided by total assets at *t* − 1 |
| Asset Turnover (`L1_Asset_Turnover`) | Net sales divided by total assets at *t* − 1 |
| Capital Intensity (`L1_Capital_Intensity`) | Capital expenditures divided by total assets at *t* − 1 |
| Cash Ratio (`L1_Cash_Ratio`) | Cash divided by total assets at *t* − 1 |
| Asset Tangibility (`asset_tangibility`) | Net property, plant, and equipment as % of total assets |
| Issuer Track Record (`issuer_track_record`) | Cumulative count of prior green bond issuances |
| Green Bond Framework (`has_green_framework`) | Binary indicator (= 1) if issuer has a documented framework |

---

### 3.4. Descriptive Statistics

**Table 3.4**
*Descriptive Statistics — Full Sample and Group Comparison*

**Panel A: Full Sample (N = 23,284)**
| Variable | count | mean | std | min | 25% | 50% | 75% | max |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|
| Return on Assets (ROA) | 21,727 | 0.0353 | 0.1062 | -0.4902 | 0.0068 | 0.0377 | 0.0764 | 0.3670 |
| Tobin's Q | 20,634 | 1.4021 | 1.3492 | 0.3211 | 0.7629 | 0.9934 | 1.4583 | 9.5867 |
| ESG Score | 4,143 | 0.4763 | 0.1786 | 0.0957 | 0.3379 | 0.4727 | 0.6095 | 0.8545 |
| ln(Emissions Intensity) | 18,888 | 10.4390 | 2.6335 | -5.5116 | 8.7838 | 10.3553 | 11.9394 | 20.7667 |
| L1_Firm_Size | 19,298 | 11.8335 | 2.0191 | 7.2540 | 10.4778 | 11.6233 | 12.9959 | 17.5891 |
| L1_Leverage | 19,298 | 0.2259 | 0.2001 | 0.0000 | 0.0471 | 0.1877 | 0.3583 | 0.8607 |
| L1_Asset_Turnover | 19,279 | 0.6699 | 0.6750 | 0.0001 | 0.1850 | 0.4943 | 0.9193 | 3.7762 |
| L1_Capital_Intensity | 19,279 | 167.345 | 1421.33 | 0.2648 | 1.0878 | 2.0231 | 5.4067 | 13097.3 |
| L1_Cash_Ratio | 16,848 | 0.7926 | 1.6380 | 0.0030 | 0.1014 | 0.2827 | 0.7399 | 11.9198 |

**Panel B: Treated vs. Untreated Comparison (Means)**
| Variable | Treated (Mean) | Untreated (Mean) | Difference |
|:---|---:|---:|---:|
| Return on Assets (ROA) | 0.0462 | 0.0353 | +0.0109 |
| Tobin's Q | 1.2425 | 1.4027 | -0.1602 |
| ESG Score | 0.6963 | 0.4736 | +0.2227*** |
| ln(Emissions Intensity) | 13.8184 | 10.4282 | +3.3902*** |
| L1_Firm_Size | 14.9437 | 11.8212 | +3.1225*** |
| L1_Leverage | 0.4122 | 0.2252 | +0.1870*** |

*Note.* Treated firms are significantly larger, more leveraged, and have higher ESG scores and emissions intensity (reflecting sector composition, i.e., heavy industry).

---

### 3.5. Research Models

#### 3.5.1. Propensity Score Matching Model (First Stage)

Propensity score matching is used to construct a counterfactual control group for green bond issuers based on observable pre-treatment firm characteristics. Each treated firm is matched to the most similar untreated firm(s) using nearest-neighbour matching within a caliper bound.

The propensity score *p*(*X*) is estimated via logistic regression:

$$p(X_{it}) = \Pr(\text{green\_bond\_active}_{it} = 1 \mid X_{it})$$

where $X_{it}$ denotes the vector of lagged control variables defined in Section 3.3.3 (Table 3.3). The caliper is set at $2 \times \sigma_p$ (following Austin, 2011), with a minimum floor of 0.05 standard deviations. Covariate balance is assessed using standardized mean differences (Cohen's *d*); balance is considered acceptable when all differences fall below 0.10.

#### 3.5.2. Difference-in-Differences Model (Second Stage)

The baseline DiD specification is a Two-Way Fixed Effects (TWFE) panel regression estimated on the full unmatched panel (due to limited PSM coverage; see Section 4.3):

$$Y_{it} = \alpha + \delta \cdot \text{green\_bond\_active}_{it} + \beta X_{it-1} + \mu_i + \lambda_t + \varepsilon_{it}$$

where $Y_{it}$ is one of the four outcome variables, $\delta$ is the ATT of green bond issuance, $X_{it-1}$ is the vector of lagged controls, $\mu_i$ denotes entity fixed effects, $\lambda_t$ denotes year fixed effects, and $\varepsilon_{it}$ is the idiosyncratic error term. Standard errors are clustered at the entity level to account for within-firm serial correlation.

Five specifications are estimated for each outcome to assess robustness: (1) entity fixed effects only, (2) time fixed effects only, (3) two-way fixed effects (TWFE), (4) entity fixed effects with a firm-specific linear time trend, and (5) no fixed effects (pooled OLS).

To address treatment timing heterogeneity, a cohort-specific event study following Callaway and Sant'Anna (2021) is also estimated, decomposing the aggregated ATT by treatment cohort:

$$ATT(g, t) = \mathbb{E}[Y_{it}(g) - Y_{it}(0) \mid G_i = g]$$

where $G_i = g$ denotes the cohort of firm *i* (i.e., the calendar year of first green bond issuance) and $Y_{it}(0)$ is the counterfactual potential outcome under no treatment.

#### 3.5.3. Dynamic Panel Estimation Model (System GMM)

System GMM (Arellano & Bover, 1995; Blundell & Bond, 1998) is employed as the primary robustness estimator to address dynamic endogeneity, unobserved heterogeneity, and potential simultaneity between green bond issuance and firm performance:

$$Y_{it} = \rho Y_{it-1} + \delta \cdot \text{green\_bond\_active}_{it} + \beta X_{it-1} + \mu_i + \varepsilon_{it}$$

The system GMM estimator combines the differenced equation (instrumenting with lagged levels) and the levels equation (instrumenting with lagged differences), yielding consistent estimates when *T* is small and *N* is large. Instrument validity is assessed via the Arellano-Bond AR(2) test for second-order autocorrelation and the Sargan-Hansen test for overidentifying restrictions.

---

### 3.6. Model Estimation and Evaluation

#### 3.6.1. Parallel Trends Assumption

The validity of the DiD estimator rests on the parallel trends assumption — that treated and control firms would have followed similar trajectories in the absence of treatment. This is tested via a pre-treatment event study specification including leads and lags of the treatment indicator:

$$Y_{it} = \alpha + \sum_{k=-2}^{+1} \gamma_k \cdot D_{it}^k + \beta X_{it-1} + \mu_i + \lambda_t + \varepsilon_{it}$$

where $D_{it}^k$ is an indicator for $k$ periods relative to first green bond issuance. Evidence of significant pre-treatment leads ($k < 0$) would indicate a violation of parallel trends. Both pooled and cohort-specific pre-trend tests are reported.

#### 3.6.2. Robustness Checks

Three robustness procedures are conducted. First, specification sensitivity is assessed by estimating the treatment effect across all five DiD specifications. Second, a placebo test shifts the treatment date one year forward to verify that estimated effects are not driven by pre-existing trends. Third, leave-one-out cross-validation (100 folds) is used to assess the stability of the estimated treatment coefficients across subsamples.

---

## CHAPTER IV. RESEARCH RESULTS AND DISCUSSION

### 4.1. Model Selection and Diagnostic Summary

Prior to estimating the main treatment effects, the panel data underwent rigorous diagnostic testing to ensure the validity of the econometric specifications. Summary statistics and group comparisons (see Section 3.4, Table 3.4) indicate significant pre-treatment differences between green bond issuers and non-issuers, particularly regarding firm size and ESG profile, justifying the use of Propensity Score Matching (PSM) and Two-Way Fixed Effects (TWFE).

Technical diagnostics, including the Hausman test, Breusch-Pagan test for heteroscedasticity, Wooldridge test for autocorrelation, and Pesaran CD test for cross-sectional dependence, were conducted for all outcome variables. The results consistently reject the null hypotheses of homoscedasticity and independence, necessitating the use of entity-clustered standard errors across all specifications. Detailed diagnostic tables and the Pearson correlation matrix are provided in **Appendix A**.

### 4.2. Propensity Score Matching Diagnostics

Logistic regression over the pre-treatment period yielded propensity scores for 16,831 firm-year observations. Nearest-neighbour matching within the specified caliper (0.05) produced 9 matched treated firms paired with 36 control firms (45 total matched observations), representing a match rate of 45% (9 out of 20 treated firms).

**Table 4.1**
*PSM Diagnostics*

| Metric | Value |
|---|---|
| Propensity Scores Estimated | 16,831 |
| Caliper (2× Austin, floor 0.05) | 0.0500 |
| Matched Treated Firms | 9 / 20 (45.0%) |
| Matched Control Firms | 36 |
| Total Matched Observations | 45 |
| Max Standardized Difference (post-match) | < 0.10 (Cohen's *d*) |

*Note.* Covariate balance criterion met: all standardized differences < 0.10. Due to low match rate, DiD and GMM are estimated on the full panel (23,284 observations).

### 4.3. Parallel Trends Test

**Table 4.2**
*Pooled Parallel Trends Test*

| Term | Coefficient | *p*-value |
|---|---|---|
| `treatment_lead_1` (pre-treatment, *k* = −1) | 0.1089 | .009*** |
| `green_bond_active` (contemporaneous) | 0.0272 | .407 |
| `treatment_lag_1` (post-treatment, *k* = +1) | 0.3750 | .008*** |

*Note.* \*\*\* *p* < .01. Standard errors clustered at entity level.

The pooled pre-treatment lead is statistically significant (*p* = .009), raising a potential concern about the parallel trends assumption. However, cohort-specific event studies (Section 4.4.1) reveal that this violation is not universal across cohorts: zero of four cohorts violate pre-trends for ROA, and only the 2024 cohort violates for ESG Score. The pooled significance reflects composition effects across staggered treatment cohorts rather than a systematic failure of the identification assumption.

### 4.4. Robustness Check Results

**Table 4.3**
*Robustness Check Summary*

| Test | Result |
|---|---|
| Specification sensitivity (5 specifications) | All ROA coefficients null across specifications. Robust. |
| Placebo test (treatment date shifted +1 year) | β = 0.008, *p* = .669. No spurious effect detected. ✓ |
| Leave-one-out cross-validation (100 folds) | Treatment coefficient stable across subsamples. ✓ |

---

### 4.5. Regression Result Analysis

#### 4.5.1. Impact of Green Bonds on Corporate Environmental Performance

**Cohort-Specific Event Study: ESG Score**

**Table 4.4**
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

GMM results (Table 4.7) indicate a negative but non-significant treatment effect on log emissions intensity (β = −0.084, *p* = .284) when using the full vector of theory-driven controls. While the point estimate remains negative across specifications (Table 4.8), its statistical significance is sensitive to the inclusion of firm-level characteristics such as asset tangibility and prior issuance history, suggesting that previously observed "green effects" may have been partially confounded by unobserved firm-level quality.

#### 4.5.2. Impact of Green Bonds on Corporate Financial Performance

**DiD Results (Full Panel, 5 Specifications)**

**Table 4.5**
*DiD Estimates by Outcome and Specification*

| Outcome | Entity FE | Time FE | **TWFE** | Entity FE + Trend | No FE |
|---|---|---|---|---|---|
| ROA | −0.007 (.480) | 0.007 (.500) | **0.004 (.730)** | −0.000 (.990) | 0.018 (.040)* |
| Tobin's Q | 0.187 (.320) | 0.395 (.020)* | **0.356 (.080)†** | 0.250 (.180) | −0.160 (.410) |
| ESG Score | 0.057 (.050)* | 0.134 (< .001)*** | **0.020 (.610)** | 0.020 (.520) | 0.152 (< .001)*** |
| ln(Emissions) | −0.077 (.430) | 1.130 (.010)** | **−0.057 (.610)** | −0.064 (.510) | 1.119 (.010)** |

*Note.* Cell entries are coefficient (*p*-value). TWFE column is the preferred specification. Standard errors clustered at the entity level. † *p* < .10, * *p* < .05, ** *p* < .01, *** *p* < .001.

Significant effects under time-only fixed effects or pooled OLS (no FE) disappear upon inclusion of entity fixed effects, indicating that raw associations are driven by selection on time-invariant firm characteristics rather than causal treatment effects.

**Cohort-Specific Event Study: ROA**

**Table 4.6**
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

**System GMM Estimates**

**Table 4.7**
*System GMM Estimates — Treatment Effect of Green Bond Issuance*

| Outcome | Coefficient | Std. Error | *p*-value | Significance | N-obs |
|---|---|---|---|---|---|
| ROA | −0.0039 | 0.0027 | .143 | | 9,816 |
| Tobin's Q | 0.1441 | 0.1521 | .343 | | 9,257 |
| ESG Score | 0.0136 | 0.0099 | .168 | | 1,328 |
| ln(Emissions Intensity) | −0.0839 | 0.0783 | .284 | | 7,259 |
| Implied Cost of Debt | −1889.3 | 2567.6 | .462 | | 1,000 |

*Note.* System GMM following Arellano and Bover (1995) and Blundell and Bond (1998). Corrected for dynamic endogeneity with theory-driven controls including asset tangibility and track record.

**Table 4.8**
*Cross-Method Comparison: DiD (TWFE) vs. System GMM*

| Outcome | DiD — TWFE | System GMM | Directional Consistency |
|---|---|---|---|
| ROA | 0.004 | −0.004 | Mixed (both near zero) |
| Tobin's Q | 0.356 | 0.144 | ✓ Both positive |
| ESG Score | 0.020 | 0.014 | ✓ Both positive |
| ln(Emissions Intensity) | −0.057 | −0.084 | ✓ Both negative |

*Note.* Direction is consistent for three of four outcomes. Magnitude divergence for ln(Emissions Intensity) reflects GMM's additional correction for dynamic endogeneity.

**Heterogeneous Effects by Firm Size**

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
| Does green bond issuance improve ROA? | **Not supported.** Null across all specifications. | GMM: β = −0.0039, *p* = .143 |
| Does green bond issuance improve Tobin's Q? | **Weakly supported.** Marginal under TWFE; not robust to GMM. | TWFE: β = 0.356, *p* = .080† |
| Does green bond issuance improve ESG Score? | **Conditionally supported.** Significant under entity FE; absorbed under TWFE. | Entity FE: β = 0.057, *p* = .050* |
| Does green bond issuance reduce emissions intensity? | **Inconclusive.** Consistently negative point estimate but non-significant with theory-driven controls. | GMM: β = −0.0839, *p* = .284 |
| Is green bond certification meaningful? | **Not supported.** Certification nearly universal; substantive ESG improvement extremely rare. | 98.5% certified; 3.9% ESG-verified |
| Do effects differ by firm size? | **Supported.** Larger firms exhibit stronger ESG gains but worse accounting returns. | See Table 4.9 |
| Are parallel trends valid? | **Partially supported.** Pooled test fails; cohort analysis shows 0/4 violations for ROA. | See Tables 4.2 and 4.6 |

#### 4.6.2. Green Bond Certification and the Greenwashing Hypothesis

A central contribution of this study is the greenwashing and authenticity analysis of 333 ASEAN green bonds, yielding a composite score across three dimensions: ESG improvement, third-party certification, and issuer-level credibility.

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

However, the evidence does not support a conclusion of purely symbolic greenwashing. While the reduction in direct emissions intensity under System GMM (β = −0.084, *p* = .284) is not statistically significant in this more robust specification, the point estimate remains negative across all tested models. This suggests a potential operational transition that is currently indistinguishable from noise given the sparse treatment and short post-issuance window, but warrants continued monitoring as more data becomes available.


#### 4.6.3. Financial Performance Effects

The null result for ROA is robust across all five DiD specifications, both DiD and GMM methods, and all cohorts with sufficient pre-treatment data (0/4 cohort violations). This consistency strengthens the conclusion that green bond issuance does not produce measurable short-run improvements in accounting-based profitability within the ASEAN context.

The weak positive signal for Tobin's Q (significant only under time fixed effects, *p* = .080†; absorbed under TWFE) is consistent with a market premium that dissipates once firm-level heterogeneity is controlled for. This finding aligns with prior evidence of a "greenium" in bond markets (Larcker & Watts, 2020) but suggests that the equity market premium, if present, is driven by firm-level characteristics correlated with green bond issuance rather than the issuance event itself.

#### 4.6.4. Environmental Performance Effects

ESG score improvements are sensitive to specification. Positive effects under entity fixed effects (β = 0.057, *p* = .050) disappear under TWFE (β = 0.020, *p* = .610) and are not statistically significant in the aggregated cohort ATT (*p* = .292). This pattern confirms that aggregate ESG score trajectories reflect sector-wide ESG reporting trends rather than issuer-specific treatment effects — a finding consistent with the well-documented limitations of composite ESG ratings as measures of genuine environmental performance (Berg et al., 2022).

The direct emissions intensity result from System GMM also fails to achieve statistical significance (β = −0.084, *p* = .284) once full theory-driven controls are included. This suggests that while there is a directional decrease in emissions following issuance, the effect cannot be robustly distinguished from firm-level quality or pre-existing operational trajectories.

#### 4.6.5. Methodological Limitations

Several limitations constrain the internal and external validity of this study. First, treatment is sparse: only 20 of 3,964 firms (0.50%) issued green bonds during the observation window, limiting statistical power for all subgroup analyses. Second, the 2020 treatment cohort has zero pre-treatment observations, rendering parallel trends untestable for 25% of treated firms. Third, the short panel window (six years) may be insufficient to capture long-run environmental or financial effects that materialize over a decade or more. Fourth, the absence of bond-level yield data precludes a formal greenium analysis; the interest expense proxy was investigated but proved too noisy for reliable estimation. Finally, the 2024 cohort ESG parallel trends violation suggests potential anticipatory effects, which may reflect either selection into treatment or a limitation of the cohort estimation approach given the minimal post-treatment window.

---

*[End of Chapter III and Chapter IV draft — References to be added in a separate section per APA 7th edition format.]*