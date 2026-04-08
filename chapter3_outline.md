**CHAPTER III. RESEARCH METHODOLOGY**

**3.1. Research Process**

This study employs a multi-stage quasi-experimental research design to
establish causal inference between green bond issuance and corporate
performance outcomes in the ASEAN region. The overarching methodological
framework integrates three complementary identification strategies:
Propensity Score Matching (PSM), Difference-in-Differences (DiD), and
System Generalized Method of Moments (GMM). This triangulation approach
ensures robustness by addressing distinct sources of endogeneity
inherent in the treatment assignment process.

Green bond issuance is a non-random event. Firms that elect to issue
green bonds differ systematically from non-issuers across multiple
dimensions, including size, financial health, environmental commitment,
and institutional capacity (Flammer, 2021; Tang & Zhang, 2020). A naïve
comparison of issuers and non-issuers would conflate the causal effect
of green bond issuance with the selection effect arising from
pre-existing firm characteristics. This confounding violates the
fundamental identifying assumption of random treatment assignment
required for causal inference.

To address this challenge, the research design implements a three-stage
identification strategy. The first stage involves using Propensity Score
Matching (PSM) to mitigate selection bias by constructing a comparable
control group. PSM estimates the probability of green bond issuance
conditional on observable pre-treatment covariates, subsequently
matching treated firms to control firms with similar propensity scores.
This procedure ensures that subsequent treatment effect estimates are
not driven by observable differences between issuers and non-issuers
(Rosenbaum & Rubin, 1983).

The second stage employs a Difference-in-Differences (DiD) framework,
leveraging the panel structure of the data to control for time-invariant
unobserved heterogeneity---such as corporate culture or management
quality---through entity fixed effects. It simultaneously accounts for
time-varying aggregate shocks, such as macroeconomic shifts or
regulatory changes, via time fixed effects. By utilizing this
dual-control approach, the DiD estimator isolates the treatment effect
from within-firm and within-year variation in outcomes following green
bond issuance (Angrist & Pischke, 2009).

The final stage applies the System Generalized Method of Moments (GMM)
to mitigate dynamic endogeneity issues arising from the inclusion of
lagged dependent variables. When performance metrics, such as
profitability or ESG scores, exhibit temporal persistence, standard
fixed-effects estimators are prone to producing biased results, a
phenomenon known as Nickell bias. System GMM addresses this by using
lagged levels and differences of endogenous variables as internal
instruments, thereby ensuring consistent and robust estimates within a
dynamic panel setting (Blundell & Bond, 1998).

The research workflow proceeds through sequential phases of data
integration, preparation, and rigorous estimation. Initially, financial
data, ESG scores, market metrics, and green bond records are integrated
into a comprehensive panel dataset spanning 2020 to 2025. Following the
construction of treatment indicators, outcomes, and theory-based
controls, the analytical phase commences with propensity score
estimation to ensure covariate balance. Subsequently, DiD estimation is
conducted across multiple fixed-effects specifications, accompanied by
parallel trends testing through an event-study framework to validate the
underlying assumptions. The analysis then advances to System GMM
estimation to address dynamic panel biases, concluding with extensive
robustness checks, including placebo tests and greenwashing screens, to
substantiate the hypothesis testing for both environmental and financial
performance outcomes.

Complete technical specifications for PSM algorithms, DiD models, and
GMM implementations are detailed in Appendix A.7.

**3.2. Research Data**

**3.2.1. Data Sources**

