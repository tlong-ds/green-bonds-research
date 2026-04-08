# Descriptive Statistics: Key Variables Analysis

## Summary

This document presents comprehensive descriptive statistics for all key variables used in the green bond impact analysis. The analysis covers 23,284 firm-year observations from 3,964 ASEAN-listed companies (2020-2025), with 81 treated observations (green bond active) and 23,203 control observations. All 13 requested variables are now included.

**Updated:** April 4, 2026 - Reflects all data quality fixes from professor feedback including asset_tangibility variance correction, Capital_Intensity capping, and Cash_Ratio outlier treatment.

---

## Table 1: Descriptive Statistics - Full Sample (N = 23,284)

| Variable | N | Mean | Std Dev | Min | 25th | Median | 75th | Max | Coverage |
|----------|----:|-----:|--------:|----:|-----:|-------:|-----:|----:|---------:|
| **Outcome Variables** | | | | | | | | | |
| Return on Assets (ROA) | 21,727 | 0.035 | 0.106 | -0.490 | 0.007 | 0.038 | 0.076 | 0.367 | 93.3% |
| Tobin's Q | 20,634 | 1.402 | 1.349 | 0.321 | 0.763 | 0.993 | 1.458 | 9.587 | 88.6% |
| ESG Score | 4,143 | 47.630 | 17.860 | 9.570 | 33.790 | 47.270 | 60.950 | 85.450 | 17.8% |
| ln(Emissions Intensity) | 18,888 | 10.439 | 2.633 | -5.512 | 8.784 | 10.355 | 11.939 | 20.767 | 81.1% |
| Implied Cost of Debt | 169 | 0.125 | 0.136 | 0.020 | 0.037 | 0.055 | 0.171 | 0.480 | 0.7% |
| **Control Variables (Lagged)** | | | | | | | | | |
| L1_Firm_Size (ln Assets) | 19,298 | 11.834 | 2.019 | 7.254 | 10.478 | 11.623 | 12.996 | 17.589 | 82.9% |
| L1_Leverage | 19,298 | 0.226 | 0.200 | 0.000 | 0.047 | 0.188 | 0.358 | 0.861 | 82.9% |
| L1_Asset_Turnover | 19,279 | 0.670 | 0.675 | 0.000 | 0.185 | 0.494 | 0.919 | 3.776 | 82.8% |
| L1_Capital_Intensity | 15,550 | 3.603 | 4.622 | 0.246 | 1.002 | 1.703 | 3.941 | 24.377 | 66.8% |
| L1_Cash_Ratio | 16,848 | 0.682 | 1.053 | 0.003 | 0.101 | 0.283 | 0.740 | 5.000 | 72.4% |
| **Firm Characteristics** | | | | | | | | | |
| asset_tangibility | 23,284 | 0.509 | 0.225 | 0.000 | 0.348 | 0.550 | 0.657 | 0.998 | 100.0% |
| issuer_track_record | 23,284 | 0.008 | 0.211 | 0.000 | 0.000 | 0.000 | 0.000 | 9.000 | 100.0% |
| has_green_framework | 23,284 | 0.003 | 0.059 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | 100.0% |

**Notes:**
- Coverage = percentage of non-missing observations out of total 23,284 firm-years
- 25th/75th = 25th and 75th percentile values (interquartile range)
- L1_Capital_Intensity has moderate coverage (66.8%), now suitable for robustness specifications
- Tobin's Q and lagged financial controls have good coverage (>80%)
- asset_tangibility and green bond-specific variables have complete coverage

**Distribution Insights:**
- **ROA**: Interquartile range [0.7%, 7.6%] shows most firms have modest profitability; negative values (below 25th percentile) indicate significant loss-making firms
- **Tobin's Q**: IQR [0.76, 1.46] suggests most firms trade close to book value; median 0.99 indicates efficient market pricing
- **ESG Score**: IQR [33.8, 60.9] represents companies in the 34th-61st percentile range of ESG performance; limited to higher-quality firms with ESG reporting
- **Firm Size**: IQR [10.48, 13.00] in ln(assets) represents medium to large enterprises ($36K - $440K assets)
- **Leverage**: IQR [4.7%, 35.8%] shows wide variation in capital structure; median 18.8% is moderate leverage

---

## Table 2: Treatment vs Control Group Comparison

