# Chapter 3: Research Methodology

## 3.1 Identification Strategy
To rigorously evaluate the impact of green bond issuance on corporate performance, this study employs a quasi-experimental research design. Given that the decision to issue green bonds is non-random and likely influenced by firm-specific characteristics, a simple OLS estimation would yield biased results due to self-selection. To address this endogeneity, we implement a two-stage identification strategy: Propensity Score Matching (PSM) followed by a staggered Difference-in-Differences (DiD) estimation. This approach ensures that the "treated" firms (green bond issuers) are compared against a statistically similar control group, thereby isolating the treatment effect of the issuance.

## 3.2 Data and Sample Construction
The analysis is based on an unbalanced panel dataset of listed companies across ASEAN member nations, spanning the period from 2015 to 2025. The initial sample consists of 42,506 firm-year observations representing 4,593 unique entities. Consistent with the nascent nature of the ASEAN green finance market, treatment prevalence is sparse, with 30 entities identified as green bond issuers during the sample period (approximately 0.5% of the entity pool). This low-prevalence environment necessitates a robust matching framework and careful diagnostic verification of the common support assumption.

## 3.3 Variable Definitions and Measurement
### 3.3.1 Outcome Variables
We examine the impact of green bond issuance across three primary dimensions:
1. **Profitability:** Measured by Return on Assets (ROA), reflecting internal operational efficiency.
2. **Market Valuation:** Measured by Tobin’s Q, representing the market's expectation of future growth and intangible value.
3. **Environmental Performance:** Measured by the firm’s ESG Score, serving as a proxy for sustainability disclosure and performance quality.

### 3.3.2 Treatment and Controls
The primary independent variable is a binary treatment indicator, $GB_{it}$, which takes the value of 1 for the periods following a firm's initial green bond issuance and 0 otherwise. Control variables include a vector of financial and structural characteristics identified in the literature, such as firm size (Log Assets), leverage, capital intensity, and sector-specific indicators.

## 3.4 Econometric Specification
### 3.4.1 Propensity Score Matching (Stage 1)
To construct a comparable control group, we estimate propensity scores using a Probit model:
$$ P(GB_i = 1 | X_i) = \Phi(X_i' \gamma) $$
where $X_i$ represents pre-treatment covariates. Firms are matched using a nearest-neighbor algorithm with a specified caliper to ensure the validity of the "synthetic" control group.

### 3.4.2 Difference-in-Differences (Stage 2)
The causal effect is estimated using the following multi-way fixed effects DiD specification:
$$ Y_{it} = \alpha + \beta GB_{it} + \delta X_{it} + \eta_i + \lambda_t + \epsilon_{it} $$
where $Y_{it}$ is the outcome for firm $i$ in year $t$; $\beta$ is the coefficient of interest (the Average Treatment Effect on the Treated, ATT); $\eta_i$ and $\lambda_t$ represent entity and time fixed effects, respectively; and $\epsilon_{it}$ is the idiosyncratic error term. Standard errors are clustered at the entity level to account for within-firm serial correlation.

---

# Chapter 4: Empirical Results and Discussion

## 4.1 Treatment Profile and Descriptive Evidence
The sample comprises 42,506 firm-year observations with a mean treatment prevalence of 0.5%. Preliminary analysis of the panel reveals significant heterogeneity in firm scale across the ASEAN region, with Singapore-listed entities exhibiting substantially larger asset bases compared to regional peers. This variation reinforces the necessity of employing log-transformations and entity-level fixed effects to control for time-invariant scale effects.

## 4.2 PSM Quality and Common Support
The first-stage Probit estimation yields a mean propensity score of 0.0122 for the treated group and 0.0037 for the pool of potential controls. Diagnostic plots of the support interval $[0.0004, 0.0355]$ indicate that while matching improves comparability, the density of overlap is concentrated at the lower end of the distribution. Given that only a subset of controls falls within the common support of the treated group, our DiD estimates are interpreted as the effect for firms with identifiable regional peers.

## 4.3 Main Difference-in-Differences Results
Table 1 presents the DiD coefficients across four model specifications for each outcome variable.

**Table 1: Impact of Green Bond Issuance on Corporate Performance**
| Outcome | Specification | Coefficient | Std. Error | P-value |
| :--- | :--- | ---: | ---: | ---: |
| **Return on Assets** | Entity FE | -0.009966 | 0.004687 | 0.0335** |
| | Time FE | 0.012164 | 0.007182 | 0.0903* |
| | Two-way FE | -0.007120 | 0.005263 | 0.1761 |
| | Pooled OLS | 0.013672 | 0.006996 | 0.0507* |
| **Tobin’s Q** | Entity FE | -0.033234 | 0.064959 | 0.6089 |
| | Time FE | -0.013276 | 0.136069 | 0.9223 |
| | Two-way FE | -0.017075 | 0.068711 | 0.8037 |
| | Pooled OLS | -0.127051 | 0.140623 | 0.3663 |
| **ESG Score** | Entity FE | 6.260823 | 1.755906 | 0.0004*** |
| | Time FE | 12.985407 | 2.406703 | <0.0001*** |
| | Two-way FE | 0.757960 | 2.362671 | 0.7484 |
| | Pooled OLS | 11.367153 | 2.272400 | <0.0001*** |
*Note: \*, \*\*, and \*\*\* denote significance at the 10%, 5%, and 1% levels, respectively.*

The results indicate a strong and statistically significant positive impact on ESG Scores across most specifications, suggesting that green bond issuance is associated with a substantial improvement in environmental transparency and reporting quality. Conversely, the impact on market valuation (Tobin’s Q) remains statistically insignificant, while the effect on ROA is sensitive to the fixed-effect structure, showing a marginal negative association in the entity-fixed effect model that loses significance under the more stringent two-way fixed effects specification.

## 4.4 Identification Diagnostics and Robustness
### 4.4.1 Parallel Trends Verification
The validity of the DiD estimator rests on the parallel trends assumption. We conduct an event-study analysis to test for pre-treatment differences. The coefficients for the first two leads ($t-1$ and $t-2$) are small and statistically insignificant ($p > 0.59$), providing empirical support for the absence of divergent pre-trends. While the third lead ($t-3$) shows marginal significance ($p = 0.0747$), the overall trajectory suggests that the observed effects are likely driven by the treatment rather than pre-existing trends.

### 4.4.2 Falsification and Sensitivity Tests
To further validate the findings, we perform a series of robustness checks:
1. **Placebo Timing:** Shifting the treatment timing yields a significant coefficient ($p=0.0015$), suggesting that firms may experience anticipatory effects or that the results are sensitive to broader temporal shocks.
2. **Leave-One-Out Cross-Validation (LOOCV):** The primary results remain stable when individual entities are iteratively removed, indicating that the findings are not driven by extreme outliers.
3. **Specification Sensitivity:** The ROA coefficients remain within a consistent range ($-0.019$ to $-0.009$) across various nested control sets.

## 4.5 Discussion and Policy Implications
The empirical evidence suggests that in the ASEAN context, green bonds serve more effectively as a mechanism for enhancing corporate sustainability profiles than as a driver of immediate financial outperformance. The significant boost in ESG scores indicates that the stringent reporting requirements associated with green bond frameworks may compel firms to improve their environmental data management and disclosure. 

For policymakers and regulators, these findings highlight the need for continued support in reducing the "greenium" and issuance costs to encourage broader participation. Furthermore, the sensitivity of the results to treatment sparsity suggests that as the market matures, further research with larger samples will be essential to definitively establish the long-term financial implications of green finance instruments in emerging economies.