The empirical analysis relies on a comprehensively integrated dataset
constructed from four primary sources. Financial data is retrieved from
LSEG Datastream/Workspace (Refinitiv), providing annual financial
statements, ratios, and firm identifiers for listed companies across six
ASEAN member states (Indonesia, Malaysia, the Philippines, Singapore,
Thailand, and Vietnam) from 2020 to 2025. Environmental, Social, and
Governance (ESG) performance is evaluated using the LSEG ASSET4
database, which supplies composite ESG scores and detailed environmental
metrics, including carbon intensity and scope emissions, primarily for
large- and mid-cap firms representing approximately 18% of the panel
observations. Market valuation data, including market capitalization and
trading volumes, is sourced directly from regional stock exchanges to
facilitate the calculation of market-based metrics such as Tobin\'s Q.
Finally, green bond issuance data is extracted from the LSEG Green Bonds
Database and supplemented by meticulous manual authentication. This
process verifies each of the 333 identified bonds against established
certification standards, such as the Climate Bonds Initiative (CBI) and
the International Capital Market Association (ICMA) Green Bond
Principles, while also evaluating use-of-proceeds documentation to
rigorously screen for greenwashing.

**3.2.2. Sample Selection and Panel Structure**

The initial research universe encompasses all ASEAN-6 listed firms with
available financial data within the LSEG Refinitiv database. The final
unbalanced panel comprises 23,284 firm-year observations from 3,964
unique entities over the six-year observation window. The unbalanced
nature of the panel naturally accommodates dynamic market entries and
exits, such as initial public offerings and delistings. Geographically,
the observations are distributed across Thailand (23.3%), Indonesia
(23.3%), Malaysia (21.3%), Singapore (15.0%), Vietnam (10.1%), and the
Philippines (6.9%).

**Table 3.1 *Panel Data Structure***

  -----------------------------------------------------------------------
  **Dimension**                       **Value**
  ----------------------------------- -----------------------------------
  Total Observations                  23,284

  Number of Entities                  3,964 (identified by org_permid)

  Observation Periods                 6 years (2020--2025)

  Treated Firm-Years                  81 (0.35% of panel)

  Treated Firms                       20 (0.50% of entities)

  Treatment Cohorts                   5 cohorts (2020-2024)
  -----------------------------------------------------------------------

The study also implements a two-pass winsorization procedure to ensure
statistical robustness. In the first pass, 18 raw financial metrics are
winsorized at the 1st and 99th percentiles to mitigate the influence of
extreme values. In the second pass, five computed financial ratios
undergo identical winsorization.

**3.3. Measurement of Variables**

**3.3.1. Dependent Variables**

This study evaluates corporate performance across four primary outcome
variables, encompassing both financial and environmental dimensions.

Financial performance is evaluated using two distinct proxies. The first
is an accounting-based measure, Return on Assets (ROA), representing
internal operational profitability and efficiency of asset deployment.

The second proxy is a market-based measure, Tobin\'s Q, which serves as
a forward-looking indicator of market valuation, capturing the market\'s
assessment of a firm\'s growth opportunities and intangible assets,
potentially reflecting a \"green premium\" (Flammer, 2021).

Furthermore, the implied cost of debt is included to test the greenium
hypothesis, assessing whether issuance leads to a reduction in borrowing
costs (Larcker & Watts, 2020), although severe data sparsity limits the
robustness of this specific metric.

Corporate environmental performance is assessed through two
complementary measures. The first is a composite ESG rating score
sourced from Refinitiv ASSET4, which evaluates a firm\'s overarching
sustainability performance and disclosure practices relative to industry
peers (Berg et al., 2022). To capture direct environmental impact and
address potential disclosure biases inherent in composite scores, the
study employs a second metric: log emissions intensity. A negative
treatment effect on thidirect evidence of substantive environmental
improvement aligned with the fundamental objectives of green bond
financing (Tang & Zhang, 2020).

