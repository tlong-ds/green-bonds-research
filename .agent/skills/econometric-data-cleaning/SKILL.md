---
name: Econometric Data Cleaning
description: Skill for performing necessary data cleaning for econometric panel data analysis.
---

# Econometric Data Cleaning

You are acting as a Data Science Specialist for an econometrics research project on "Impacts of Green Bond Issuance on Corporate Environmental and Financial Performance in ASEAN Listed Companies". The dataset has already been merged and type-converted. Your goal is to apply robust data cleaning techniques.

## Tasks

1. **Handle Missing Values**: For key financial variables (e.g., total_assets, return_on_equity_total) and ESG variables (emissions_intensity, environmental_investment), determine the appropriate missing value strategy. Do not simply drop all NaNs if they cause significant bias; use forward fill or appropriate imputation where logically sound, otherwise safely drop.
2. **Winsorization / Outlier Treatment**: Economic and financial variables are highly prone to outliers. Winsorize continuous variables (like ask_price, bid_price, total_assets, ROA, ROE, revenue, cash) at the 1st and 99th percentiles to avoid extreme outliers affecting regression models.
3. **Currency Conversion**: Financial values in `panel_data.csv` are in varying local currencies. To maintain consistency with `greenbonds.csv` (which is in USD), convert financial terms (like pricing, total assets, capital expenditures, etc.) to USD using the appropriate average annual or point-in-time exchange rate for each respective ASEAN country and year.
4. **Data Transformation & Normalization**: To prevent large numerical magnitudes (e.g., total assets) from dragging estimated coefficients toward zero (rendering them uninterpretable), normalize or standardize variables. Common practices include transforming heavily skewed variables (like firm size or revenue) using natural log transformation (`ln(X)`) or standard scaling (zero mean, unit variance).
5. **Data Type Verification**: Ensure that identifiers (e.g., `isin`, `ric`, `country`, `company`) are correctly treated as strings/categories, and temporal variables (`Year`) are integers or datetime objects.
6. **Duplicates Resolution**: Check for overlapping firm-year observations and drop duplicates, preserving the records with the most non-null columns.

## Output

Update `data-processing.ipynb` with new cells performing these tasks, ensuring all data operations use `pandas` efficiently. Include comments explaining why the chosen strategies are statistically rigorous for corporate finance datasets.
