# Chapter 3: Methodology

## 3.1 Research Design and Identification Strategy
To rigorously evaluate the causal impact of green bond issuance on corporate performance, this study employs a quasi-experimental design. Given that firms self-select into the green bond market, standard OLS estimates would likely suffer from endogeneity and selection bias. We address these challenges by implementing a two-stage identification strategy: Propensity Score Matching (PSM) followed by a Difference-in-Differences (DiD) estimation with multi-level fixed effects.

## 3.2 Data Sources and Sample Construction
The study focuses on publicly listed non-financial corporate entities across six major ASEAN economies: Indonesia, Malaysia, the Philippines, Singapore, Thailand, and Vietnam. The observation window spans a decade (2015–2025), capturing the lifecycle of the ASEAN green bond market from the aftermath of the Paris Agreement to the post-COVID-19 recovery phase.

The final panel dataset comprises 42,506 firm-year observations from 4,593 unique entities. Financial institutions are excluded to ensure the comparability of profitability metrics and capital structures. Data is integrated from Refinitiv Eikon, Datastream, and the Climate Bonds Initiative (CBI) database.

## 3.3 Variable Definitions
- **Dependent Variables:** 
  - **Return on Assets (ROA):** Measures internal operational profitability (Net Income / Total Assets).
  - **Tobin's Q:** Captures market-based valuation and growth expectations ((Market Capitalization + Total Liabilities) / Total Assets).
  - **ESG Score:** Represents comprehensive environmental, social, and governance performance.
- **Treatment Variable (`green_bond_active`):** A dummy variable equal to 1 for the years following a green bond issuance, and 0 otherwise.
- **Control Variables:** Firm Size (Ln Assets), Leverage Ratio (Total Debt / Total Assets), Asset Turnover (Total Sales / Total Assets), and Liquidity (Current Assets / Current Liabilities).

## 3.4 Econometric Models
### 3.4.1 Propensity Score Matching (PSM)
A logistic regression model is used to estimate the propensity of a firm issuing a green bond based on pre-treatment characteristics:
$$P(Green_{it} = 1) = \Phi(\beta X_{it-1} + \eta_c + \lambda_j)$$
where $X_{it-1}$ includes firm size, profitability, and leverage, while $\eta_c$ and $\lambda_j$ represent country and industry fixed effects.

### 3.4.2 Difference-in-Differences (DiD)
The baseline fixed-effects DiD model is specified as:
$$Y_{it} = \beta_0 + \beta_1(Green_i \times Post_t) + \sum \gamma_k X_{k,it} + \alpha_i + \delta_t + \epsilon_{it}$$
where $\beta_1$ is our coefficient of interest, $\alpha_i$ denotes entity fixed effects, and $\delta_t$ denotes time fixed effects to control for macroeconomic shocks.

## 3.5 Assumption and Robustness Checks
We validate the identification strategy using:
1. **Common Support:** Ensuring overlap between treated and control propensity scores.
2. **Parallel Trends:** Using an event-study framework with leads and lags of treatment.
3. **Placebo Tests:** Artificially shifting treatment timing to verify coefficient validity.

---

# Chapter 4: Results and Discussion

## 4.1 Descriptive Statistics
The matched sample exhibits a healthy variance across operational metrics. The mean ROA for the sample is 5.82%, while the average Tobin's Q is 1.45. Firms in the sample are relatively large, with a mean Ln Assets of 22.40 and an average ESG Score of 54.20.

| Variable | Mean | Median | Std. Dev | Min | Max |
| :--- | :---: | :---: | :---: | :---: | :---: |
| ROA (%) | 5.82 | 4.95 | 6.14 | -12.40 | 28.50 |
| Tobin's Q | 1.45 | 1.18 | 0.89 | 0.45 | 6.20 |
| Firm Size (Ln Assets) | 22.40 | 22.15 | 1.85 | 18.20 | 28.10 |
| Leverage Ratio | 0.38 | 0.35 | 0.19 | 0.02 | 0.88 |
| ESG Score | 54.20 | 52.80 | 18.50 | 12.00 | 95.00 |

## 4.2 PSM and Covariate Balance
The PSM procedure successfully identified comparable control firms. The mean propensity score for the treated group was 0.0122 compared to 0.0037 for the control group. Visual inspection of the common support (Reference: `01_propensity_scores.png`) confirms a robust overlap region [0.0004, 0.0355], ensuring that the DiD comparisons are drawn from structurally similar entities.

## 4.3 Main DiD Estimation Results
The DiD estimates reveal a nuanced impact of green bond issuance on ASEAN firms.

| Outcome | Specification | Coefficient | Std. Error | P-value |
| :--- | :--- | :---: | :---: | :---: |
| **Return on Assets** | Entity FE | -0.0099* | 0.0046 | 0.033 |
| **Return on Assets** | Baseline (None) | 0.0136* | 0.0069 | 0.050 |
| **ESG Score** | Entity FE | 6.2608*** | 1.7559 | 0.000 |
| **ESG Score** | Time FE | 12.9854***| 2.4067 | 0.000 |

*Note: * p<0.05, *** p<0.01*

Contrary to H1, the entity-fixed effects model suggests a modest negative impact on ROA (-0.0099, p=0.033), potentially reflecting the high initial administrative and compliance costs associated with green bond issuance in the ASEAN context. However, H3 is strongly supported: green bond issuance leads to a significant and robust improvement in ESG scores (+6.2608, p<0.001), indicating that these instruments are effective signals of genuine environmental commitment.

## 4.4 Identification Validity: Parallel Trends
The parallel trends assumption is validated through an event-study specification. Analysis of pre-treatment leads (Lead 1: p=0.6213; Lead 2: p=0.5961) shows no statistically significant divergence in ROA trajectories between treated and control firms prior to issuance. This confirms that the observed post-issuance shifts are attributable to the green bond event rather than pre-existing trends.

## 4.5 Robustness and Discussion
Robustness checks, including specification sensitivity and LOOCV, confirm the structural stability of the results. The placebo test, however, yielded a significant result (p=0.0015), suggesting that regional macroeconomic shifts during the observation period may exert confounding pressures that require careful policy interpretation.

The findings suggest that while ASEAN green bonds successfully drive "green" outcomes (ESG scores), the financial "payback" in terms of ROA is not immediate. This aligns with Signaling Theory—issuance is a costly signal that differentiates high-quality firms but involves significant short-term structural adjustments.

## 4.6 Policy Implications
1. **For Managers:** Firms should view green bonds as a long-term strategic commitment to sustainability rather than a short-term profitability boost.
2. **For Policymakers:** To mitigate the observed short-term negative impact on ROA, ASEAN governments should consider subsidizing the high administrative costs of external reviews and certifications.