| Variable | Treated Group (N=81) | Control Group (N=23,203) | Difference Test |
|----------|:--------------------:|:------------------------:|:---------------:|
| | Mean (Std) | Mean (Std) | T-stat (P-val) |
| **Outcome Variables** | | | |
| Return on Assets (ROA) | 0.046 (0.037) | 0.035 (0.106) | **2.611 (0.011)** |
| Tobin's Q | 1.242 (1.060) | 1.403 (1.350) | -1.330 (0.187) |
| ESG Score | 69.631 (13.319) | 47.361 (17.742) | **8.845 (0.000)*** |
| ln(Emissions Intensity) | 13.818 (2.795) | 10.428 (2.626) | **9.383 (0.000)*** |
| Implied Cost of Debt | 0.042 (0.006) | 0.128 (0.138) | **-7.678 (0.000)*** |
| **Control Variables (Lagged)** | | | |
| L1_Firm_Size | 14.944 (1.781) | 11.821 (2.010) | **15.244 (0.000)*** |
| L1_Leverage | 0.412 (0.190) | 0.225 (0.200) | **8.541 (0.000)*** |
| L1_Asset_Turnover | 0.257 (0.359) | 0.672 (0.676) | **-9.985 (0.000)*** |
| L1_Capital_Intensity | 5.351 (4.385) | 3.753 (4.144) | **2.073 (0.046)** |
| L1_Cash_Ratio | 0.782 (0.754) | 0.682 (1.054) | 0.942 (0.351) |
| **Firm Characteristics** | | | |
| asset_tangibility | 0.409 (0.210) | 0.509 (0.225) | **-4.29 (0.000)*** |
| issuer_track_record | 2.420 (2.655) | 0.000 (0.000) | **8.20 (0.000)*** |
| has_green_framework | 1.000 (0.000) | 0.000 (0.000) | **∞ (0.000)*** |

**Significance levels:** *p<0.05, **p<0.01, ***p<0.001

**Key Findings:**

### Financial Performance
1. **ROA Advantage**: Green bond issuers have **higher ROA** (4.6% vs 3.5%, p=0.011), suggesting superior operational efficiency
2. **Market Valuation**: No significant difference in Tobin's Q, indicating similar market-to-book ratios
3. **Lower Cost of Debt**: Treated firms have **significantly lower implied cost of debt** (4.2% vs 12.8%, p<0.001)

### Environmental Performance  
4. **ESG Leadership**: Green bond issuers have **substantially higher ESG scores** (69.6 vs 47.4 on 0-100 scale, p<0.001)
5. **Higher Emissions**: Paradoxically, treated firms have **higher emissions intensity** (ln: 13.8 vs 10.4, p<0.001), potentially indicating selection of high-emitting firms seeking improvement

### Firm Characteristics
6. **Size Effect**: Green bond issuers are **significantly larger** (ln Assets: 14.94 vs 11.82, highly significant)
7. **Higher Leverage**: Treated firms have **higher leverage ratios** (41.2% vs 22.5%, p<0.001)
8. **Lower Operational Efficiency**: Treated firms show **lower asset turnover** (0.26 vs 0.67, p<0.001)
9. **Less Tangible Assets**: Green bond issuers have **lower asset tangibility** (40.9% vs 50.9%, p<0.001)
10. **Perfect Framework Adoption**: All treated firms have green frameworks (selection criterion)
11. **Established Track Record**: Treated firms have **substantial issuance history** (2.42 vs 0.00, p<0.001)

---

## Table 3: Variable Coverage Summary

| Variable | N Observations | Coverage % | Data Quality |
|----------|---------------:|------------|--------------|
| **Perfect Coverage (100%)** | | | |
| asset_tangibility | 23,284 | 100.0% | ✅ Complete |
| issuer_track_record | 23,284 | 100.0% | ✅ Complete |
| has_green_framework | 23,284 | 100.0% | ✅ Complete |
| **High Coverage (>60%)** | | | |
| Return on Assets (ROA) | 21,727 | 93.3% | ✅ Excellent |
| Tobin's Q | 20,634 | 88.6% | ✅ Excellent |
| L1_Firm_Size | 19,298 | 82.9% | ✅ Good |
| L1_Leverage | 19,298 | 82.9% | ✅ Good |
| L1_Asset_Turnover | 19,279 | 82.8% | ✅ Good |
| ln(Emissions Intensity) | 18,888 | 81.1% | ✅ Good |
| L1_Cash_Ratio | 16,848 | 72.4% | ✅ Good |
| L1_Capital_Intensity | 15,550 | 66.8% | ✅ Good |
| **Moderate Coverage (10-60%)** | | | |
| ESG Score | 4,143 | 17.8% | ⚠️ Limited (Large-cap bias) |
| **Insufficient Coverage (<10%)** | | | |
| Implied Cost of Debt | 169 | 0.7% | ❌ Insufficient |

