# CHAPTER III. RESEARCH METHODOLOGY

## 3.1. Research Process

This study applies a multi-stage quasi-experimental design to identify the causal effects of green bond issuance on corporate outcomes in ASEAN. The methodology combines three identification strategies: **Propensity Score Matching (PSM)**, **Difference-in-Differences (DiD)**, and **System Generalized Method of Moments (GMM)**. The triangulated design addresses distinct endogeneity risks in treatment assignment.

### 3.1.1. Quasi-Experimental Design

Green bond issuance is non-random. Issuers differ from non-issuers in size, financial capacity, environmental commitment, and institutional capability (Flammer, 2021; Tang & Zhang, 2020). A simple issuer vs. non-issuer comparison would confound **causal effects** with **selection effects**, violating random assignment assumptions.

The identification strategy proceeds in three stages:

**Stage 1: Propensity Score Matching (PSM)**
Constructs a comparable control group by matching treated firms to non-issuers with similar issuance propensities based on pre-treatment covariates (Rosenbaum & Rubin, 1983).

**Stage 2: Difference-in-Differences (DiD)**
Uses panel data to control for time-invariant firm heterogeneity and common shocks via firm and time fixed effects, identifying effects from within-firm changes after issuance (Angrist & Pischke, 2009).

**Stage 3: System GMM**
Handles dynamic endogeneity from lagged outcomes in short panels and obtains consistent estimates using internal instruments (Blundell & Bond, 1998).

### 3.1.2. Research Workflow

