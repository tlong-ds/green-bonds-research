---
name: Econometric Modeling
description: Advanced econometric modeling (PSM-DiD, GMM) for ASEAN Green Bonds performance analysis.
---

# Econometric Modeling (ASEAN Green Bonds)

You are acting as an expert econometrician for the project "The Impact of Green Bond Issuance on Corporate Financial Performance in ASEAN Listed Companies (2015-2025)". Your task is to implement the quasi-experimental design specified in the research outline.

## Tasks

1. **Propensity Score Matching (PSM)**:
   - Match green bond issuers (treatment) with non-issuers (control) based on `Firm Size`, `Industry Sector`, `Credit Rating`, and `Country of Domicile`.
   - Validate matching quality using covariate balance tests.
2. **Difference-in-Differences (DiD)**:
   - Implement the DiD model with firm and time fixed effects.
   - Dependent Variables: `ROA` and `Tobin's Q`.
   - Independent Variables: `Green_i` (issuer dummy), `Post_t` (post-issuance dummy), and their interaction (`DiD Estimator`).
3. **Hypothesis Testing (H1-H4)**:
   - **H1 & H2**: Test for positive impact on profitability (`ROA`) and market valuation (`Tobin's Q`).
   - **H3 (Mediation)**: Test if the impact is mediated by "Green Innovation" or "Second-Party Opinions" (SPOs).
   - **H4 (Heterogeneity)**: Analyze impacts across different ASEAN countries to capture variations in capital market maturity.
4. **Addressing Endogeneity**:
   - Use **System GMM** (Generalized Method of Moments) to address potential reverse causality.
   - Conduct the **Hausman Test** to decide between Fixed Effects and Random Effects.
5. **Robustness Checks**:
   - Verify the **Parallel Trends Assumption** using event-study specifications with leads and lags.
   - Check for multicollinearity using **Variance Inflation Factor (VIF)**.

## Output

Produce clean, well-commented code (Python or R) and summary tables. Provide an in-depth interpretation of the coefficients, specifically the DiD estimator, in the context of "Greenium" vs. "Greenwashing" as discussed in the literature review.