**Coverage Assessment:**
- **Excellent (>90%)**: ROA available for robust main specifications
- **Good (>80%)**: Core financial metrics and emissions data support primary analysis
- **Good (>60%)**: Capital Intensity now suitable for robustness specifications (66.8% coverage, 9.8× improvement)
- **Limited ESG Coverage**: 17.8% availability creates large-cap/transparency bias but includes 50 treated observations (61.7% of treated sample)
- **Insufficient Variables**: Cost of Debt (0.7%) excluded from main specifications due to sparse coverage

---

## Data Quality Assessment

### Coverage Analysis
- **High Coverage (>80%)**: Tobin's Q (88.6%), Financial controls (82.8-82.9%)
- **Moderate Coverage (70-80%)**: L1_Cash_Ratio (72.4%)
- **Low Coverage (<10%)**: L1_Capital_Intensity (6.8%) - excluded from main specifications
- **Complete Coverage (100%)**: All firm characteristic variables

### Treatment Group Representativeness
- **Advantage**: Higher data availability for treated firms across all variables
- **Selection Concern**: Systematic differences in firm characteristics require propensity score matching
- **Sample Size**: 81 treated observations provide adequate power for main effects testing

### Missing Variables Analysis
All 13 requested variables are now **successfully located and included** in the analysis:

✅ **Found all variables:**
- Return on Assets (ROA): `return_on_assets` - 93.3% coverage
- Tobin's Q: `Tobin_Q` - 88.6% coverage  
- ESG Score: `esg_score` - 17.8% coverage
- ln(Emissions Intensity): `ln_emissions_intensity` - 81.1% coverage
- Implied Cost of Debt: `implied_cost_of_debt` - 0.7% coverage
- All lagged controls (L1_*): 66.8%-82.9% coverage
- All firm characteristics: 100% coverage

---

## Methodological Implications

### For Propensity Score Matching
The significant differences between treated and control groups **validate the need for PSM**:
- Large effect sizes (Cohen's d > 0.8) for firm size, leverage, and asset turnover
- Perfect separation on has_green_framework necessitates exact matching
- Issuer_track_record provides additional matching dimension

### For Difference-in-Differences
- **Parallel Trends Concern**: Systematic pre-treatment differences require careful testing
- **Common Support**: Size differences may limit matching region
- **Time-Varying Confounders**: Need for comprehensive control variable set

### For System GMM
- **Instrument Validity**: Lagged outcome variables appropriate given dynamic relationships
- **Weak Instrument Risk**: Low correlation magnitudes suggest adequate instrument strength
- **Heteroskedasticity**: High standard deviations across variables motivate robust standard errors

---

## Recommended Specifications

Based on data availability and balance concerns:

### Primary Specification (High Coverage Variables):
- **Outcome**: Tobin_Q (88.6% coverage)
- **Treatment**: green_bond_active
- **Controls**: L1_Firm_Size, L1_Leverage, L1_Asset_Turnover (>82% coverage)
- **Matching Variables**: Same as controls + asset_tangibility

### Robustness Specifications:
- **Include L1_Cash_Ratio**: Reduces sample to 72.4% coverage but adds liquidity control
- **Include L1_Capital_Intensity**: Now viable with 66.8% coverage (9.8× improvement from threshold reduction)
- **Industry/Country FE**: Control for sectoral and institutional differences

### Data Enhancement Priorities:
1. ~~Locate ROA variable for financial performance outcomes~~ ✅ **FOUND**
2. ~~Verify ESG_Score availability and coverage patterns~~ ✅ **VERIFIED** 
3. ~~Find emissions intensity measures for environmental outcomes~~ ✅ **FOUND**
4. ~~Improve Capital_Intensity coverage~~ ✅ **FIXED** (6.8% → 66.8%)
5. Assess cost of debt proxies (interest coverage ratios, credit spreads) - **REMAINING**

---

*Generated: April 4, 2026*  
*Data Source: processed_data/full_panel_data.csv*  
*Sample: 23,284 firm-year observations, 3,964 firms, 2020-2025*