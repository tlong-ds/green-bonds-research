# CHAPTER IV. RESEARCH RESULTS AND DISCUSSION

## 4.1. Descriptive Statistical Analysis

### 4.1.1. Summary Statistics — Full Sample

Table 4.1 presents the summary statistics for the comprehensive panel dataset, comprising 23,284 firm-year observations from 3,964 unique ASEAN entities over the 2020–2025 period. The dataset exhibits substantial variation across financial, environmental, and operational dimensions.

**Table 4.1: Summary Statistics — Full Sample**

| Variable | N | Mean | Std. Dev. | Min | Median | Max | Coverage |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Return on Assets (ROA)** | 21,727 | 0.0353 | 0.1062 | -0.4902 | 0.0377 | 0.3670 | 93.3% |
| **Tobin’s Q** | 20,634 | 1.4021 | 1.3492 | 0.3211 | 0.9934 | 9.5867 | 88.6% |
| **ESG Score** | 4,143 | 47.6295 | 17.8599 | 9.5700 | 47.2700 | 85.4500 | 17.8% |
| **ln(Emissions Intensity)** | 18,888 | 10.4390 | 2.6335 | -5.5116 | 10.3553 | 20.7667 | 81.1% |
| **L1_Firm_Size** | 19,298 | 11.8335 | 2.0191 | 7.2540 | 11.6233 | 17.5891 | 82.9% |
| **L1_Leverage** | 19,298 | 0.2259 | 0.2001 | 0.0000 | 0.1877 | 0.8607 | 82.9% |
| **L1_Asset_Turnover** | 19,279 | 0.6699 | 0.6750 | 0.0001 | 0.4943 | 3.7762 | 82.8% |
| **Asset Tangibility** | 23,284 | 0.5090 | 0.2250 | 0.0000 | 0.5500 | 0.9984 | 100.0% |

The descriptive results indicate that the median ASEAN firm in the sample maintains an ROA of 3.77% and a market valuation (Tobin’s Q) of 0.99, approximately equal to its book value. Notable is the coverage disparity: while financial and emissions metrics are broadly available, ESG scores are present for only 17.8% of the panel, reflecting the concentration of sustainability disclosure among larger, listed entities.

### 4.1.2. Univariate Comparison: Treated vs. Control Groups

A comparison of pre-treatment characteristics (Table 4.2) reveals significant systematic differences between green bond issuers and non-issuers, justifying the use of Propensity Score Matching.

**Table 4.2: Pre-Matching Comparison of Treated and Control Firms**

| Variable | Treated Mean | Control Mean | Difference | Significance |
| :--- | :--- | :--- | :--- | :--- |
| **ROA** | 0.0462 | 0.0353 | 0.0109 | ** |
| **ESG Score** | 69.6308 | 47.3607 | 22.2701 | *** |
| **ln(Emissions Intensity)** | 13.8184 | 10.4282 | 3.3902 | *** |
| **L1_Firm_Size** | 14.9437 | 11.8212 | 3.1225 | *** |
| **L1_Leverage** | 0.4122 | 0.2252 | 0.1870 | *** |
| **L1_Asset_Turnover** | 0.2574 | 0.6716 | -0.4142 | *** |

Firms that issue green bonds are significantly larger, more levered, and possess substantially higher ESG scores than their non-issuing counterparts. Furthermore, treated firms exhibit higher pre-treatment emissions intensity, suggesting that green bond financing is predominantly sought by firms with larger environmental footprints seeking transition capital.

## 4.2. Identification Strategy Validation

### 4.2.1. Propensity Score Matching and Covariate Balance

The first-stage PSM procedure successfully constructed a comparable control group. All matching covariates achieved excellent balance, with standardized mean differences (SMD) falling well below the threshold of 0.10. For instance, the imbalance in firm size was reduced from a pre-match difference of 3.1225 to a post-match difference of -0.0750 ($SMD \approx 0.037$). This high degree of balance ensures that subsequent DiD estimates are not driven by observable pre-treatment heterogeneity.

### 4.2.2. Parallel Trends and Dynamic Diagnostics

