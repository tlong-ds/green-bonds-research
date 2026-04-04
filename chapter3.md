# CHAPTER III. RESEARCH METHODOLOGY

## 3.1. Research Process

This study employs a multi-stage quasi-experimental research design to establish causal inference between green bond issuance and corporate performance outcomes in the ASEAN region. The overarching methodological framework integrates three complementary identification strategies: **Propensity Score Matching (PSM)**, **Difference-in-Differences (DiD)**, and **System Generalized Method of Moments (GMM)**. This triangulation approach ensures robustness by addressing distinct sources of endogeneity inherent in the treatment assignment process.

### 3.1.1. Quasi-Experimental Design

Green bond issuance is a non-random event. Firms that elect to issue green bonds differ systematically from non-issuers across multiple dimensions — size, financial health, environmental commitment, and institutional capacity (Flammer, 2021; Tang & Zhang, 2020). A naïve comparison of issuers and non-issuers would conflate the **causal effect** of green bond issuance with the **selection effect** arising from pre-existing firm characteristics. This confounding violates the fundamental identifying assumption of random treatment assignment required for causal inference.

To address this challenge, the research design implements a **three-stage identification strategy**:

**Stage 1: Propensity Score Matching (PSM)**  
Mitigates selection bias by constructing a comparable control group. PSM estimates the probability of green bond issuance conditional on observable pre-treatment covariates, then matches treated firms to control firms with similar propensity scores. This ensures that subsequent treatment effect estimates are not driven by observable differences between issuers and non-issuers (Rosenbaum & Rubin, 1983).

**Stage 2: Difference-in-Differences (DiD)**  
Exploits the panel structure of the data to control for time-invariant unobserved heterogeneity (e.g., management quality, corporate culture) through entity fixed effects, and for time-varying aggregate shocks (e.g., macroeconomic conditions, regulatory changes) through time fixed effects. The DiD estimator identifies the treatment effect from within-firm, within-year variation in outcomes following green bond issuance (Angrist & Pischke, 2009).

**Stage 3: System GMM**  
Addresses dynamic endogeneity arising from the inclusion of lagged dependent variables in the model. When outcomes exhibit persistence over time (e.g., profitability, ESG performance), standard fixed effects estimators produce biased estimates (Nickell bias). System GMM uses lagged values of endogenous variables as instruments to obtain consistent estimates in dynamic panel settings (Blundell & Bond, 1998).

### 3.1.2. Research Workflow

The empirical analysis proceeds through the following sequential steps:

1. **Data Collection and Integration**: Aggregate financial data (LSEG Refinitiv), ESG scores (LSEG ASSET4), market data, and green bonds data (LSEG Green Bonds Database + manual authentication) into a unified panel dataset spanning 2020–2025.

