# Panel Data Structure Tables for Chapter 3

These tables provide comprehensive documentation of the panel data structure for Section 3.2 (Research Data).

---

## Table 3.1: Panel Dimensions and Structure

| Dimension | Value | Notes |
|-----------|-------|-------|
| **Total Observations** | 23,284 | Firm-year pairs |
| **Unique Entities** | 3,964 firms | Identified by org_permid |
| **Time Periods** | 6 years (2020-2025) | Annual frequency |
| **Panel Type** | Unbalanced | Firms may enter/exit sample |
| **Treated Observations** | 81 (0.35%) | Firm-years with active green bond |
| **Treated Firms** | 20 (0.50%) | Unique green bond issuers |
| **Treatment Cohorts** | 5 cohorts (2020-2024) | Staggered treatment adoption |

*Note*: The sample consists of publicly listed companies across six ASEAN markets: Indonesia, Malaysia, Philippines, Singapore, Thailand, and Vietnam. Treatment indicator (`green_bond_active`) equals 1 if a firm has issued at least one green bond by year *t*.

---

## Table 3.2: Temporal Distribution of Observations

| Year | Observations | % of Total | Unique Firms |
|------|--------------|------------|--------------|
| 2020 | 3,773 | 16.20% | 3,773 |
| 2021 | 3,867 | 16.61% | 3,867 |
| 2022 | 3,918 | 16.83% | 3,918 |
| 2023 | 3,930 | 16.88% | 3,930 |
| 2024 | 3,898 | 16.74% | 3,898 |
| 2025 | 3,898 | 16.74% | 3,898 |
| **Total** | **23,284** | **100.00%** | **—** |

*Note*: The panel is approximately balanced across years, with each year contributing 16-17% of total observations. The slight increase in firm count from 2020 to 2023 reflects new listings; stabilization in 2024-2025 reflects maturation of the sample frame. Each year represents a cross-section of active, publicly listed firms in the sample.

---

## Table 3.3: Panel Balance (Observations per Firm)

| Years Observed | Number of Firms | % of Firms | Cumulative % |
|----------------|-----------------|------------|--------------|
| 3 years | 41 | 1.03% | 1.03% |
| 4 years | 78 | 1.97% | 3.00% |
| 5 years | 221 | 5.58% | 8.58% |
| 6 years | 3,624 | 91.42% | 100.00% |
| **Total** | **3,964** | **100.00%** | **—** |

**Panel Balance Statistics:**
- Mean observations per firm: 5.87 years
- Median observations per firm: 6 years
- Standard deviation: 0.46 years

*Note*: The panel is **strongly balanced**, with 91.42% of firms observed for the full 6-year period. Firms with fewer observations typically reflect late entry (IPO post-2020) or early exit (delisting, merger/acquisition). This high degree of balance minimizes attrition bias and supports the validity of entity fixed effects estimation.

---

## Table 3.4: Geographic Distribution

| Country | Observations | % of Total | Unique Firms | % of Firms | Obs/Firm |
|---------|--------------|------------|--------------|------------|----------|
| Thailand | 5,426 | 23.30% | 913 | 23.03% | 5.94 |
| Indonesia | 5,418 | 23.27% | 927 | 23.39% | 5.84 |
| Malaysia | 4,969 | 21.34% | 849 | 21.42% | 5.85 |
| Singapore | 3,500 | 15.03% | 607 | 15.31% | 5.77 |
| Vietnam | 2,361 | 10.14% | 397 | 10.02% | 5.95 |
| Philippines | 1,610 | 6.91% | 271 | 6.84% | 5.94 |
| **Total** | **23,284** | **100.00%** | **3,964** | **100.00%** | **5.87** |

*Note*: The sample exhibits relatively balanced geographic distribution across ASEAN-6 markets. The three largest markets (Thailand, Indonesia, Malaysia) collectively account for 67.9% of observations, reflecting their dominance in regional market capitalization and number of listed companies. Singapore contributes 15% of the sample despite having fewer listings, consistent with its role as a regional financial hub with larger average firm size. All countries show similar panel balance (5.77-5.95 observations per firm), indicating data availability is not systematically biased by geography.

---

## Table 3.5: Green Bond Treatment Timeline

| Year | Active Treated Obs | New Issuances | Cumulative Issuers |
|------|-------------------|---------------|---------------------|
| 2020 | 5 | 5 firms | 5 firms |
| 2021 | 8 | 3 firms | 8 firms |
| 2022 | 12 | 5 firms | 12 firms |
| 2023 | 16 | 5 firms | 16 firms |
| 2024 | 20 | 5 firms | 20 firms |
| 2025 | 20 | 0 firms | 20 firms |
| **Total** | **81** | **20 firms** | **—** |