**Table 3.2 *Dependent Variables***

  --------------------------------------------------------------------------
  **Variable**      **Dimension**           **Description**      **Scale**
  ----------------- ----------------------- -------------------- -----------
  Return on Assets  Financial ---           Net income divided   \<1
  (ROA)             Accounting              by total assets.     

  Tobin\'s Q        Financial - Market      Market               \> 0
                                            capitalization       
                                            divided by total     
                                            assets               

  ESG Score         Environmental -         Refinitiv ESG rating 0--100
                    Composite               (ASSET4)             

  ln(Emissions      Environmental - Direct  Natural log of GHG   \~0--21
  Intensity)                                emissions per unit   
                                            output               

  Implied Cost of   Financial - Cost        Interest expense     \> 0
  Debt                                      divided by total     
                                            debt                 
  --------------------------------------------------------------------------

**3.3.2. Independent Variable (Treatment)**

The primary independent variable is corporate green bond issuance,
operationalized as a binary treatment indicator. Within this framework,
a firm is designated as treated if it issues at least one green bond
during the 2020--2025 observation period. This study abstracts from
continuous intensity dimensions---such as issuance volume or
frequency---to preserve statistical power given the nascent stage of the
ASEAN green bond market and to align with established practices in the
literature (Flammer, 2021; Tang & Zhang, 2020).

To accommodate the distinct identification strategies employed, the
treatment variable is specified in two complementary formats:

*green_bond_issue* (Binary, 0/1): This variable takes the value of 1
exclusively in the inaugural year of a firm's green bond issuance and 0
otherwise. This specification (PSM) analysis to isolate the probability
of initial treatment adoption.

*green_bond_active* (Binary, 0/1): This variable takes the value of 1
from the year of first issuance through the end of the observation
period, and 0 otherwise. This specification is employed for the
panel-based Difference-in-Differences (DiD) and System GMM models,
recognizing that green bond financing represents a persistent shift in
corporate financial and environmental commitment rather than a transient
event.

The treatment adoption is staggered temporally, with cohorts entering
the treatment state progressively from 2020 through 2024. This staggered
structure reflects the evolving regulatory landscape in ASEAN and
necessitates the use of cohort-specific estimation techniques to account
for potential heterogeneity in treatment effects across time. Green bond
identification is based on the LSEG Green Bonds Database, with each
issuance manually verified against established certification standards
(e.g., CBI, ICMA) and use-of-proceeds documentation to ensure the
integrity of the treatment group. issuers with documented green
use-of-proceeds frameworks.

#### **3.3.3. Control Variables**

To mitigate omitted variable bias, all regression specifications include
a vector of firm-level control variables, each measured with a one-year
lag relative to the outcome to reduce simultaneity bias.

**Table 3.3 *Control Variables (One-Year Lagged)***

  -----------------------------------------------------------------------
  **Variable**                       **Operationalization**
  ---------------------------------- ------------------------------------
  Firm Size (*L1_Firm_Size*)         Natural log of total assets at *t* −
                                     1

  Leverage (*L1_Leverage*)           Total debt divided by total assets
                                     at *t* − 1

  Asset Turnover                     Net sales divided by total assets at
  (*L1_Asset_Turnover*)              *t* − 1

  Capital Intensity                  Capital expenditures divided by
  (*L1_Capital_Intensity*)           total assets at *t* − 1

  Cash Ratio (*L1_Cash_Ratio*)       Cash divided by total assets at *t*
                                     − 1

  Asset Tangibility                  Net property, plant, and equipment
  (*asset_tangibility*)              as % of total assets

  Issuer Track Record                Cumulative count of prior green bond
  (*issuer_track_record*)            issuances

  Green Bond Framework               Binary indicator (= 1) if issuer has
  (*has_green_framework*)            a documented framework
  -----------------------------------------------------------------------

### 3.4. Research Models

**3.4.1. Propensity Score Matching Model (First Stage)**

**3.4.1.1. Theoretical Foundation**

The Propensity Score Matching (PSM) procedure addresses selection on
observables by balancing the distribution of pre-treatment covariates
between treated and control groups (Rosenbaum & Rubin, 1983). The
propensity score, defined as the conditional probability of treatment
given observed covariates, serves as a balancing score: conditional on
the propensity score, the distribution of covariates is independent of
treatment assignment.

