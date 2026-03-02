---
name: Variable Engineering
description: Skill for calculating intermediate financial and environmental variables for regression models.
---

# Variable Engineering

You are acting as a Data Science Specialist. Build upon the cleaned dataset for the "Impacts of Green Bond Issuance..." project by calculating new variables required for the main econometric models.

## Tasks
1. **Calculate Control Variables**: 
   - **Firm Size**: `log(total_assets)`
   - **Leverage**: `total_debt / total_assets`
   - **Profitability Measures**: Standardize or verify `return_on_assets` and `return_on_equity_total`. Calculate derived variables if directly available fields are null.
   - **Capital Intensity**: `capital_expenditures / total_assets`
2. **Green Bond & ESG Processing**: Since assessing the impact of green bonds is central, ensure that ESG metrics or intensity variables (e.g., `emissions_intensity`) are correctly logged if they are severely right-skewed.
3. **Lagged Variables**: Environmental performance impacts often take a year to manifest financially. Compute 1-year lagged variables for independent variables using pandas `groupby('isin')['variable'].shift(1)`.
4. **Country and Year Dummies**: Note or verify that `country` and `Year` variables are properly formatted so they can be easily converted to dummy variables (fixed effects) during regression.

## Output
Add appropriate code cells to `data-processing.ipynb` to engineer these features. Ensure that operations group by firm identifier correctly so that data does not bleed across different companies.