2. **Data Preparation**: Construct treatment indicators (`green_bond_issue`, `green_bond_active`), outcome variables (ROA, Tobin's Q, ESG Score, Emissions Intensity, Cost of Debt), and theory-driven control variables (lagged financial ratios).

3. **Propensity Score Estimation**: Estimate propensity scores via logistic regression, calculate optimal caliper width, trim extreme propensity scores, and assess covariate balance.

4. **DiD Estimation**: Estimate treatment effects across multiple specifications (Entity FE, Time FE, TWFE, Entity FE + Trend, Pooled OLS) using the matched sample. Implement cohort-specific DiD for staggered treatment adoption.

5. **Parallel Trends Testing**: Conduct event study analysis with leads and lags of treatment to verify the parallel trends assumption underlying DiD identification.

6. **System GMM Estimation**: Estimate dynamic panel models with lagged dependent variables, using lagged outcomes as instruments. Conduct Arellano-Bond AR tests and Sargan/Hansen overidentification tests to validate instrument exogeneity.

7. **Robustness Checks**: Sensitivity analysis across alternative specifications, placebo tests, subsample analysis by firm size, and greenwashing detection via authenticity scoring.

8. **Hypothesis Testing**: Map empirical results to research questions (RQ1–RQ4) and hypotheses (H1: Environmental Performance, H2: Financial Performance).

---

## 3.2. Research Data

### 3.2.1. Data Sources

This study integrates four primary data sources to construct a comprehensive panel dataset for ASEAN listed companies:

**1. Financial Data (LSEG Refinitiv)**  
- **Coverage**: Publicly listed companies across six ASEAN markets (Indonesia, Malaysia, Philippines, Singapore, Thailand, Vietnam)
- **Variables**: Financial statements (income statement, balance sheet, cash flow), financial ratios (profitability, leverage, liquidity, efficiency), firm identifiers (RIC, ORG_PERMID, ISIN)
- **Frequency**: Annual data from 2020 to 2025

**2. ESG Data (LSEG ASSET4)**  
- **Coverage**: Large-cap and mid-cap firms with international visibility (approximately 18% of panel observations)
- **Variables**: ESG combined score [0–100], Environmental pillar score, Social pillar score, Governance pillar score, Emissions data (Scope 1, Scope 2, Scope 3), Carbon intensity metrics
- **Frequency**: Annual scores with quarterly updates aggregated to annual

**3. Market Data (Stock Exchanges)**  
- **Coverage**: Stock price data for all listed firms in sample
- **Variables**: Market capitalization, stock prices (daily/monthly aggregated to annual), trading volume
- **Purpose**: Construction of Tobin's Q (market-based valuation metric)

**4. Green Bonds Data (LSEG Green Bonds Database + Manual Authentication)**  
- **Coverage**: All green bonds issued by ASEAN firms during the observation period
- **Variables**: Issue date, maturity date, issue amount, currency, use of proceeds, CBI certification status, ICMA Green Bond Principles adherence, issuer track record, green bond framework documentation
- **Authentication**: Manual verification of 333 ASEAN green bonds via authenticity scoring framework (ESG divergence analysis, certification verification, issuer credibility assessment)

### 3.2.2. Sample Selection and Panel Structure

**Universe**: All publicly listed companies in ASEAN-6 markets with available financial data in LSEG Refinitiv database.

**Final Panel**:
- **Observations**: 23,284 firm-year observations
- **Firms**: 3,964 unique entities
- **Time Period**: 2020–2025 (6 years)
- **Panel Type**: Unbalanced panel (firms may enter/exit the sample due to IPO, delisting, mergers, or data availability)

**Geographic Distribution**:
| Country | Observations | Percentage |
|---------|--------------|------------|
| Thailand | 5,426 | 23.3% |
| Indonesia | 5,418 | 23.3% |
| Malaysia | 4,969 | 21.3% |
| Singapore | 3,500 | 15.0% |
| Vietnam | 2,361 | 10.1% |
| Philippines | 1,610 | 6.9% |

### 3.2.3. Treatment Group Characteristics

**Treatment Definition**: A firm is classified as "treated" if it issued at least one green bond during the observation window (2020–2025).

**Treatment Indicators**:
- **`green_bond_issue`**: Binary indicator equal to 1 in the year of first green bond issuance, 0 otherwise. Used for PSM (cross-sectional treatment assignment).
- **`green_bond_active`**: Binary indicator equal to 1 in the year of issuance and all subsequent years, 0 otherwise. Used for DiD and GMM (post-treatment indicator).

**Treatment Sample**:
- **Treated Firms**: 20 (0.50% of universe)
- **Green Bond Issuance Events**: 23 (some firms issued multiple bonds)
- **Treated Firm-Year Observations**: 81 (0.35% of panel)

**Issuance Timeline**:
| Year | Issuances |
|------|-----------|
| 2020 | 5 |
| 2021 | 3 |
| 2022 | 5 |
| 2023 | 5 |
| 2024 | 5 |

**Treatment Sparsity**: The low treatment rate (0.35%) reflects the nascent stage of green bond market development in ASEAN. This sparsity poses statistical power challenges but accurately reflects the real-world adoption pattern during the study period.

---

## 3.3. Measurement of Variables

### 3.3.1. Dependent Variables

The study examines five outcome variables capturing distinct dimensions of corporate performance:

#### 3.3.1.1. Financial Performance — Accounting-Based

**Return on Assets (ROA)**

$$\\text{ROA}_{it} = \\frac{\\text{Net Income}_{it}}{\\text{Total Assets}_{it}}$$

- **Interpretation**: Measures internal operational efficiency and profitability relative to asset base. A 1-percentage-point increase in ROA indicates that the firm generates an additional 1% return on each dollar of assets deployed.
- **Rationale**: ROA is the canonical measure of accounting-based profitability, widely used in corporate finance research (Fama & French, 1995). It directly tests whether green bond issuance improves internal asset utilization and operational efficiency.
- **Coverage**: 21,727 observations (93.3%); 79 treated observations (97.5%)

#### 3.3.1.2. Financial Performance — Market-Based

**Tobin's Q**

$$\\text{Tobin's Q}_{it} = \\frac{\\text{Market Value of Equity}_{it} + \\text{Total Liabilities}_{it}}{\\text{Total Assets}_{it}}$$

- **Interpretation**: Measures market valuation relative to book value of assets. Q > 1 indicates the market values the firm above its replacement cost, reflecting growth opportunities, intangible assets, or competitive advantages.
- **Rationale**: Tobin's Q captures the market's forward-looking assessment of firm value and growth potential (Tobin, 1969). It tests whether green bond issuance generates a "green premium" through enhanced investor perceptions, reputational capital, or reduced cost of equity (Flammer, 2021).
- **Coverage**: 20,634 observations (88.6%); 78 treated observations (96.3%)

#### 3.3.1.3. Environmental Performance — Composite Metric

**ESG Score**

- **Source**: LSEG ASSET4 ESG Combined Score [0–100]
- **Interpretation**: Composite index aggregating performance across Environmental, Social, and Governance dimensions. Higher scores reflect superior ESG disclosure quality and performance relative to industry peers.
- **Rationale**: ESG scores are the most widely adopted measure of corporate sustainability performance in financial markets (Berg et al., 2022). However, ESG scores primarily capture *disclosure quality* rather than *substantive environmental impact*, motivating the inclusion of direct emissions metrics.
- **Coverage**: 4,143 observations (17.8%); 50 treated observations (61.7%)  
- **Limitation**: Coverage is skewed toward large-cap firms with international visibility, introducing potential sample selection bias.

#### 3.3.1.4. Environmental Performance — Direct Impact

**Log Emissions Intensity**

$$\\text{ln(Emissions Intensity)}_{it} = \\ln\\left(\\frac{\\text{Total GHG Emissions}_{it}}{\\text{Revenue}_{it}}\\right)$$

- **Interpretation**: Measures carbon emissions per dollar of revenue (carbon efficiency). Negative treatment effect indicates reduced emissions intensity post-issuance.
- **Rationale**: Direct emissions intensity is a more credible measure of substantive environmental performance than composite ESG scores. It captures operational carbon efficiency, aligning with the core environmental objective of green bonds (Flammer, 2021; Tang & Zhang, 2020).
- **Log Transformation**: Addresses right-skewness in emissions distributions and facilitates percentage interpretation of coefficients.
- **Coverage**: 18,888 observations (81.1%); 60 treated observations (74.1%)

#### 3.3.1.5. Cost of Capital

**Implied Cost of Debt**

$$\\text{Cost of Debt}_{it} = \\frac{\\text{Interest Expense}_{it}}{\\text{Total Debt}_{it}}$$

- **Interpretation**: Average interest rate paid on debt. A reduction in cost of debt post-issuance would support the "greenium" hypothesis (Larcker & Watts, 2020).
- **Rationale**: Green bonds may enable access to capital at lower rates if investors accept lower yields for sustainable investments (greenium effect). This variable tests the financial channel through which green bonds may reduce financing costs.
- **Coverage**: 169 observations (0.7%); 6 treated observations (7.4%)  
- **Limitation**: Severe data sparsity precludes robust causal estimation. Results for this outcome are reported for completeness but flagged as underpowered.

---

### 3.3.2. Independent Variable (Treatment)

#### Green Bond Issuance Variable

The central independent variable in this study is **green bond issuance**, operationalized as a binary treatment indicator capturing whether a firm has accessed green capital markets. Given the different analytical approaches employed, this study uses two complementary specifications of the treatment variable:

#### Variable Definition and Construction

**`green_bond_issue`** (Binary, 0/1): Equals 1 in the year when a firm issues its first green bond, and 0 otherwise. This specification is used for **cross-sectional propensity score matching** analysis, where the focus is on identifying the immediate impact of treatment adoption.

**`green_bond_active`** (Binary, 0/1): Equals 1 from the year of first green bond issuance onward, and 0 otherwise. This specification is employed for **panel data analysis** (DiD and GMM), recognizing that green bond financing represents an ongoing commitment with persistent effects rather than a one-time event.

The mathematical relationship between these variables is:
```
green_bond_active_{it} = max(green_bond_issue_{i1}, green_bond_issue_{i2}, ..., green_bond_issue_{it})
```

Where `green_bond_issue_{it} = 1` only in the first year of issuance for firm *i*.

#### Data Source and Coverage

Green bond identification is based on **LSEG Green Bonds Database** supplemented by manual verification. The treatment definition includes all bonds that are either: (1) certified under established green bond standards (Climate Bonds Initiative, ICMA Green Bond Principles); or (2) self-labeled as green bonds by issuers with documented green use-of-proceeds frameworks.

**Treatment Distribution**:
- **Total treated firms**: 20 out of 3,964 firms (0.50%)
- **Total treated observations**: 81 out of 23,284 firm-years (0.35%)
- **Treatment cohorts**: 5 cohorts spanning 2020-2024
- **Cohort sizes**: 2020 (5 firms), 2021 (3 firms), 2022 (5 firms), 2023 (5 firms), 2024 (5 firms)

#### Treatment Timing and Staggered Adoption

The treatment exhibits a **staggered adoption pattern** where different firms enter treatment at different time periods. This timing variation is crucial for identification in difference-in-differences specifications:

- **Early adopters (2020)**: 5 firms, providing longest post-treatment observation period
- **Later adopters (2024)**: 4 firms, providing limited post-treatment data
- **No treatment reversals**: Once a firm issues a green bond, `green_bond_active` remains 1 throughout the panel

This staggered timing enables the use of **Callaway and Sant'Anna (2021)** cohort-specific difference-in-differences estimators, which address potential bias from treatment effect heterogeneity across adoption cohorts.

#### Treatment Intensity Considerations

The binary specification necessarily abstracts from **treatment intensity dimensions** including:
- **Issuance amount**: Green bond proceeds as percentage of total debt or market capitalization
- **Issuance frequency**: Number of green bond tranches issued over the observation period  
- **Use-of-proceeds categories**: Energy efficiency, renewable energy, sustainable transportation, etc.

While these dimensions could provide additional analytical insights, the sparse treatment distribution in the sample (20 treated firms) precludes reliable estimation of dose-response relationships. The binary approach follows established precedent in the green finance literature (Flammer, 2021; Tang & Zhang, 2020) and ensures adequate statistical power for hypothesis testing.

#### Variable Validation and Quality Checks

Several validation procedures ensure treatment variable accuracy:

1. **Cross-referencing**: Green bond identification cross-validated against multiple data sources (Bloomberg, Refinitiv, issuer financial reports)

2. **Temporal consistency**: Verification that `green_bond_issue` appears only once per firm and `green_bond_active` follows correct cumulative pattern

3. **Missing data handling**: Firms with incomplete green bond data excluded from treatment group to avoid misclassification

4. **Greenwashing screening**: Manual review of use-of-proceeds documentation to exclude bonds with insufficient green credentials

#### Econometric Implications

The binary treatment structure has several important implications for econometric estimation:

**For Propensity Score Matching**: The 0/1 specification enables standard logistic regression for propensity score estimation and straightforward nearest-neighbor matching procedures.

**For Difference-in-Differences**: The persistent nature of `green_bond_active` allows identification of both **immediate effects** (year of issuance) and **cumulative effects** (post-issuance periods) through dynamic specifications.

**For System GMM**: The treatment variable can be treated as predetermined (firms cannot un-issue green bonds) but not strictly exogenous due to self-selection concerns, motivating the use of lagged instruments.

#### Treatment Assignment Mechanism

Treatment assignment is **non-random**, arising from strategic corporate decisions influenced by:
- Firm characteristics (size, financial capacity, environmental performance)
- Market conditions (green bond pricing, investor demand)
- Regulatory environment (disclosure requirements, taxonomy alignment)
- Stakeholder pressure (institutional investors, civil society, regulators)

This endogenous treatment assignment necessitates the quasi-experimental methodologies employed in this study (PSM, DiD, GMM) to achieve credible causal identification.

The non-random nature of treatment assignment is addressed through the comprehensive empirical strategy outlined in Section 3.4, which combines multiple approaches to control for observable and unobservable sources of selection bias.

---

### 3.3.3. Control Variables

To isolate the causal effect of green bond issuance, the models include a theory-driven set of **lagged control variables** capturing firm characteristics that may confound the treatment-outcome relationship. All controls are lagged by one year (L1) to ensure they are pre-determined relative to contemporaneous outcomes, reducing endogeneity concerns (Angrist & Pischke, 2009).

#### 3.3.3.1. Firm Size

**L1_Firm_Size** = Lag-1 of $\\ln(\\text{Total Assets}_{it})$

- **Rationale**: Larger firms have greater resources, institutional capacity, and stakeholder visibility. Size affects both the propensity to issue green bonds and baseline performance levels (economies of scale).
- **Expected Sign**: Positive for profitability (scale economies), ambiguous for market valuation (growth vs. maturity trade-off).

#### 3.3.3.2. Financial Leverage

**L1_Leverage** = Lag-1 of $\\frac{\\text{Total Debt}_{it}}{\\text{Total Assets}_{it}}$

- **Rationale**: Leverage captures financial risk and capital structure. Highly leveraged firms face greater financial constraints, which may limit their ability to invest in green projects or influence their decision to issue green bonds.
- **Expected Sign**: Negative for profitability (financial distress risk), ambiguous for market valuation (tax shield vs. bankruptcy risk).

#### 3.3.3.3. Asset Turnover

**L1_Asset_Turnover** = Lag-1 of $\\frac{\\text{Revenue}_{it}}{\\text{Total Assets}_{it}}$

- **Rationale**: Asset turnover measures operational efficiency and intensity of asset utilization. Firms with higher turnover generate more revenue per dollar of assets, indicating superior operational performance.
- **Expected Sign**: Positive for profitability and market valuation.

#### 3.3.3.4. Capital Intensity

**L1_Capital_Intensity** = Lag-1 of $\\frac{\\text{Fixed Assets}_{it}}{\\text{Total Assets}_{it}}$

- **Rationale**: Capital-intensive firms (e.g., manufacturing, utilities) have different operational structures, environmental footprints, and green investment opportunities compared to service-based firms.
- **Expected Sign**: Ambiguous. High capital intensity may correlate with higher emissions but also greater opportunities for green capital expenditure.
- **Coverage**: 6.8% (sparse; included when available but not enforced as a required covariate).

#### 3.3.3.5. Liquidity

**L1_Cash_Ratio** = Lag-1 of $\\frac{\\text{Cash and Cash Equivalents}_{it}}{\\text{Current Liabilities}_{it}}$

- **Rationale**: Liquidity captures financial flexibility and the firm's ability to finance investments without external capital. Firms with greater cash reserves may be better positioned to undertake green projects or weather short-run compliance costs.
- **Expected Sign**: Positive for profitability (financial flexibility), positive for market valuation (low distress risk).

#### 3.3.3.6. Asset Tangibility

**asset_tangibility** = $\\frac{\\text{Fixed Assets}_{it}}{\\text{Total Assets}_{it}}$ (contemporaneous)

- **Rationale**: Tangibility measures the proportion of hard assets that can serve as collateral. Tangible assets facilitate access to debt financing and may moderate the relationship between green bond issuance and financial outcomes.
- **Expected Sign**: Positive for leverage capacity, ambiguous for profitability.

---

## 3.4. Research Models

### 3.4.1. Propensity Score Matching Model (First Stage)

#### 3.4.1.1. Theoretical Foundation

Propensity Score Matching (PSM) addresses **selection on observables** by balancing the distribution of pre-treatment covariates between treated and control groups (Rosenbaum & Rubin, 1983). The propensity score, defined as the conditional probability of treatment given observed covariates, serves as a **balancing score**: conditional on the propensity score, the distribution of covariates is independent of treatment assignment.

**Propensity Score**:

$$e(X_i) = P(D_i = 1 \\mid X_i)$$

Where:
- $D_i = 1$ if firm $i$ issued a green bond (treated)
- $X_i$ is a vector of pre-treatment covariates

**Balancing Property**: $(D_i \\perp X_i) \\mid e(X_i)$

**Identification Assumption**: **Conditional Independence Assumption (CIA)**  
$$\\{Y_i^{(0)}, Y_i^{(1)}\\} \\perp D_i \\mid X_i$$

Potential outcomes $(Y^{(0)}, Y^{(1)})$ are independent of treatment assignment conditional on observables $X$. This assumption is untestable but becomes more plausible when $X$ includes rich pre-treatment covariates capturing the treatment selection process.

#### 3.4.1.2. Propensity Score Estimation

**Model**: Logistic Regression

$$\\log\\left(\\frac{e(X_i)}{1 - e(X_i)}\\right) = \\beta_0 + \\beta_1 \\cdot \\text{L1\\_Firm\\_Size}_i + \\beta_2 \\cdot \\text{L1\\_Leverage}_i + \\beta_3 \\cdot \\text{L1\\_Asset\\_Turnover}_i + \\beta_4 \\cdot \\text{L1\\_Capital\\_Intensity}_i + \\beta_5 \\cdot \\text{L1\\_Cash\\_Ratio}_i$$

**Feature Selection Criteria**:
- All features are **lagged by 1 year** to ensure pre-treatment measurement
- Variables capture dimensions known to predict green bond issuance: size (resources), leverage (financial health), operational efficiency, and liquidity
- Variables with perfect collinearity (e.g., `prior_green_bonds`) are excluded

**Standardization**: All features are standardized (mean = 0, standard deviation = 1) before estimation to ensure numerical stability and comparability of coefficients.

#### 3.4.1.3. Caliper Selection

To prevent poor matches, matching is restricted to pairs within a pre-specified **caliper** (maximum allowable propensity score distance). The optimal caliper is calculated using **Austin's (2011) rule**:

$$\\text{Caliper} = 0.25 \\times \\text{SD}(e(X))$$

**Rationale**: Austin (2011) demonstrates via simulation that this rule minimizes mean squared error in treatment effect estimates across a range of data-generating processes.

**Empirical Implementation**: Due to sparse treatment (20 issuers), a **relaxed caliper** of $2 \\times \\text{Austin's caliper}$ is employed to improve match rates while maintaining acceptable balance.

#### 3.4.1.4. Matching Algorithm

**Algorithm**: Nearest Neighbor Matching with Replacement

**Procedure**:
1. For each treated unit $i$, identify all control units $j$ within the caliper: $|e(X_i) - e(X_j)| < \\text{caliper}$
2. Select the control unit with the smallest propensity score distance: $j^* = \\arg\\min_j |e(X_i) - e(X_j)|$
3. Allow **replacement**: The same control unit may be matched to multiple treated units

**Matching Ratio**: 1:4 (one treated unit matched to up to four control units)

**Advantages**:
- Matching with replacement reduces bias (allows better matches) at the cost of increased variance (some controls used multiple times)
- 1:4 ratio balances bias-variance trade-off in sparse treatment settings (Stuart, 2010)

#### 3.4.1.5. Common Support and Trimming

**Common Support Condition**: Matching is restricted to the region where propensity score distributions of treated and control groups overlap.

$$\\text{Common Support} = [\\max(\\min e(X)_{D=1}, \\min e(X)_{D=0}), \\min(\\max e(X)_{D=1}, \\max e(X)_{D=0})]$$

**Trimming Method**: Crump et al. (2009) optimal trimming

- Observations with $e(X) < 0.10$ or $e(X) > 0.90$ are trimmed by default
- This ensures sufficient overlap and reduces extrapolation bias

**Quality Gate**: At least 70% of treated units must be retained after trimming; otherwise, matching is flagged as unreliable.

#### 3.4.1.6. Balance Assessment

Matching quality is assessed via **standardized mean differences (SMD)** for each covariate:

$$\\text{SMD} = \\frac{\\bar{X}_{\\text{treated}} - \\bar{X}_{\\text{control}}}{\\sqrt{\\frac{s^2_{\\text{treated}} + s^2_{\\text{control}}}{2}}}$$

**Benchmark**:
- **Acceptable balance**: $|\\text{SMD}| < 0.10$ (Stuart & Rubin, 2008)
- **Good balance**: $|\\text{SMD}| < 0.05$

**Empirical Results**: All PSM features achieve $|\\text{SMD}| < 0.10$ post-matching, confirming successful balance.

---

### 3.4.2. Difference-in-Differences Model (Second Stage)

#### 3.4.2.1. Theoretical Framework

The Difference-in-Differences (DiD) estimator exploits the panel structure to control for:
- **Time-invariant unobserved heterogeneity** (entity fixed effects $\\alpha_i$)
- **Time-varying aggregate shocks** (time fixed effects $\\lambda_t$)

**Identifying Assumption**: **Parallel Trends**

In the absence of treatment, treated and control firms would have experienced parallel trends in outcomes:

$$E[Y_{it}^{(0)} - Y_{i,t-1}^{(0)} \\mid D_i = 1] = E[Y_{it}^{(0)} - Y_{i,t-1}^{(0)} \\mid D_i = 0]$$

**Estimand**: Average Treatment Effect on the Treated (ATT)

$$ATT = E[Y_{it}^{(1)} - Y_{it}^{(0)} \\mid D_{it} = 1]$$

#### 3.4.2.2. Two-Way Fixed Effects (TWFE) Specification — Preferred

$$Y_{it} = \\alpha_i + \\lambda_t + \\beta \\cdot \\text{green\\_bond\\_active}_{it} + \\gamma' X_{it} + \\epsilon_{it}$$

Where:
- $Y_{it}$: Outcome for firm $i$ in year $t$
- $\\alpha_i$: Firm fixed effects (absorb time-invariant firm characteristics)
- $\\lambda_t$: Year fixed effects (absorb common time shocks)
- $\\beta$: **Treatment effect (ATT)** — the parameter of primary interest
- $X_{it}$: Vector of time-varying control variables (lagged financial ratios)
- $\\epsilon_{it}$: Error term

**Identification**: $\\beta$ is identified from **within-firm, within-year variation** — comparing outcomes before and after green bond issuance for treated firms, relative to control firms over the same time periods.

**Standard Errors**: Clustered at the firm level ($i$) to account for serial correlation in outcomes within firms over time (Bertrand et al., 2004).

#### 3.4.2.3. Alternative Specifications

To assess robustness, the study estimates four additional specifications:

**Specification 1: Entity Fixed Effects Only**

$$Y_{it} = \\alpha_i + \\beta \\cdot \\text{green\\_bond\\_active}_{it} + \\gamma' X_{it} + \\epsilon_{it}$$

- Controls for firm-specific effects but not time shocks
- Expected: Results may be biased if time-varying confounders (e.g., business cycles) affect outcomes

**Specification 2: Time Fixed Effects Only**

$$Y_{it} = \\lambda_t + \\beta \\cdot \\text{green\\_bond\\_active}_{it} + \\gamma' X_{it} + \\epsilon_{it}$$

- Controls for aggregate time shocks but not firm heterogeneity
- Expected: Results may be biased by selection on time-invariant firm quality

**Specification 3: Entity FE + Linear Time Trend**

$$Y_{it} = \\alpha_i + \\delta \\cdot t + \\beta \\cdot \\text{green\\_bond\\_active}_{it} + \\gamma' X_{it} + \\epsilon_{it}$$

- More parsimonious than TWFE (linear trend instead of year dummies)
- Assumes time effects are linear

**Specification 4: Pooled OLS (No Fixed Effects)**

$$Y_{it} = \\alpha + \\beta \\cdot \\text{green\\_bond\\_active}_{it} + \\gamma' X_{it} + \\epsilon_{it}$$

- Baseline for comparison; captures total association (not causal effect)
- Expected: Coefficients should change substantially when FE are added

#### 3.4.2.4. Cohort-Specific DiD (Callaway & Sant'Anna, 2021)

Standard TWFE assumes homogeneous treatment effects across cohorts. When treatment is staggered (firms treated in different years), TWFE can be biased if:
- Treatment effects vary across cohorts
- Earlier-treated firms serve as controls for later-treated firms (contamination)

**Solution**: Estimate cohort-specific ATTs using only **never-treated firms** as controls.

**Cohort-Specific ATT** for cohort $g$:

$$ATT_g = E[Y_{it} - Y_{i,g-1} \\mid G_i = g, t \\geq g] - E[Y_{it} - Y_{i,g-1} \\mid G_i = \\infty, t \\geq g]$$

Where:
- $G_i = g$: Firm first treated in year $g$
- $G_i = \\infty$: Never-treated firm

**Aggregated ATT**:

$$ATT = \\sum_{g \\in \\{2020, 2021, 2022, 2023, 2024\\}} \\frac{n_g}{\\sum_g n_g} \\cdot ATT_g$$

Weighted by cohort size $n_g$.

---

### 3.4.3. Dynamic Panel Estimation Model (System GMM)

#### 3.4.3.1. The Dynamic Panel Problem

When outcomes exhibit persistence over time, the model includes a lagged dependent variable:

$$Y_{it} = \\rho Y_{i,t-1} + \\beta \\cdot \\text{green\\_bond\\_active}_{it} + \\gamma' X_{it} + \\alpha_i + \\epsilon_{it}$$

**Problem**: $Y_{i,t-1}$ is mechanically correlated with $\\alpha_i$ (the firm fixed effect), even if $\\epsilon_{it}$ is i.i.d. This induces **Nickell bias** (Nickell, 1981):
- FE estimator is biased downward for $\\rho$
- Bias is $O(1/T)$ — severe in short panels (here $T = 6$)

#### 3.4.3.2. System GMM Estimation (Blundell & Bond, 1998)

**Solution**: Combine **differenced equations** (Arellano-Bond, 1991) with **levels equations** to improve instrument strength.

**Differenced Equation** (eliminates $\\alpha_i$):

$$\\Delta Y_{it} = \\rho \\Delta Y_{i,t-1} + \\beta \\cdot \\Delta \\text{green\\_bond\\_active}_{it} + \\gamma' \\Delta X_{it} + \\Delta \\epsilon_{it}$$

**Instruments for Differenced Equation**: Lagged levels $(Y_{i,t-2}, Y_{i,t-3}, \\ldots)$

**Levels Equation**:

$$Y_{it} = \\rho Y_{i,t-1} + \\beta \\cdot \\text{green\\_bond\\_active}_{it} + \\gamma' X_{it} + \\alpha_i + \\epsilon_{it}$$

**Instruments for Levels Equation**: Lagged differences $(\\Delta Y_{i,t-1}, \\Delta Y_{i,t-2}, \\ldots)$

**Additional Assumption**: Mean stationarity of initial conditions  
$$E[\\Delta Y_{i,t-1} \\cdot \\alpha_i] = 0$$

#### 3.4.3.3. Instrument Selection and Collapse

**Automatic Lag Selection**: Instruments are selected automatically based on data coverage. For outcome $Y$:
- $L2_Y$, $L3_Y$ (2-year and 3-year lags) are included if they have ≥10% non-missing observations

**Instrument Collapse**: To prevent "instrument proliferation" (Roodman, 2009), which invalidates overidentification tests, instruments are **collapsed** when the panel is large ($N > 500$). This study has 3,964 entities → instruments are collapsed to one lag per variable.

#### 3.4.3.4. Validity Diagnostics

**1. Arellano-Bond AR Test**  
Tests for serial correlation in first-differenced residuals.

- **AR(1)**: Should be **significant** (mechanical correlation in differenced errors)
- **AR(2)**: Should be **insignificant** (validates instrument exogeneity)

**2. Sargan/Hansen Test**  
Tests overidentifying restrictions (H0: all instruments are valid).

- $p > 0.05$: Do not reject H0 → instruments appear valid
- Caveat: Test has low power with few overidentifying restrictions

---

## 3.5. Model Estimation and Evaluation

### 3.5.1. Estimation Procedures

**PSM**: Estimated using `scikit-learn` LogisticRegression with standardized features.

**DiD**: Estimated using `linearmodels.PanelOLS` with entity and/or time effects, clustered standard errors at the entity level.

**System GMM**: Estimated using custom GMM routines with robust rank-checking, automatic instrument selection, and validity diagnostics.

### 3.5.2. Diagnostic Testing

**Parallel Trends**: Event study specification with leads and lags of treatment. Pre-treatment leads should be statistically insignificant if parallel trends hold.

**Common Support**: Propensity score overlap assessed via histograms and summary statistics. Trimming applied to observations outside [0.10, 0.90] range.

**Covariate Balance**: Standardized mean differences calculated for all PSM features. Acceptable if |SMD| < 0.10.

**Serial Correlation**: Arellano-Bond AR(2) test for GMM residuals. Insignificance confirms valid instruments.

**Overidentification**: Hansen J-test for GMM. $p > 0.05$ indicates instruments are not rejected as invalid.

### 3.5.3. Robustness Checks

- **Specification Robustness**: Estimate across five DiD specifications to verify consistency
- **Heterogeneity Analysis**: Subsample analysis by firm size (median split)
- **Greenwashing Detection**: Authenticity scoring framework to distinguish certified vs. verified green bonds
- **Cohort Analysis**: Separate ATTs for each treatment cohort to detect effect heterogeneity

### 3.5.4. Statistical Inference

**Significance Levels**:
- † $p < 0.10$ (marginal significance)
- * $p < 0.05$
- ** $p < 0.01$
- *** $p < 0.001$

**Hypothesis Testing**: Two-sided tests for all coefficients. Null hypothesis: $H_0: \\beta = 0$ (no treatment effect).

**Multiple Testing**: Results are reported without multiple testing corrections. Given the exploratory nature of the heterogeneity and robustness analyses, a conservative interpretation is adopted: only results that are statistically significant and directionally consistent across multiple specifications are interpreted as evidence of treatment effects.

---

*[End of Chapter III]*