$e(X_{i})\  = \ P(D_{i} = 1|X_{i})$

***Formula 1: The Propensity Score***

Where $D_{i} = 1$ if firm *i* issued a green bond, $X_{i}$ is the
covariate vector. The balancing property is
$\left( D_{i}\ \bot\ X_{i} \right)$. The score therefore acts as a
balancing score.

For identifying the Average Treatment Effect on the Treated (ATT), the
Conditional Independence Assumption (CIA) is the core requirement. This
assumption ensures that treatment assignment is independent of potential
outcomes conditional on the observed covariates, effectively allowing
for a causal interpretation by simulating a randomized experimental
design within the observational data.

$\left\{ Y_{i}^{(0)},Y_{i}^{(1)} \right\}\ \bot\ D_{i}\ |\ X_{i}$

***Formula 2: Conditional Independence Assumption (CIA)***

**3.4.1.2. Propensity Score Estimation**

To estimate the propensity scores, an enhanced logistic regression model
is employed, specified as:

$\log\left( \frac{e(X_{i})}{1 - e(X_{i})} \right)\  = \ \beta_{0} + \sum_{j = 1}^{n}\beta_{j}X_{ij} + \sum_{k = 1}^{7}\gamma_{k}Industry_{k} + \sum_{m = 1}^{5}\delta_{m}Country_{m}$

***Formula 3: Propensity Score Estimation Model (Logistic)***

*Note.* $X$ are covariates described in the Table 3.3. $Industry$ and
$Country$ explain the fixed effects specifically to the firm in its
country.

These covariates capture the financial capacity (e.g., size, leverage,
liquidity) and operational structure (e.g., turnover, capital intensity)
hypothesized to influence the green bond issuance decision. The model
also controls for fixed industry and country effects to account for
regulatory heterogeneity and sectoral constraints. All continuous
features are standardized to ensure numerical stability. To resolve
issues of perfect and quasi-separation in sparse binary
predictors---such as the presence of a green framework---the estimation
employs L1 penalized logistic regression.

**3.4.1.3. Matching Algorithm and Caliper Selection**

The matching procedure uses nearest-neighbor matching with replacement,
matching one treated firm to up to four control firms (1:4 matching).
The caliper is conventionally set at 0.25 standard deviations of the
logit of the propensity score.

$Caliper = 0.25 \times SD(e(X))$

***Formula 4: Optimal Caliper Width Definition***

However, accommodating the extreme sparsity of the treatment group, a
relaxed caliper of twice the standard Austin criterion is applied to
maximize match retention while ensuring covariate balance.

**3.4.1.4. Common Support and Balance Assessment**

Common support is rigorously enforced by trimming observations with
extreme propensity scores (below 0.10 or above 0.90) (Crump et al.,
2009). This enforces overlap and reduces extrapolation bias.
Post-matching balance is verified using standardized mean differences
(SMD), with all covariates required to fall below the acceptable
threshold of 0.10 (Stuart & Rubin, 2008).

$SMD\  = \ \frac{{\bar{X}}_{treated}\  - \ {\bar{X}}_{control}}{}$

***Formula 5: Standardized Mean Difference (SMD)***

**3.4.2. Difference-in-Differences Model (Second Stage)**

**3.4.2.1. Theoretical Framework**

The Difference-in-Differences (DiD) estimator relies on the Parallel
Trends Assumption, which posits that in the absence of treatment, the
treated and control groups would have followed parallel trajectories in
the outcome variables.

$E\left\lbrack Y_{it}^{(0)} - Y_{i,t - 1}^{(0)}|\ D_{i} = 1 \right\rbrack = E\left\lbrack Y_{it}^{(0)} - Y_{i,t - 1}^{(0)}|\ D_{i} = 0 \right\rbrack$

***Formula 6: Parallel Trends Assumption for Identification***

