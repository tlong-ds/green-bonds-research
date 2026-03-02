import json
import nbformat as nbf
import os

notebook_path = 'notebooks/data-processing.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

markdown_cell = nbf.v4.new_markdown_cell("""## Econometric Data Cleaning
Applying data cleaning techniques based on the Econometric Data Cleaning skill and the Evaluation Report fixes.

**Pipeline order (corrected):**
1. Load data & filter non-ASEAN firms / Year 2025
2. Handle missing values via forward fill (grouped by `ric`), then drop firms with <3 years of `total_assets`
3. Data type conversion (ensure numeric columns are numeric early)
4. Currency conversion to USD using `yfinance` (excludes ratios: ROA, ROE, emissions_intensity)
5. Winsorization at 1st/99th percentiles (AFTER currency conversion, in common currency)
6. Normalize ROA/ROE from percentage to decimal (divide by 100)
7. Log transform `total_assets`
8. Encode `environmental_investment` as binary (Y=1, N=0, NaN=NaN)
9. Data type verification & duplicate resolution
""")

code_cell = nbf.v4.new_code_cell("""import pandas as pd
import yfinance as yf
from scipy.stats.mstats import winsorize
import numpy as np

# Load data
df = pd.read_csv('../processed_data/final_data.csv')
print(f"Original shape: {df.shape}")

# ============================================================
# 0. Filter non-ASEAN firms and Year 2025
# (Issue #7, #8, #18: "Other" country includes Korean firms
#  in non-ASEAN exchanges; Year 2025 has almost all NaN financials)
# ============================================================
df = df[df['country'] != 'Other'].copy()
print(f"Shape after removing non-ASEAN ('Other') firms: {df.shape}")

df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
df = df[df['Year'] != 2025].copy()
print(f"Shape after removing Year 2025: {df.shape}")

# ============================================================
# 1. Handle Missing Values
# Forward fill slowly-changing variables, grouped by 'ric'.
# NOTE: environmental_investment is NOT forward-filled (Issue #19)
#   — it is a Y/N indicator, ffill would artificially inflate 'Y'.
# ============================================================
vars_to_ffill = [
    'total_assets', 'return_on_equity_total', 'return_on_assets',
    'emissions_intensity', 'esg_score', 'estimated_total_carbon_footprint',
    'internal_carbon_pricing', 'internal_carbon_price_per_tonne'
]
for col in vars_to_ffill:
    if col in df.columns:
        df[col] = df.groupby('ric')[col].transform(lambda x: x.ffill())

# Reduce data loss (Issue #15): keep firms with at least 3 years of
# non-null total_assets, then drop individual rows still missing it.
ta_notna_count = df.groupby('ric')['total_assets'].transform(
    lambda x: x.notna().sum()
)
df = df[ta_notna_count >= 3].copy()
df = df.dropna(subset=['total_assets']).copy()
print(f"Shape after ffill and filtering firms with <3 years of total_assets: {df.shape}")

# ============================================================
# 2. Early Data Type Conversion (Issue #9)
# Convert numeric columns from object to float BEFORE any math.
# ============================================================
numeric_cols = [
    'ask_price', 'bid_price', 'capital_expenditures', 'cash',
    'current_assets_total', 'current_liabilities_total',
    'earnings_bef_interest_tax', 'interest_expense_total',
    'long_term_debt', 'market_capitalization', 'market_value',
    'net_cash_flow_operating_actv', 'net_sales_or_revenues',
    'operating_income', 'total_assets', 'total_capital',
    'total_debt', 'total_liabilities',
    'return_on_assets', 'return_on_equity_total',
    'emissions_intensity', 'esg_score', 'estimated_total_carbon_footprint',
    'internal_carbon_pricing', 'internal_carbon_price_per_tonne',
    'employees', 'tri'
]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# ============================================================
# 3. Currency Conversion to USD (BEFORE winsorization)
# (Issue #16: winsorize AFTER conversion to common currency)
# (Issue #17: EXCLUDE ratios from FX conversion — ROA, ROE,
#  emissions_intensity are percentages/ratios, not currency values)
# ============================================================
currency_map = {
    'Vietnam': 'VND=X',
    'Thailand': 'THB=X',
    'Malaysia': 'MYR=X',
    'Singapore': 'SGD=X',
    'Indonesia': 'IDR=X',
    'Philippines': 'PHP=X'
}

fx_rates = {}
for country, ticker in currency_map.items():
    tk = yf.Ticker(ticker)
    hist = tk.history(period="max")
    if not hist.empty:
        hist['Year'] = hist.index.year
        yearly_avg = hist.groupby('Year')['Close'].mean()
        fx_rates[country] = yearly_avg.to_dict()

# Only MONETARY columns — explicitly exclude ratios/percentages
financial_cols_for_fx = [
    'ask_price', 'bid_price', 'capital_expenditures', 'cash',
    'current_assets_total', 'current_liabilities_total',
    'earnings_bef_interest_tax', 'interest_expense_total',
    'long_term_debt', 'market_capitalization', 'market_value',
    'net_cash_flow_operating_actv', 'net_sales_or_revenues',
    'operating_income', 'total_assets', 'total_capital',
    'total_debt', 'total_liabilities'
]
# NOTE: return_on_assets, return_on_equity_total, emissions_intensity,
#        esg_score, internal_carbon_pricing are NOT converted.

def get_fx_rate(row):
    country = row['country']
    year = row['Year']
    if country in fx_rates and year in fx_rates[country]:
        return fx_rates[country][year]
    return 1.0  # fallback (should not happen after filtering 'Other')

df['fx_rate'] = df.apply(get_fx_rate, axis=1)

for col in financial_cols_for_fx:
    if col in df.columns:
        df[col] = df[col] / df['fx_rate']

df.drop(columns=['fx_rate'], inplace=True)
print("Currency conversion to USD complete (ratios excluded).")

# ============================================================
# 4. Winsorization (AFTER currency conversion — Issue #16)
# Now all monetary values are in USD, so percentile trimming
# is statistically meaningful across countries.
# Also winsorize emissions_intensity (Issue #25).
# ============================================================
winsorize_vars = [
    'ask_price', 'bid_price', 'total_assets', 'net_sales_or_revenues',
    'cash', 'capital_expenditures', 'long_term_debt', 'total_debt',
    'market_capitalization', 'market_value', 'operating_income',
    'earnings_bef_interest_tax', 'current_assets_total',
    'current_liabilities_total', 'total_liabilities', 'total_capital',
    'emissions_intensity', 'estimated_total_carbon_footprint'
]
# Also winsorize ratios separately
ratio_winsorize_vars = ['return_on_assets', 'return_on_equity_total']

for col in winsorize_vars + ratio_winsorize_vars:
    if col in df.columns:
        mask = df[col].notna()
        if mask.sum() > 0:
            df.loc[mask, col] = winsorize(df.loc[mask, col], limits=[0.01, 0.01])

print("Winsorization complete (post-FX conversion).")

# ============================================================
# 5. Normalize ROA and ROE from percentage to decimal
# (User feedback: these are stored as percentages, divide by 100)
# ============================================================
for col in ['return_on_assets', 'return_on_equity_total']:
    if col in df.columns:
        df[col] = df[col] / 100.0

# ============================================================
# 6. Data Transformation & Normalization
# Log transform total_assets (standard in corporate finance)
# ============================================================
df['ln_total_assets'] = np.log(df['total_assets'].replace(0, np.nan))

# ============================================================
# 7. Encode environmental_investment properly (Issue #11)
# Map Y→1, N→0, keep NaN as NaN (not falsely coded as 0)
# ============================================================
if 'environmental_investment' in df.columns:
    df['environmental_investment'] = df['environmental_investment'].map({'Y': 1, 'N': 0})
    print(f"environmental_investment encoded: "
          f"1={int((df['environmental_investment']==1).sum())}, "
          f"0={int((df['environmental_investment']==0).sum())}, "
          f"NaN={int(df['environmental_investment'].isna().sum())}")

# ============================================================
# 8. Data Type Verification
# ============================================================
df['isin'] = df['isin'].astype(str)
df['ric'] = df['ric'].astype(str)
df['country'] = df['country'].astype(str)
df['company'] = df['company'].astype(str)
df['Year'] = df['Year'].astype(int)

# Treat GIC as categorical, not numeric (Issue #14)
if 'gic' in df.columns:
    df['gic'] = df['gic'].astype(str).astype('category')

# ============================================================
# 9. Duplicates Resolution
# ============================================================
df = df.sort_values(by=df.columns.tolist()).drop_duplicates(subset=['ric', 'Year'], keep='last')

print(f"\\nData Cleaning Complete. Final Shape: {df.shape}")
print(f"Countries: {df['country'].unique()}")
print(f"Year range: {df['Year'].min()} - {df['Year'].max()}")
print(f"Unique firms (RICs): {df['ric'].nunique()}")

# Save the cleaned dataset for the next step
df.to_csv('../processed_data/cleaned_panel_data.csv', index=False)
""")

nb['cells'].extend([markdown_cell, code_cell])

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f"Successfully added Econometric Data Cleaning cells to {notebook_path}")
