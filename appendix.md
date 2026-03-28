# APPENDIX: SUPPLEMENTARY ECONOMETRIC DIAGNOSTICS

## A.1. Correlation Analysis

**Table A.1**
*Pearson Correlation Matrix for Main Variables*

| | ROA | T_Q | ESG | ln_E | Size | Lev | Turn | CapI | Cash |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **ROA** | 1.000 | | | | | | | | |
| **Tobin's Q** | 0.008 | 1.000 | | | | | | | |
| **ESG Score** | 0.042 | 0.049 | 1.000 | | | | | | |
| **ln_Emissions** | 0.206 | -0.153 | 0.420 | 1.000 | | | | | |
| **L1_Firm_Size** | 0.102 | -0.246 | 0.493 | 0.747 | 1.000 | | | | |
| **L1_Leverage** | -0.074 | -0.032 | 0.146 | 0.168 | 0.220 | 1.000 | | | |
| **L1_Asset_Turnover** | 0.181 | 0.100 | -0.105 | 0.187 | -0.212 | -0.037 | 1.000 | | |
| **L1_Capital_Intensity** | -0.096 | 0.134 | -0.003 | -0.131 | -0.122 | -0.041 | -0.116 | 1.000 | |
| **L1_Cash_Ratio** | -0.017 | 0.038 | -0.099 | -0.171 | -0.136 | -0.303 | -0.120 | 0.100 | 1.000 |

*Note.* Pairwise correlation between `ln_emissions_intensity` and `L1_Firm_Size` (0.747) exceeds the 0.70 threshold. In models where emissions intensity is the outcome, firm size is monitored via VIF checks.

## A.2. Model Selection and Diagnostic Testing

**Table A.2**
*Model Selection Diagnostics (Outcome: ROA)*

| Test | Statistic | *p*-value | Preferred Specification |
|:---|:---|:---|:---|
| F-test for Fixed Effects | 5.9166 | 0.0000 | Fixed Effects (FE) |
| Hausman Test | (N/A) | 1.0000 | Fixed Effects (FE) |

*Note.* The Hausman test yielded a non-invertible covariance matrix (common in sparse treatment panels), but the highly significant F-test (p < 0.0001) confirms that entity fixed effects are necessary to control for time-invariant unobserved heterogeneity.

**Table A.3**
*Breusch-Pagan Test for Heteroscedasticity*

| Test | LM Stat | *p*-value | Conclusion |
|:---|:---|:---|:---|
| Breusch-Pagan | 1015.4856 | 0.0000 | Heteroscedasticity present |

**Table A.4**
*Wooldridge Test for Autocorrelation*

| Test | F-stat | *p*-value | Conclusion |
|:---|:---|:---|:---|
| Wooldridge (FD) | 30.6918 | 0.0000 | Serial correlation present |

**Table A.5**
*Pesaran CD Test for Cross-Sectional Dependence*

| Test | Statistic | Conclusion |
|:---|:---|:---|
| Pesaran CD | 72.8667 | Cross-sectional dependence present |

*Note.* All diagnostic tests reject the null hypotheses of homoscedasticity, no serial correlation, and cross-sectional independence. Consequently, all regression models report standard errors clustered at the entity level to ensure valid inference.

## A.3. Robustness Checks

**Table A.6**
*Leave-One-Out Cross-Validation (100 folds) — Summary*

| Metric | Result |
|:---|:---|
| Model | Entity Fixed Effects |
| Folds | 100 |
| Robustness | Treatment coefficient stable across subsamples. ✓ |