The DiD estimator identifies the Average Treatment Effect on the Treated
(ATT) as the within-firm variation subsequent to green bond issuance,
net of aggregate temporal shocks. The ATT definition is:

$ATT = E\left\lbrack Y_{it}^{(1)} - Y_{i,t - 1}^{(0)}|\ D_{it} = 1 \right\rbrack$

***Formula 7: Average Treatment Effect on the Treated (ATT)
Definition***

**3.4.2.2. Two-Way Fixed Effects (TWFE) Specification**

The primary baseline DiD specification utilizes a Two-Way Fixed Effects
(TWFE) panel regression estimated on the full dataset. This
specification includes both entity and year fixed effects, alongside the
vector of lagged time-varying controls, with standard errors clustered
at the entity level to account for within-firm serial correlation.

$Y_{it} = \alpha_{i} + \lambda_{t} + \beta\ .green\_ bond\_ active_{it} + \gamma'X_{it} + \epsilon_{it}\ $

***Formula 8: Two-Way Fixed Effects (TWFE) Specification Model***

*Note.* $\alpha_{i}$ are the firm fixed effects; $\lambda_{t}$ are the
year fixed effects; $\beta$ is the treatment effect (ATT); $X_{it}$ are
the time-varied control.

**3.4.2.3. Alternative Specifications**

Besides the TWFE configuration, four other distinct DiD configurations
are estimated for robustness:

1.  **Entity Fixed Effects only:**

$Y_{it} = \alpha_{i} + \beta\ .green\_ bond\_ active_{it} + \gamma'X_{it} + \epsilon_{it}\ $

2.  **Time Fixed Effects only:**

$Y_{it} = \lambda_{t} + \beta\ .green\_ bond\_ active_{it} + \gamma'X_{it} + \epsilon_{it}\ $

3.  **Entity Fixed Effects incorporating a firm-specific linear trend:**

$Y_{it} = \alpha_{i} + \delta.t + \beta\ .green\_ bond\_ active_{it} + \gamma'X_{it} + \epsilon_{it}\ $

4.  **Pooled OLS (neither fixed effect):**

$Y_{it} = \alpha + \lambda_{t} + \beta\ .green\_ bond\_ active_{it} + \gamma'X_{it} + \epsilon_{it}\ $

**3.4.2.4. Cohort-Specific DiD**

Recognizing that standard TWFE estimators can be biased under conditions
of staggered treatment adoption and heterogeneous treatment effects, the
study additionally implements a cohort-specific event study methodology
following Callaway and Sant\'Anna (2021). This approach decomposes the
aggregate ATT by estimating specific effects for each treatment cohort
(, defined by the calendar year of first issuance) using strictly
never-treated firms as the counterfactual control group, thereby
preventing earlier-treated firms from serving as invalid controls for
later-treated cohorts. The aggregated ATT across cohorts is defined as:

$ATT_{g} = E\left\lbrack Y_{it}^{} - Y_{i,g - 1}^{}|G_{i} = g,t \geq g \right\rbrack - E\left\lbrack Y_{it}^{} - Y_{i,g - 1}^{}|G_{i} = \infty,t \geq g \right\rbrack$

$ATT = \sum_{g \in \lbrack 2020,\ 2025)}^{}\frac{n_{g}}{\Sigma n_{g}}.ATT_{g}$

***Formula 9: Aggregated Average Treatment Effect on the Treated across
Cohorts***

**3.4.3. Dynamic Panel Estimation Model (System GMM)**

**3.4.3.1. The Dynamic Panel Problem**

To formally address dynamic endogeneity, unobserved heterogeneity, and
potential simultaneity inherent in corporate performance data, the study
employs System GMM as its primary robustness estimator (Arellano &
Bover, 1995; Blundell & Bond, 1998). Corporate outcomes, such as
profitability or ESG scores, typically exhibit strong temporal
persistence. Including lagged dependent variables in standard panel
models causes a dynamic panel problem and can lead to biased results
(Nickell bias).

