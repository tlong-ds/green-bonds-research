---
name: Feature Selection
description: Selection of key financial and ESG variables for the ASEAN Green Bonds research.
---

# Feature Selection (ASEAN Green Bonds)

You are acting as a Data Science Specialist. Select and validate the features required for the econometric models assessing the impact of green bonds on performance.

## Tasks

1. **Required Control Variables**:
   - Ensure the following covariates (X_it) are present:
     - **Firm Size**: `Ln(Total Assets)`
     - **Leverage**: `Long-term Debt / Total Assets`
     - **Asset Turnover**: `Total Sales / Total Assets`
     - **Liquidity**: `Current Assets / Current Liabilities`
     - **ESG Score**: Composite rating from agencies (e.g., Refinitiv).
2. **Multicollinearity Diagnostic**:
   - Compute **VIF** for all regressors. Ensure VIF < 10 (ideally < 5).
   - Analyze the Pearson correlation matrix. Investigate any pairs with |r| > 0.7.
3. **Lagged Controls**:
   - Apply 1-year lags to control variables where appropriate to mitigate simultaneity bias, as per the research outline's emphasis on causal isolation.
4. **Variable Justification**:
   - Document the rationale for including each feature based on corporate finance theory (e.g., Signaling Theory for Firm Size).

## Output

Generate a finalized list of variables and a correlation heatmap. Provide a markdown summary explaining how the selected features isolate the "true" effect of green bond issuance from other firm-specific shocks.
