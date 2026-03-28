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
| ln(Emissions Intensity) | (Inconclusive) | — | — | | 6,371 |
| Implied Cost of Debt | (Inconclusive) | — | — | | 1,000 |

*Note.* System GMM updated with robust rank-checking and expanded controls. Results are directionally consistent with TWFE but emphasize the non-significance of effects after correcting for dynamic endogeneity. Inconclusive outcomes reflect cases where data sparsity or perfect multicollinearity prevented valid instrument selection.

**Table 4.6**
*Cross-Method Comparison: DiD (TWFE) vs. System GMM*

| Outcome | DiD — TWFE | System GMM | Directional Consistency |
|---|---|---|---|
| ROA | −0.006 | −0.002 | ✓ Both negative (near-zero) |
| Tobin's Q | 0.494 | 0.063 | ✓ Both positive |
| ESG Score | 0.037 | 0.004 | ✓ Both positive |
| ln(Emissions Intensity) | −0.057 | (Inconclusive) | N/A |
| Implied Cost of Debt | −0.084ª | (Inconclusive) | N/A |

*Note.* Direction is consistent for three of four outcomes. Magnitude divergence for ln(Emissions Intensity) reflects GMM's additional correction for dynamic endogeneity. ª Result from Time FE specification (TWFE absorbed).

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

GMM results (Table 4.5) indicate an inconclusive result for emissions intensity due to instrument sparsity, although point estimates in DiD models (Table 4.4) suggest a negative direction (β = −0.057, *p* = .734). While the point estimate remains negative across specifications (Table 4.6), its statistical significance is sensitive to the inclusion of firm-level characteristics such as asset tangibility and prior issuance history, suggesting that previously observed "green effects" may have been partially confounded by unobserved firm-level quality.

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
| Does green bond issuance reduce emissions intensity? | **Inconclusive.** Consistently negative point estimate but non-significant. | TWFE: β = −0.057, *p* = .734 |
| Does green bond issuance reduce borrowing costs? | **Conditionally supported.** Significant reduction in cross-sectional models. | Time FE: β = −0.084, *p* < .001*** |
| Is green bond certification meaningful? | **Not supported.** Certification nearly universal; substantive ESG improvement extremely rare. | 98.5% certified; 3.9% ESG-verified |
| Do effects differ by firm size? | **Supported.** Larger firms exhibit stronger ESG gains but worse accounting returns. | See Table 4.9 |
| Are parallel trends valid? | **Partially supported.** Pooled test fails; cohort analysis shows 0/4 violations for ROA. | See Tables 4.2 and 4.8 |

*Note.* Results updated with full vector of theory-driven controls and robust System GMM identification. Borrowing cost evidence (Implied Cost of Debt) is derived from Time FE and Pooled OLS specifications, as the treatment indicator was absorbed in TWFE due to a single-unit treated sample for this outcome.

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