$Y_{it} = \rho Y_{i,t - 1} + \beta.green\_ bond\_ active_{it} + \gamma'X_{it} + \alpha_{i} + \epsilon_{it}$

***Formula 10: Dynamic Panel Model Specification with Lagged Dependent
Variable***

**3.4.3.2. System GMM Estimation**

The System GMM estimator resolves this by constructing a system of two
equations: a differenced equation instrumented with lagged levels, and a
levels equation instrumented with lagged differences.

${\Delta Y}_{it} = \rho{\Delta Y}_{i,t - 1} + \beta.\Delta green\_ bond\_ active_{it} + \gamma'{\Delta X}_{it} + \epsilon_{it}$

***Formula 11: First-Differenced Equation Specification***

*Note.* Use lagged levels $Y_{i,t - 2},Y_{i,t - 3},\cdots\ $as
instruments

$Y_{it} = \rho Y_{i,t - 1} + \beta.green\_ bond\_ active_{it} + \gamma'X_{it} + \alpha_{i} + \epsilon_{it}$

**Formula 12: Level Equation Specification**

*Note.* Use lagged differences
${\Delta Y}_{i,t - 2},{\Delta Y}_{i,t - 3},\cdots\ $as instruments

This approach yields consistent estimates by exploiting the internal
instruments of the model (Roodman, 2009).

**3.4.3.3. Instrument Selection and Validity Diagnostics**

To avoid instrument proliferation, instruments are collapsed to one lag
per variable, and automatic lag selection is employed based on data
coverage. Model validity is confirmed by the Hansen J-test for
over-identifying restrictions (where p \> 0.05 indicates instruments are
not rejected) and the Arellano-Bond AR(2) test for the absence of
second-order serial correlation.

## 3.5. Model Evaluation and Estimation

### 3.5.1. Diagnostic Testing

Validation of the core assumptions underlying this quasi-experimental
design requires a sequence of rigorous diagnostic procedures. The
foundational parallel trends assumption is verified using an event-study
specification that incorporates lead and lag indicators of green bond
issuance. For the identification strategy to be valid, pre-treatment
coefficients must remain statistically insignificant, confirming that
the treated and control groups followed comparable outcome trajectories
prior to the intervention.

Conditioning on the propensity score distribution ensures the
enforceability of common support between the groups. By examining
overlap and applying a trimming rule that excludes extreme propensity
scores outside the \[0.10, 0.90\] interval, the analysis reduces
extrapolation bias and ensures that treated firms are compared only to a
truly comparable set of control observations. Following this matching
procedure, covariate balance is quantitatively assessed using the
Standardized Mean Difference (SMD), with a maximum threshold of 0.10
applied to all matching variables to confirm successful balancing.

Dynamic panel diagnostics provide a final layer of validation for the
System GMM estimations. The Arellano-Bond AR(2) test is applied to the
differenced residuals to confirm the absence of second-order serial
correlation, which is critical for instrument validity. Simultaneously,
the Sargan-Hansen J-test evaluates the exogeneity of the overidentifying
restrictions, where an insignificant p-value serves as evidence that the
internal instruments employed in the dynamic model are appropriately
specified.

Finally, the Dynamic Panel Diagnostics for the System GMM model involve
two critical tests: the Arellano-Bond AR(2) test on the differenced
residuals, which must be insignificant to confirm the absence of
second-order serial correlation; and the Sargan-Hansen J-test, which
evaluates the validity of the overidentifying restrictions (instrument
exogeneity), accepting the null hypothesis if the p-value exceeds 0.05.

### 3.5.2. Robustness Checks and Greenwashing Detection

A comprehensive set of Robustness Checks is performed to ensure that the
empirical results are not artifacts of a specific model configuration,
thus lending greater credibility to the findings. Crucially, the
analysis dedicates a core component to **Greenwashing Detection** to
rigorously test the authenticity of green bond commitments, which is the
most critical validity concern in the ASEAN market.