1. **Data collection and integration**: Combine financial data (LSEG Refinitiv), ESG scores (LSEG ASSET4), market data, and green bond data (LSEG Green Bonds Database + manual authentication) into a panel for 2020-2025.
2. **Data preparation**: Construct treatment indicators (`green_bond_issue`, `green_bond_active`), outcomes (ROA, Tobin's Q, ESG Score, Emissions Intensity, Cost of Debt), and theory-based controls (lagged ratios).
3. **Propensity score estimation**: Estimate logistic model, select caliper, trim extremes, and assess covariate balance.
4. **DiD estimation**: Estimate multiple FE specifications on the matched sample; implement cohort-specific DiD for staggered adoption.
5. **Parallel trends testing**: Event study with leads and lags to validate DiD assumptions.
6. **System GMM estimation**: Estimate dynamic models with lagged outcomes; run Arellano-Bond and Sargan/Hansen tests.
7. **Robustness checks**: Alternative specifications, placebo tests, subsamples by firm size, and greenwashing screening.
8. **Hypothesis testing**: Map results to RQ1-RQ4 and H1 (Environmental Performance), H2 (Financial Performance).

---

## 3.2. Research Data

### 3.2.1. Data Sources

Four primary sources are integrated to build the ASEAN firm panel:

**1. Financial Data (LSEG Refinitiv)**
- **Coverage**: Listed firms in Indonesia, Malaysia, Philippines, Singapore, Thailand, Vietnam
- **Variables**: Financial statements, ratios, identifiers (RIC, ORG_PERMID, ISIN)
- **Frequency**: Annual, 2020-2025

**2. ESG Data (LSEG ASSET4)**
- **Coverage**: Large- and mid-cap firms; about 18% of panel observations
- **Variables**: ESG combined score, E/S/G pillar scores, emissions (Scope 1-3), carbon intensity
- **Frequency**: Annual scores from quarterly updates

**3. Market Data (Stock Exchanges)**
- **Coverage**: Stock price data for all listed firms
- **Variables**: Market capitalization, prices (daily/monthly to annual), trading volume
- **Purpose**: Tobin's Q construction

**4. Green Bonds Data (LSEG Green Bonds Database + Manual Authentication)**
- **Coverage**: All ASEAN green bonds in 2020-2025
- **Variables**: Issue date, maturity, amount, currency, use of proceeds, CBI/ICMA status, issuer track record, framework documentation
- **Authentication**: Manual verification of 333 bonds via authenticity scoring (ESG divergence, certification checks, issuer credibility)

### 3.2.2. Sample Selection and Panel Structure

**Universe**: All ASEAN-6 listed firms with financial data in LSEG Refinitiv.

**Final Panel**:
- **Observations**: 23,284 firm-year observations
- **Firms**: 3,964 unique entities
- **Time Period**: 2020-2025 (6 years)
- **Panel Type**: Unbalanced (entry/exit via IPOs, delistings, mergers, or data gaps)

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

**Treatment Definition**: A firm is treated if it issues at least one green bond during 2020-2025.

**Treatment Indicators**:
- **`green_bond_issue`**: 1 in the first issuance year, 0 otherwise (PSM).
- **`green_bond_active`**: 1 from issuance year onward, 0 otherwise (DiD, GMM).

**Treatment Sample**:
- **Treated Firms**: 20 (0.50% of universe)
- **Green Bond Issuance Events**: 23
- **Treated Firm-Year Observations**: 81 (0.35% of panel)
Some firms issued multiple bonds.

**Issuance Timeline**:
| Year | Issuances |
|------|-----------|
| 2020 | 5 |
| 2021 | 3 |
| 2022 | 5 |
| 2023 | 5 |
| 2024 | 5 |

**Treatment Sparsity**: The 0.35% treatment rate reflects the early-stage green bond market in ASEAN and implies limited statistical power, but it matches observed adoption patterns.

---

## 3.3. Measurement of Variables

### 3.3.1. Dependent Variables

Five outcomes capture financial and environmental performance.

#### 3.3.1.1. Financial Performance - Accounting-Based

**Return on Assets (ROA)**

$$\text{ROA}_{it} = \frac{\text{Net Income}_{it}}{\text{Total Assets}_{it}}$$

- **Interpretation**: Internal profitability per unit of assets; a 1-percentage-point increase implies an additional 1% return per unit of assets deployed.
- **Rationale**: Canonical accounting measure of profitability (Fama & French, 1995).
- **Coverage**: 21,727 observations (93.3%); 79 treated observations (97.5%).

#### 3.3.1.2. Financial Performance - Market-Based

**Tobin's Q**

$$\text{Tobin's Q}_{it} = \frac{\text{Market Value of Equity}_{it} + \text{Total Liabilities}_{it}}{\text{Total Assets}_{it}}$$

- **Interpretation**: Market valuation relative to asset replacement cost; Q > 1 indicates valuation above replacement cost, reflecting growth opportunities, intangible assets, or competitive advantages.
- **Rationale**: Market-based, forward-looking valuation (Tobin, 1969), capturing potential green premium (Flammer, 2021).
- **Coverage**: 20,634 observations (88.6%); 78 treated observations (96.3%).

#### 3.3.1.3. Environmental Performance - Composite Metric

**ESG Score**

- **Source**: LSEG ASSET4 ESG Combined Score [0-100].
- **Interpretation**: Composite ESG performance and disclosure relative to industry peers.
- **Rationale**: Widely used sustainability measure (Berg et al., 2022), but reflects disclosure more than direct impact.
- **Coverage**: 4,143 observations (17.8%); 50 treated observations (61.7%).
- **Limitation**: Skewed toward large-cap firms, implying potential selection bias.

#### 3.3.1.4. Environmental Performance - Direct Impact

**Log Emissions Intensity**

$$\text{ln(Emissions Intensity)}_{it} = \ln\left(\frac{\text{Total GHG Emissions}_{it}}{\text{Revenue}_{it}}\right)$$

- **Interpretation**: Carbon emissions per unit of revenue; a negative treatment effect indicates reduced emissions intensity post-issuance.
- **Rationale**: Direct environmental performance measure aligned with green bond objectives (Flammer, 2021; Tang & Zhang, 2020).
- **Log Transformation**: Reduces skewness and supports percentage interpretation.
- **Coverage**: 18,888 observations (81.1%); 60 treated observations (74.1%).

#### 3.3.1.5. Cost of Capital

**Implied Cost of Debt**

$$\text{Cost of Debt}_{it} = \frac{\text{Interest Expense}_{it}}{\text{Total Debt}_{it}}$$

- **Interpretation**: Average interest rate on debt.
- **Rationale**: Tests the greenium hypothesis; a post-issuance reduction supports greenium effects (Larcker & Watts, 2020).
- **Coverage**: 169 observations (0.7%); 6 treated observations (7.4%).
- **Limitation**: Severe sparsity; results reported for completeness only.

---

### 3.3.2. Independent Variable (Treatment)

#### Green Bond Issuance Variable

The treatment is a binary indicator for access to green bond markets, implemented in two forms:

**`green_bond_issue`**: 1 only in the first issuance year; used for cross-sectional PSM.

**`green_bond_active`**: 1 in the issuance year and all subsequent years; used for DiD and GMM to capture persistent effects.

Relationship:
```
green_bond_active_{it} = max(green_bond_issue_{i1}, green_bond_issue_{i2}, ..., green_bond_issue_{it})
```

#### Data Source and Coverage

Identification uses the **LSEG Green Bonds Database** plus manual verification. Treatment includes bonds certified under recognized standards (CBI, ICMA GBP) and issuer-labeled green bonds with documented use-of-proceeds frameworks.

**Treatment Distribution**:
- **Total treated firms**: 20 out of 3,964 (0.50%)
- **Total treated observations**: 81 out of 23,284 firm-years (0.35%)
- **Treatment cohorts**: 5 cohorts spanning 2020-2024
- **Cohort sizes**: 2020 (5 firms), 2021 (3 firms), 2022 (5 firms), 2023 (5 firms), 2024 (5 firms)

#### Treatment Timing and Staggered Adoption

Treatment is staggered across years:
- **Early adopters (2020)**: 5 firms with longest post-treatment windows
- **Later adopters (2024)**: 4 firms with limited post-treatment windows
- **No reversals**: Once treated, `green_bond_active` stays 1

This timing variation is crucial for DiD identification and supports cohort-specific DiD (Callaway and Sant'Anna, 2021) to address heterogeneous treatment effects.

#### Treatment Intensity Considerations

Binary treatment abstracts from intensity dimensions:
- **Issuance amount** (as % of debt or market cap)
- **Issuance frequency** (number of tranches)
- **Use-of-proceeds categories** (renewables, transport, efficiency, etc.)

Given the small treated sample (20 firms), dose-response estimation is infeasible. The binary approach follows common practice (Flammer, 2021; Tang & Zhang, 2020) and preserves statistical power for hypothesis testing.

#### Variable Validation and Quality Checks

1. **Cross-referencing**: Bloomberg, Refinitiv, and issuer reports.
2. **Temporal consistency**: `green_bond_issue` occurs once; `green_bond_active` is cumulative.
3. **Missing data handling**: Firms with incomplete bond data excluded from treatment.
4. **Greenwashing screening**: Manual review of use-of-proceeds documentation.

#### Econometric Implications

- **PSM**: Binary treatment enables standard logistic estimation and matching.
- **DiD**: Persistent `green_bond_active` captures immediate and cumulative effects in dynamic specifications.
- **System GMM**: Treatment treated as predetermined, not strictly exogenous, motivating internal instruments.

#### Treatment Assignment Mechanism

Assignment is endogenous and driven by firm size, financial capacity, environmental performance, market conditions, regulation, and stakeholder pressure. This motivates the combined PSM-DiD-GMM strategy described in Section 3.4.

---

### 3.3.3. Control Variables

All controls are lagged by one year (L1) to ensure pre-treatment measurement (Angrist & Pischke, 2009).

#### 3.3.3.1. Firm Size

**L1_Firm_Size** = Lag-1 of $\ln(\text{Total Assets}_{it})$

- **Rationale**: Size proxies resources and issuance capacity.
- **Expected Sign**: Positive for profitability (scale economies); ambiguous for market valuation (growth vs. maturity trade-off).

#### 3.3.3.2. Financial Leverage

**L1_Leverage** = Lag-1 of $\frac{\text{Total Debt}_{it}}{\text{Total Assets}_{it}}$

- **Rationale**: Captures risk and capital structure.
- **Expected Sign**: Negative for profitability (distress risk); ambiguous for market valuation (tax shield vs. bankruptcy risk).

#### 3.3.3.3. Asset Turnover

**L1_Asset_Turnover** = Lag-1 of $\frac{\text{Revenue}_{it}}{\text{Total Assets}_{it}}$

- **Rationale**: Operational efficiency.
- **Expected Sign**: Positive for profitability and valuation.

#### 3.3.3.4. Capital Intensity

**L1_Capital_Intensity** = Lag-1 of $\frac{\text{Fixed Assets}_{it}}{\text{Total Assets}_{it}}$

- **Rationale**: Industry structure and emissions opportunities; high capital intensity may imply higher emissions but also greater scope for green capex.
- **Expected Sign**: Ambiguous.
- **Coverage**: 6.8% (sparse; included when available).

#### 3.3.3.5. Liquidity

**L1_Cash_Ratio** = Lag-1 of $\frac{\text{Cash and Cash Equivalents}_{it}}{\text{Current Liabilities}_{it}}$

- **Rationale**: Financial flexibility and lower distress risk.
- **Expected Sign**: Positive for profitability and valuation.

#### 3.3.3.6. Asset Tangibility

**asset_tangibility** = $\frac{\text{Fixed Assets}_{it}}{\text{Total Assets}_{it}}$ (contemporaneous)

- **Rationale**: Proportion of hard assets that can serve as collateral, affecting financing access.
- **Expected Sign**: Positive for leverage capacity; ambiguous for profitability.

---

## 3.4. Research Models

### 3.4.1. Propensity Score Matching Model (First Stage)

#### 3.4.1.1. Theoretical Foundation

PSM addresses **selection on observables** by balancing covariates between treated and control firms (Rosenbaum & Rubin, 1983). The propensity score is:

$$e(X_i) = P(D_i = 1 \mid X_i)$$

Where $D_i = 1$ if firm $i$ issued a green bond, and $X_i$ is the covariate vector. The balancing property is $(D_i \perp X_i) \mid e(X_i)$.
The propensity score therefore acts as a balancing score.

**Identification Assumption (CIA)**:
$$\{Y_i^{(0)}, Y_i^{(1)}\} \perp D_i \mid X_i$$

#### 3.4.1.2. Propensity Score Estimation

**Model**: Enhanced logistic regression

$$\log\left(\frac{e(X_i)}{1 - e(X_i)}\right) = \beta_0 + \sum_{j=1}^{8} \beta_j X_{ij} + \sum_{k=1}^{7} \gamma_k \text{Industry}_k + \sum_{m=1}^{5} \delta_m \text{Country}_m$$

Covariates:

$$\begin{aligned}
X_{i1} &= \text{L1\_Firm\_Size}_i \\
X_{i2} &= \text{L1\_Leverage}_i \\
X_{i3} &= \text{L1\_Asset\_Turnover}_i \\
X_{i4} &= \text{L1\_Capital\_Intensity}_i \\
X_{i5} &= \text{L1\_Cash\_Ratio}_i \\
X_{i6} &= \text{asset\_tangibility}_i \\
X_{i7} &= \text{L1\_return\_on\_assets}_i \\
X_{i8} &= \text{issuer\_track\_record}_i
\end{aligned}$$

**Theoretical justification**:
1. **Financial capacity** (size, leverage, liquidity) influences issuance feasibility (Flammer, 2021; Hyun et al., 2020).
2. **Operational structure** (turnover, capital intensity, tangibility) reflects industry constraints and green investment needs (Tang & Zhang, 2020).
3. **Performance track record** (ROA, issuer track record) reduces information asymmetry (Fatica et al., 2021; Zerbib, 2019).
4. **Industry controls**: TRBC sector effects (Dorfleitner et al., 2022).
5. **Country controls**: Regulatory and market heterogeneity (Glomsrød & Wei, 2018).

**Feature selection criteria**:
- **Temporal precedence**: Lagged by one year.
- **Coverage threshold**: >75% data coverage.
- **Separation handling**: Exclude variables with quasi-separation.
- **Theoretical grounding**: Each variable justified in literature.

**Standardization**: All continuous features are standardized (mean 0, SD 1) to improve numerical stability and coefficient comparability.

**Perfect separation handling**:
Variables like `has_green_framework` show quasi-separation (>=80% of treated vs. <20% of controls). Perfect separation causes logistic regression to fail or yield infinite coefficients because the MLE does not converge.

**Solutions**:
1. **Variable exclusion** for separation-inducing covariates.
2. **Regularization** via L1 penalized logistic regression for partial separation.

**Empirical implementation**: Variables with separation ratios >10:1 are excluded. Remaining covariates use L1 regularization with C = 1.0.

#### 3.4.1.4. Caliper Selection

Following Austin (2011), which minimizes MSE in simulation:

$$\text{Caliper} = 0.25 \times \text{SD}(e(X))$$

Due to sparse treatment (20 issuers), a relaxed caliper of **2 x Austin's caliper** is used to increase match rates while preserving balance.

#### 3.4.1.5. Matching Algorithm

**Nearest neighbor with replacement** and **1:4 matching**:
1. For treated unit $i$, consider controls within $|e(X_i) - e(X_j)| < \text{caliper}$.
2. Select $j^* = \arg\min_j |e(X_i) - e(X_j)|$.
3. Allow replacement (controls can be reused).

This reduces bias at the cost of higher variance (Stuart, 2010).

#### 3.4.1.6. Common Support and Trimming

Common support:

$$\text{Common Support} = [\max(\min e(X)_{D=1}, \min e(X)_{D=0}), \min(\max e(X)_{D=1}, \max e(X)_{D=0})]$$

**Crump et al. (2009) trimming**:
- Trim observations with $e(X) < 0.10$ or $e(X) > 0.90$.
- At least 70% of treated units must remain; otherwise matching is flagged as unreliable. This enforces overlap and reduces extrapolation bias.

#### 3.4.1.7. Balance Assessment

Balance is assessed with standardized mean differences (SMD):

$$\text{SMD} = \frac{\bar{X}_{\text{treated}} - \bar{X}_{\text{control}}}{\sqrt{\frac{s^2_{\text{treated}} + s^2_{\text{control}}}{2}}}$$

Benchmarks: $|\text{SMD}| < 0.10$ (acceptable) and $< 0.05$ (good) (Stuart & Rubin, 2008). All PSM covariates achieve $|\text{SMD}| < 0.10$ post-matching.

---

### 3.4.2. Difference-in-Differences Model (Second Stage)

#### 3.4.2.1. Theoretical Framework

DiD controls for time-invariant heterogeneity and common shocks via firm and time fixed effects. The **parallel trends** assumption requires:

$$E[Y_{it}^{(0)} - Y_{i,t-1}^{(0)} \mid D_i = 1] = E[Y_{it}^{(0)} - Y_{i,t-1}^{(0)} \mid D_i = 0]$$

The estimand is the **ATT**:

$$ATT = E[Y_{it}^{(1)} - Y_{it}^{(0)} \mid D_{it} = 1]$$

#### 3.4.2.2. Two-Way Fixed Effects (TWFE) Specification - Preferred

$$Y_{it} = \alpha_i + \lambda_t + \beta \cdot \text{green\_bond\_active}_{it} + \gamma' X_{it} + \epsilon_{it}$$

- $\alpha_i$: firm fixed effects
- $\lambda_t$: year fixed effects
- $\beta$: treatment effect (ATT)
- $X_{it}$: time-varying controls (lagged ratios)

Standard errors are clustered at the firm level (Bertrand et al., 2004).
Identification comes from within-firm, within-year variation in outcomes before and after issuance relative to controls.

#### 3.4.2.3. Alternative Specifications

1. **Entity FE only**:
$$Y_{it} = \alpha_i + \beta \cdot \text{green\_bond\_active}_{it} + \gamma' X_{it} + \epsilon_{it}$$

2. **Time FE only**:
$$Y_{it} = \lambda_t + \beta \cdot \text{green\_bond\_active}_{it} + \gamma' X_{it} + \epsilon_{it}$$

3. **Entity FE + linear trend**:
$$Y_{it} = \alpha_i + \delta \cdot t + \beta \cdot \text{green\_bond\_active}_{it} + \gamma' X_{it} + \epsilon_{it}$$

4. **Pooled OLS**:
$$Y_{it} = \alpha + \beta \cdot \text{green\_bond\_active}_{it} + \gamma' X_{it} + \epsilon_{it}$$

Entity-FE-only omits time shocks; time-FE-only omits firm heterogeneity; the linear trend assumes linear time effects; pooled OLS captures associations rather than causal effects.

#### 3.4.2.4. Cohort-Specific DiD (Callaway & Sant'Anna, 2021)

Standard TWFE can be biased when treatment effects vary across cohorts and when earlier-treated firms serve as controls for later-treated firms. To address heterogeneous effects under staggered adoption, cohort-specific ATTs use only never-treated controls:

$$ATT_g = E[Y_{it} - Y_{i,g-1} \mid G_i = g, t \geq g] - E[Y_{it} - Y_{i,g-1} \mid G_i = \infty, t \geq g]$$

Aggregated ATT:

$$ATT = \sum_{g \in \{2020, 2021, 2022, 2023, 2024\}} \frac{n_g}{\sum_g n_g} \cdot ATT_g$$

---

### 3.4.3. Dynamic Panel Estimation Model (System GMM)

#### 3.4.3.1. The Dynamic Panel Problem

With outcome persistence:

$$Y_{it} = \rho Y_{i,t-1} + \beta \cdot \text{green\_bond\_active}_{it} + \gamma' X_{it} + \alpha_i + \epsilon_{it}$$

Lagged outcomes correlate with $\alpha_i$, inducing **Nickell bias** in short panels (Nickell, 1981). The bias is $O(1/T)$ and is severe when $T = 6$.

#### 3.4.3.2. System GMM Estimation (Blundell & Bond, 1998)

**Differenced equation**:

$$\Delta Y_{it} = \rho \Delta Y_{i,t-1} + \beta \cdot \Delta \text{green\_bond\_active}_{it} + \gamma' \Delta X_{it} + \Delta \epsilon_{it}$$

Instruments: lagged levels $(Y_{i,t-2}, Y_{i,t-3}, ...)$.

**Levels equation**:

$$Y_{it} = \rho Y_{i,t-1} + \beta \cdot \text{green\_bond\_active}_{it} + \gamma' X_{it} + \alpha_i + \epsilon_{it}$$

Instruments: lagged differences $(\Delta Y_{i,t-1}, \Delta Y_{i,t-2}, ...)$.

Assumption: mean stationarity of initial conditions,
$$E[\Delta Y_{i,t-1} \cdot \alpha_i] = 0$$

#### 3.4.3.3. Instrument Selection and Collapse

- **Automatic lag selection**: For outcome $Y$, include $L2_Y$ and $L3_Y$ if coverage >=10%.
- **Instrument collapse**: Applied when $N > 500$ to avoid proliferation (Roodman, 2009). With 3,964 entities, instruments are collapsed to one lag per variable.

#### 3.4.3.4. Validity Diagnostics

**Arellano-Bond AR Test**:
- AR(1) should be significant.
- AR(2) should be insignificant.

**Sargan/Hansen Test**:
- $p > 0.05$ indicates instruments are not rejected.
- Low power caveat acknowledged.

---

## 3.5. Model Estimation and Evaluation

### 3.5.1. Estimation Procedures

- **PSM**: `scikit-learn` LogisticRegression with standardized features.
- **DiD**: `linearmodels.PanelOLS` with entity and/or time effects; firm-clustered SEs.
- **System GMM**: Custom routines with rank checks, automatic instrument selection, and diagnostic tests.

### 3.5.2. Diagnostic Testing

- **Parallel trends**: Event study with leads and lags; pre-treatment coefficients should be insignificant.
- **Common support**: Overlap checked via propensity score distributions; trimming to [0.10, 0.90].
- **Covariate balance**: SMD thresholds at 0.10.
- **Serial correlation**: Arellano-Bond AR(2) should be insignificant.
- **Overidentification**: Hansen J-test with $p > 0.05$.

### 3.5.3. Robustness Checks

- **Specification robustness**: Five DiD specifications.
- **Heterogeneity**: Subsamples by firm size (median split).
- **Greenwashing detection**: Authenticity scoring for certified vs. verified bonds (methodology detailed below).
- **Cohort analysis**: ATT by treatment cohort.

#### 3.5.3.1. Green Bond Authenticity Score Methodology

To address greenwashing risks and distinguish substantive green bonds from symbolic certification, we construct a composite authenticity score for all 333 ASEAN green bonds in the sample. The score combines three dimensions:

**Formula**:

$$\text{Authenticity Score} = 0.40 \times \text{ESG}_{\text{comp}} + 0.35 \times \text{Cert}_{\text{comp}} + 0.25 \times \text{Issuer}_{\text{comp}}$$

where:
- $\text{ESG}_{\text{comp}}$: ESG improvement component (0-40 points)
- $\text{Cert}_{\text{comp}}$: Certification component (0-35 points)
- $\text{Issuer}_{\text{comp}}$: Issuer credibility component (0-25 points)

**Component Definitions**:

1. **ESG Improvement Component (40 points)**: Verifiable ESG score improvement post-issuance relative to pre-issuance baseline, scaled to [0, 40]. Firms with ESG score increases ≥ 5 points receive full weight; smaller improvements are scaled proportionally.

2. **Certification Component (35 points)**: Third-party certification status:
   - CBI (Climate Bonds Initiative) certification: 20 points
   - ICMA Green Bond Principles adherence: 15 points
   - Maximum: 35 points if both certifications present

3. **Issuer Credibility Component (25 points)**: Issuer track record and verification framework:
   - Prior green bond issuance history: 15 points
   - Formal green bond framework documentation: 10 points
   - Maximum: 25 points

**Weighting Rationale**:

The weights reflect theoretical priorities from the green bond literature:

- **40% ESG Performance**: Highest weight assigned to verifiable environmental impact, consistent with substantive credibility principles (Flammer, 2021; Tang & Zhang, 2020). Green bonds are environmental instruments; thus, demonstrated ESG improvement is the strongest authenticity indicator.

- **35% Certification**: Third-party certification provides independent validation (Fatica & Panzica, 2021; Lebelle et al., 2020). While certification alone does not guarantee impact, it serves as a credible ex-ante signal reducing information asymmetry (Hoang et al., 2020).

- **25% Issuer Credibility**: Issuer track record and framework documentation signal institutional capacity (Baulkaran, 2019; Bachelet et al., 2019). Lower weight than performance or certification reflects that track records can coexist with limited actual impact (Hachenberg & Schiereck, 2018).

**Authenticity Categories**:

Based on total score (0-100):
- **High authenticity**: Score ≥ 80
- **Medium authenticity**: Score 60-79
- **Low authenticity**: Score 40-59
- **Unverified**: Score < 40

This weighting scheme intentionally penalizes bonds with high certification but no demonstrated ESG improvement, targeting the "certification without impact" greenwashing pattern (Khan & Vismara, 2025).

### 3.5.4. Statistical Inference

**Significance levels**:
- † $p < 0.10$
- * $p < 0.05$
- ** $p < 0.01$
- *** $p < 0.001$

**Hypothesis testing**: Two-sided tests; $H_0: \beta = 0$.

**Multiple testing**: No corrections applied. Given exploratory heterogeneity and robustness analyses, only effects that are significant and directionally consistent across specifications are interpreted as evidence.

---

*[End of Chapter III]*