*Note*: "Active Treated Obs" counts firm-year observations where `green_bond_active = 1` (i.e., firm has issued at least one green bond by year *t*). "New Issuances" counts the number of firms issuing their first green bond in that year (`green_bond_issue = 1`). The staggered adoption pattern creates five distinct treatment cohorts (2020-2024), which motivates the use of cohort-specific difference-in-differences analysis (Callaway & Sant'Anna, 2021) in addition to two-way fixed effects models.

**Treatment Intensity:** Only 0.35% of firm-year observations and 0.50% of firms are treated, reflecting the nascent stage of the green bond market in ASEAN during the observation period (2020-2025).

---

## Table 3.6: Variable Coverage Statistics

| Variable | Overall Coverage | Treated Coverage |
|----------|------------------|------------------|
| | N | % | N | % |
| **Outcome Variables:** | | | | |
| Return on Assets (ROA) | 20,634 | 88.6% | 78 | 96.3% |
| Tobin's Q | 20,634 | 88.6% | 78 | 96.3% |
| ESG Score | 4,143 | 17.8% | 37 | 45.7% |
| Emissions Intensity | 18,888 | 81.1% | 75 | 92.6% |
| Implied Cost of Debt | 169 | 0.7% | 6 | 7.4% |
| **Control Variables (Lagged, t-1):** | | | | |
| Firm Size (ln Assets) | 19,298 | 82.9% | 76 | 93.8% |
| Leverage | 19,298 | 82.9% | 76 | 93.8% |
| Asset Turnover | 19,279 | 82.8% | 76 | 93.8% |
| Cash Ratio | 16,848 | 72.4% | 51 | 63.0% |

*Note*: Variable coverage varies significantly by data source and firm characteristics:

- **High coverage (>80%)**: Financial performance metrics (ROA, Tobin's Q) and emissions data have excellent coverage across both treated and control groups, supporting robust causal inference.

- **Moderate coverage (17.8%)**: ESG Score is available only for large-cap and internationally visible firms, creating a **selection bias** toward high-quality firms. However, treated firms have substantially higher ESG coverage (45.7%), reflecting the fact that green bond issuers tend to be larger, more transparent firms with established ESG reporting.

- **Insufficient coverage (0.7%)**: Implied Cost of Debt has only 169 observations (6 treated), making robust estimation infeasible. This variable is **excluded** from main specifications.

- **Treated firm advantage**: Green bond issuers have systematically higher data availability across all variables (96.3% for ROA/Tobin's Q vs. 88.6% overall), reinforcing the need for propensity score matching to ensure control group comparability.

All control variables are lagged by one year (t-1) to mitigate simultaneity bias and ensure temporal precedence in causal inference.

---

## Data Quality and Representativeness

### Strengths:
1. **High temporal balance**: 91% of firms observed for full 6 years minimizes panel attrition concerns
2. **Comprehensive geographic coverage**: All six major ASEAN markets represented
3. **Strong financial data availability**: >80% coverage for core performance metrics
4. **Adequate treated firm coverage**: 96.3% of treated observations have complete financial data

### Limitations:
1. **ESG data sparsity**: Only 17.8% overall coverage, concentrated in large-cap firms (see Section 4.6.5 for implications)
2. **Treatment sparsity**: Only 20 treated firms (81 obs) limits statistical power for heterogeneity analysis
3. **Cost of debt unavailable**: Insufficient data to test H2c (effect on cost of capital)
4. **Large-cap bias**: Sample overrepresents large, liquid firms due to Refinitiv coverage

Despite these limitations, the panel provides a **credible foundation** for quasi-experimental analysis: strong temporal balance, adequate treatment/control overlap after PSM, and comprehensive coverage of financial outcomes enable robust estimation of causal effects using difference-in-differences and system GMM methods.

---

## Suggested Integration into Chapter 3

**Section 3.2.1: Data Sources** (keep your existing text)

**Section 3.2.2: Panel Structure**

Insert Tables 3.1-3.3 here with brief narrative:

> The final analytical dataset consists of 23,284 firm-year observations from 3,964 unique entities over six years (2020-2025), forming an unbalanced panel. As shown in Table 3.1, the treatment group comprises 20 firms (0.50% of entities) contributing 81 treated observations (0.35% of the panel). Green bond issuance follows a staggered adoption pattern, with five distinct treatment cohorts from 2020 to 2024 (Table 3.5).
>
> Temporal distribution is approximately balanced across years (Table 3.2), and the panel exhibits strong firm-level balance: 91.42% of firms are observed for the full six-year period (Table 3.3), with mean observations per firm of 5.87 years. This high degree of balance minimizes attrition bias and supports entity fixed effects estimation.

**Section 3.2.3: Geographic and Treatment Distribution**

Insert Tables 3.4-3.5 here.

**Section 3.2.4: Variable Coverage and Data Quality**

Insert Table 3.6 here with discussion of coverage limitations and implications for model specification (especially ESG Score's large-cap bias and Cost of Debt insufficiency).

---

*Generated: April 4, 2026*
*Source: processed_data/full_panel_data.csv*