#### **3.5.2.1. Green Bond Authenticity Score Methodology**

To address greenwashing risks and distinguish substantive green bonds
from symbolic certification, we construct a composite authenticity score
for all 333 ASEAN green bonds in the sample. The score is structured to
reflect theoretical priorities from the green bond literature, assigning
the highest weight to verifiable environmental impact.

Formula:

$Authenticity\ Store\  = \ 0.40 \times ESGcomp\  + \ 0.35 \times Certcomp + 0.25 \times Issuercomp$

Where the components and their weights reflect the following priorities:

-   **ESG Improvement Component (40 points):** Assigned the highest
    weight (40%) because verifiable environmental impact is the
    strongest indicator of substantive credibility (Flammer, 2021; Tang
    & Zhang, 2020). This component measures verifiable ESG score
    improvement post-issuance relative to a pre-issuance baseline,
    scaled to \[0, 40\]. Firms with ESG score increases ≥ 5 points
    receive full weight; smaller improvements are scaled proportionally.

-   **Certification Component (35 points):** Assigned 35% weight because
    third-party certification provides independent validation and serves
    as a credible ex-ante signal to reduce information asymmetry (Fatica
    & Panzica, 2021; Hoang et al., 2020). This component grants 20
    points for CBI (Climate Bonds Initiative) certification and 15
    points for ICMA Green Bond Principles adherence, with a maximum of
    35 points.

-   **Issuer Credibility Component (25 points):** Assigned the lowest
    weight (25%) as it signals institutional capacity (Baulkaran, 2019)
    but track records can coexist with limited actual environmental
    impact (Hachenberg & Schiereck, 2018). This component includes 15
    points for prior green bond issuance history and 10 points for
    formal green bond framework documentation, with a maximum of 25
    points.

Based on total score (0-100) the bond is classified as one of the
following: High authenticity (score ≥ 80); Medium authenticity (score
60-79); Low authenticity (score 40-59); Unverified (score \< 40).

This weighting scheme intentionally penalizes bonds with high
certification but no demonstrated ESG improvement, targeting the
\'certification without impact\' greenwashing pattern (Khan & Vismara,
2025).

#### **3.5.2.2. Alternative Robustness Specifications**

In addition to the rigorous greenwashing screen, the robustness analysis
incorporates several key methodological checks to ensure the validity
and stability of the causal estimates. A primary concern is validating
the estimation approach. Therefore, specification robustness is
rigorously assessed by verifying the primary treatment effect across
five alternative Difference-in-Differences (DiD) configurations, moving
beyond the baseline Two-Way Fixed Effects model.

Furthermore, to account for potential variations in impact due to
firm-specific structural characteristics, a detailed heterogeneity
analysis is conducted. This involves partitioning the sample based on
firm size, using a median split of total assets, to systematically
examine whether the treatment effect varies between large and small
firms. This step addresses the conjecture that institutional capacity
and market scrutiny may lead to differential outcomes across the
corporate size spectrum.

Finally, confirming the temporal stability of the effect is critical
given the staggered nature of green bond issuance across the ASEAN
markets. A specific cohort analysis is performed to estimate the Average
Treatment Effect on the Treated (ATT) separately for different treatment
cohorts, defined by their respective years of issuance. This analysis
ensures that the aggregated treatment effect is not driven by specific
cohort dynamics and confirms the consistency of the impact over time.

**3.5.3. Statistical Inference**

All statistical inference is based on two-sided hypothesis testing
against the null hypothesis $H_{0}:\ \beta = 0$.

Given the exploratory nature of the heterogeneity and robustness
analyses, an estimated effect is interpreted as substantive evidence
only when it demonstrates both statistical significance and consistent
directional effects across the various identification strategies and
robustness checks.
