# CHAPTER III. RESEARCH METHODOLOGY

## 3.1. Research Process

This study employs a multi-stage quasi-experimental research design to establish causal inference between green bond issuance and corporate performance outcomes in the ASEAN region. The overarching methodological framework integrates three complementary identification strategies: Propensity Score Matching (PSM), Difference-in-Differences (DiD), and System Generalized Method of Moments (GMM). This triangulation approach ensures econometric robustness by addressing distinct sources of endogeneity inherent in the treatment assignment process.

Green bond issuance is fundamentally a non-random event. Firms that elect to enter the green bond market differ systematically from non-issuers across multiple dimensions, including firm size, financial health, environmental commitment, and institutional capacity (Flammer, 2021; Tang & Zhang, 2020). A naïve comparison of issuers and non-issuers would therefore conflate the causal effect of issuance with the selection effect arising from these pre-existing characteristics. Such confounding violates the fundamental identifying assumption of random treatment assignment required for unbiased causal inference.

To address these challenges, the research design implements a three-stage identification strategy. The first stage utilizes Propensity Score Matching (PSM) to mitigate selection bias on observables by constructing a comparable counterfactual control group. The second stage employs a Difference-in-Differences (DiD) framework, leveraging the panel structure of the data to control for time-invariant unobserved heterogeneity through entity fixed effects and time-varying aggregate shocks via time fixed effects. The final stage applies System GMM to mitigate dynamic endogeneity issues arising from the inclusion of lagged dependent variables, ensuring consistent estimates in a dynamic panel setting (Blundell & Bond, 1998).

The research workflow proceeds from data integration and variable construction to rigorous estimation and diagnostic testing. Following the preparation of a comprehensive panel spanning 2020–2025, the analysis conducts parallel trends testing and covariate balance assessments to validate the underlying identification assumptions.

## 3.2. Research Data

### 3.2.1. Data Sources

The empirical analysis relies on a comprehensively integrated dataset constructed from four primary sources. Financial data is retrieved from LSEG Workspace (formerly Refinitiv), providing annual financial statements and ratios for listed companies across six ASEAN member states: Indonesia, Malaysia, the Philippines, Singapore, Thailand, and Vietnam. Environmental, Social, and Governance (ESG) performance metrics are sourced from the LSEG ASSET4 database, which supplies composite ESG scores and detailed environmental indicators, including carbon intensity and scope emissions. Market valuation data, including market capitalization and trading volumes, is sourced to facilitate the calculation of market-based metrics such as Tobin’s Q. Finally, green bond issuance data is extracted from the LSEG Green Bonds Database and supplemented by manual authentication against established certification standards (e.g., CBI and ICMA Green Bond Principles).

### 3.2.2. Sample Selection and Panel Structure

The research universe encompasses all ASEAN-6 listed firms with available financial data in LSEG Refinitiv. The final unbalanced panel comprises 23,284 firm-year observations from 3,964 unique entities over the 2020–2025 observation window. The unbalanced nature of the panel accommodates dynamic market entries and exits, such as IPOs and delistings, preserving the representative nature of the ASEAN capital markets.

**Table 3.1: Panel Data Structure and Geographic Distribution**

| Dimension | Value |
| :--- | :--- |
| Total Observations | 23,284 |
| Number of Unique Entities | 3,964 |
| Observation Periods | 6 Years (2020–2025) |
| Treated Firms | 20 (0.50% of Entities) |
| Treated Firm-Years | 81 (0.35% of Panel) |
| **Geographic Distribution** | **Percentage of Observations** |
| Thailand | 23.3% |
| Indonesia | 23.3% |
| Malaysia | 21.3% |
| Singapore | 15.0% |
| Vietnam | 10.1% |
| Philippines | 6.9% |

The study implements a two-pass winsorization procedure to ensure statistical robustness. Raw financial metrics and computed ratios are winsorized at the 1st and 99th percentiles to mitigate the influence of extreme values and measurement errors.

## 3.3. Measurement of Variables