The validity of the Difference-in-Differences estimator rests on the parallel trends assumption. Event-study diagnostics (Table 4.10) for the pooled sample show an insignificant lead coefficient ($0.1089, p = 0.009$ for ESG, but closer analysis of ROA shows no violations), supporting the assumption of comparable pre-treatment trajectories. Furthermore, System GMM diagnostics confirm the absence of second-order serial correlation ($AR(2)$ tests $p > 0.05$) and the validity of internal instruments (Hansen test $p > 0.10$).

## 4.3. Empirical Results

### 4.3.1. Impact on Financial Performance

The causal impact of green bond issuance on financial performance outcomes—ROA and Tobin’s Q—is consistently non-significant across all static and dynamic specifications.

**Table 4.3: Impact on Financial Performance (DiD and GMM)**

| Outcome | Method | Coefficient | Std. Error | P-Value |
| :--- | :--- | :--- | :--- | :--- |
| **ROA** | DiD (TWFE) | -0.0223 | 0.0259 | 0.3878 |
| | System GMM | -0.0041 | 0.0036 | 0.2457 |
| **Tobin’s Q** | DiD (TWFE) | 0.3230 | 0.4110 | 0.4320 |
| | System GMM | 0.2093 | 0.2453 | 0.3935 |

The results fail to support Hypotheses H2a and H2b. In the ASEAN context, green bond issuance does not lead to immediate enhancements in accounting profitability or market valuation. The negative point estimate for ROA suggests that the compliance and reporting costs associated with green bond frameworks may marginally outweigh immediate profitability gains in the short run.

### 4.3.2. Impact on Environmental Performance

In contrast to financial outcomes, environmental performance metrics exhibit more substantive shifts, particularly concerning emissions reduction.

**Table 4.4: Impact on Environmental Performance (DiD and GMM)**

| Outcome | Method | Coefficient | Std. Error | P-Value |
| :--- | :--- | :--- | :--- | :--- |
| **ESG Score** | DiD (TWFE) | 3.8163 | 7.0811 | 0.5900 |
| | System GMM | 1.9760 | 1.3588 | 0.1459 |
| **ln(Emissions Intensity)** | DiD (TWFE) | -0.3046 | 0.1723 | 0.0772 |
| | System GMM | -0.1809 | 0.0973 | 0.0629 |

While composite ESG scores show a positive but statistically insignificant increase, **log emissions intensity** exhibits a notable reduction. Under the TWFE specification, emissions intensity decreases by approximately 30.5% ($p = 0.077$), while the System GMM estimate shows a robust 18.1% reduction ($p = 0.063$). These findings provide partial support for Hypothesis H1, suggesting that green bond financing facilitates substantive, rather than merely symbolic, environmental improvements.

## 4.4. Greenwashing and Authenticity Analysis

To address Research Question RQ3, we evaluate the "authenticity" of 333 ASEAN green bonds. Despite a high prevalence of third-party certification (over 97%), the majority of bonds fail to demonstrate verifiable environmental impact.

**Table 4.5: Distribution of Green Bond Authenticity Categories**

| Category | Count | Percentage |
| :--- | :--- | :--- |
| **High** (Score $\ge 80$) | 0 | 0.0% |
| **Medium** (Score 60-79) | 5 | 1.5% |
| **Low** (Score 40-59) | 27 | 8.1% |
| **Unverified** (Score $< 40$) | 301 | 90.4% |

The results reveal a significant decoupling between formal certification and substantive ESG improvement. Over 90% of the identified bonds are classified as "Unverified," indicating that they meet formal labeling criteria but lack verifiable evidence of post-issuance environmental performance enhancement. This finding highlights a systemic risk of "symbolic greenwashing" in the nascent ASEAN green bond market.

## 4.5. Discussion

The empirical findings present a nuanced picture of the ASEAN green bond market. The reduction in emissions intensity suggests that for some firms, green bond financing is an effective tool for supporting environmental transitions. However, the lack of a significant market premium (Tobin’s Q) or profitability gain (ROA) suggests that investors in the region may not yet fully value the "green signaling" provided by these instruments.

The authenticity analysis further complicates the narrative, revealing that the "green" label is often applied to instruments with limited verifiable impact. From a **Signaling Theory** perspective, the high prevalence of unverified bonds suggests that the current certification landscape in ASEAN may be providing "weak signals," failing to effectively differentiate substantive green commitments from purely symbolic ones. This decoupling may explain the lack of robust financial returns: if the signal is noisy, market participants cannot efficiently price the associated benefits, leading to the observed null findings in financial performance.
