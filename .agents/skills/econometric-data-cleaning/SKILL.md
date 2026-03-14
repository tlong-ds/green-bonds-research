---
name: Econometric Data Cleaning
description: Skill for performing necessary data cleaning for the ASEAN Green Bonds research (2015-2025).
---

# Econometric Data Cleaning (ASEAN Green Bonds)

You are acting as a Data Science Specialist for the research project "The Impact of Green Bond Issuance on Corporate Financial Performance in ASEAN Listed Companies (2015-2025)". Your goal is to apply robust data cleaning techniques tailored for this specific panel dataset.

## Tasks

1. **Handle Missing Values**: 
   - For key financial variables (`ROA`, `Tobin's Q`, `Total Assets`, `Leverage`) and ESG variables (`ESG Score`, `GHG Emissions`), determine the appropriate strategy.
   - Use forward fill or interpolation for missing values where logically sound (e.g., total assets).
   - For ESG metrics, acknowledge sparsity in ASEAN markets and document the impact on sample size.
2. **Winsorization / Outlier Treatment**: 
   - Financial variables are prone to extreme values. Winsorize continuous variables (ROA, Tobin's Q, Leverage, Asset Turnover, Liquidity) at the **1st and 99th percentiles** as per standard corporate finance research practices.
3. **Currency Conversion**: 
   - Convert all financial values from local ASEAN currencies (IDR, MYR, PHP, SGD, THB, VND) to **USD** to ensure consistency. Use annual average exchange rates for the respective years (2015-2025).
4. **Data Transformation**: 
   - Transform skewed variables like `Total Assets` into `Firm Size (Ln Assets)` using the natural logarithm.
   - Ensure `ROA` is represented as a percentage.
5. **Data Type Verification**: 
   - Ensure IDs (`RIC`, `ISIN`, `Company Name`) are strings.
   - Ensure `Year` is an integer.
   - Ensure `Green_Bond_Active` (treatment dummy) is an integer (0 or 1).
6. **Duplicates Resolution**: 
   - Identify and resolve any overlapping firm-year observations, ensuring unique entries for each firm (RIC) per year.

## Output

Update the data processing pipeline with these refined steps. Include detailed comments justifying the choice of winsorization levels and currency conversion sources, specifically highlighting the relevance to the ASEAN market context.