### 3.3.1. Dependent Variables

This study evaluates corporate outcomes across five primary dimensions, encompassing financial performance, environmental impact, and the cost of capital. These variables are selected to capture both the internal operational shifts and the external market perceptions following green bond issuance.

Financial performance is evaluated through two distinct proxies. **Return on Assets (ROA)** serves as an accounting-based measure of internal operational profitability and asset efficiency. **Tobin’s Q** is employed as a market-based, forward-looking indicator of corporate valuation, capturing potential "green premiums" associated with sustainable financing (Flammer, 2021). 

Environmental performance is captured via a composite **ESG Score** from LSEG ASSET4, reflecting overarching sustainability disclosure and performance. To address potential "greenwashing" or disclosure biases, the study also utilizes **Log Emissions Intensity** (GHG emissions normalized by revenue) as a direct measure of substantive environmental impact (Tang & Zhang, 2020). Finally, the **Implied Cost of Debt** is included to test for reductions in borrowing costs, although its interpretation is limited by data sparsity in the ASEAN context.

**Table 3.2: Definition and Coverage of Dependent Variables**

| Variable | Operationalization | Rationale | Data Coverage |
| :--- | :--- | :--- | :--- |
| **Return on Assets (ROA)** | Net Income / Total Assets | Accounting profitability | 93.3% |
| **Tobin’s Q** | (Mkt Cap + Total Debt) / Total Assets | Market valuation | 88.6% |
| **ESG Score** | LSEG ASSET4 Composite Score | Sustainability performance | 17.8% |
| **ln(Emissions Intensity)** | ln(GHG Emissions / Revenue) | Direct environmental impact | 81.1% |
| **Cost of Debt** | Interest Expense / Total Debt | Greenium effect | 0.7% |

### 3.3.2. Independent Variable (Treatment)

The primary independent variable is corporate green bond issuance, operationalized as a binary treatment indicator. A firm is designated as treated if it issues at least one green bond during the observation period. To accommodate the distinct identification strategies, the treatment is specified in two formats:

1.  **`green_bond_issue`**: A binary variable taking the value of 1 exclusively in the inaugural year of issuance; used in the PSM analysis to isolate the probability of initial adoption.
2.  **`green_bond_active`**: A binary variable taking the value of 1 from the issuance year through the end of the panel; used in the DiD and GMM models to capture persistent shifts in corporate commitment.

The treatment adoption is staggered across five cohorts (2020–2024), reflecting the progressive development of green finance frameworks in the region.

### 3.3.3. Control Variables

To mitigate omitted variable bias and reduce simultaneity concerns, all specifications include a vector of firm-level control variables, each measured with a one-year lag ($L1$).

**Table 3.3: Specification of Control Variables**

| Variable | Operationalization | Theoretical Rationale |
| :--- | :--- | :--- |
| **Firm Size** | $\ln(\text{Total Assets})$ | Proxies resources and issuance capacity. |
| **Leverage** | $\text{Total Debt} / \text{Total Assets}$ | Controls for financial risk and capital structure. |
| **Asset Turnover** | $\text{Revenue} / \text{Total Assets}$ | Measures operational efficiency. |
| **Capital Intensity** | $\text{CAPEX} / \text{Total Assets}$ | Controls for industry structure and emission scope. |
| **Cash Ratio** | $\text{Cash} / \text{Current Liabilities}$ | Proxies liquidity and financial flexibility. |
| **Asset Tangibility** | $\text{Net PPE} / \text{Total Assets}$ | Indicates collateral capacity. |
| **Issuer Track Record** | Cumulative Green Bond Count | Controls for institutional experience. |
| **Green Framework** | Binary (1 if framework exists) | Proxies ex-ante green commitment. |

## 3.4. Research Models

### 3.4.1. Propensity Score Matching Model (First Stage)

The Propensity Score Matching (PSM) procedure addresses selection on observables by balancing the distribution of pre-treatment covariates between treated and control groups (Rosenbaum & Rubin, 1983). The propensity score, $e(X_i)$, is defined as the conditional probability of treatment given the observed covariate vector:

$$e(X_i) = P(D_i = 1 | X_i)$$

Propensity scores are estimated using a logistic regression model incorporating financial capacity (size, leverage, liquidity) and operational structure (turnover, tangibility) as covariates, alongside industry and country fixed effects:

$$\log\left( \frac{e(X_{i})}{1 - e(X_{i})} \right) = \beta_{0} + \sum \beta_{j}X_{ij} + \sum \gamma_{k}Industry_{k} + \sum \delta_{m}Country_{m}$$

The matching procedure employs 1:4 nearest-neighbor matching with replacement, utilizing a caliper of 0.25 standard deviations of the logit propensity score. Common support is enforced by trimming observations with extreme scores outside the $[0.10, 0.90]$ interval.

### 3.4.2. Difference-in-Differences Model (Second Stage)

The Difference-in-Differences (DiD) framework identifies the Average Treatment Effect on the Treated (ATT) by leveraging within-firm and within-year variation. The baseline Two-Way Fixed Effects (TWFE) specification is:

$$Y_{it} = \alpha_{i} + \lambda_{t} + \beta \cdot \text{green\_bond\_active}_{it} + \gamma'X_{it} + \epsilon_{it}$$

where $\alpha_i$ and $\lambda_t$ represent entity and year fixed effects, respectively, and $\beta$ captures the causal impact of issuance. To account for potential biases in staggered adoption designs, the study also implements cohort-specific DiD estimators (Callaway & Sant’Anna, 2021), decomposing the aggregate ATT into cohort-level effects.

### 3.4.3. Dynamic Panel Estimation Model (System GMM)

To address dynamic endogeneity and the temporal persistence of performance outcomes, the study employs System GMM (Blundell & Bond, 1998). This estimator addresses Nickell bias by constructing a system of equations in levels and differences, using internal instruments to ensure consistency:

$$Y_{it} = \rho Y_{i,t-1} + \beta \cdot \text{green\_bond\_active}_{it} + \gamma'X_{it} + \alpha_i + \epsilon_{it}$$

Model validity is established through the Hansen J-test for over-identifying restrictions and the Arellano-Bond AR(2) test for second-order serial correlation.

## 3.5. Model Evaluation and Estimation

### 3.5.1. Diagnostic Testing

Validation of the identification strategy requires rigorous diagnostic procedures. The foundational **Parallel Trends Assumption** is verified via an event-study specification; pre-treatment coefficients must remain statistically insignificant to confirm comparable trajectories between groups. Post-matching **Covariate Balance** is assessed using Standardized Mean Differences (SMD), with a threshold of $|SMD| < 0.10$ applied to all matching variables.

### 3.5.2. Greenwashing Detection and Authenticity Scoring

To distinguish substantive environmental commitment from symbolic "greenwashing," this study develops a composite **Authenticity Score** for the identified green bonds. The score prioritizes verifiable outcomes over ex-ante signals, structured as follows:

$$\text{Authenticity Score} = 0.40 \times \text{ESG}_{\text{comp}} + 0.35 \times \text{Cert}_{\text{comp}} + 0.25 \times \text{Issuer}_{\text{comp}}$$

Where:
- **ESG Improvement (40%)**: Verifiable enhancement in environmental performance post-issuance.
- **Certification (35%)**: Independent validation via CBI or ICMA standards.
- **Issuer Credibility (25%)**: Institutional track record and formal frameworks.

Bonds are categorized based on their total score (0–100) into High ($\ge 80$), Medium (60–79), Low (40–59), or Unverified ($< 40$) categories. This rigorous screening ensures that treatment effects are evaluated through the lens of instrument integrity.

### 3.5.3. Statistical Inference

Inference is conducted using two-sided hypothesis testing ($H_0: \beta = 0$). Standard errors are clustered at the firm level to account for within-entity serial correlation. Results are interpreted as substantive evidence only when demonstrating directional consistency across DiD and GMM specifications.


