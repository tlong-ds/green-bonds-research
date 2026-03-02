"""
Test script for data cleaning pipeline.
Mirrors the logic from add_cleaning_cells.py for quick standalone testing.
Run: python test_data_cleaning.py
"""
import pandas as pd
import yfinance as yf
from scipy.stats.mstats import winsorize
import numpy as np

# Load data
df = pd.read_csv('processed_data/final_data.csv')
print(f"Original shape: {df.shape}")

# 0. Filter non-ASEAN and Year 2025
df = df[df['country'] != 'Other'].copy()
print(f"After removing 'Other': {df.shape}")

df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
df = df[df['Year'] != 2025].copy()
print(f"After removing 2025: {df.shape}")

# 1. Forward fill (no environmental_investment)
vars_to_ffill = [
    'total_assets', 'return_on_equity_total', 'return_on_assets',
    'emissions_intensity', 'esg_score', 'estimated_total_carbon_footprint',
    'internal_carbon_pricing', 'internal_carbon_price_per_tonne'
]
for col in vars_to_ffill:
    if col in df.columns:
        df[col] = df.groupby('ric')[col].transform(lambda x: x.ffill())

# Reduce data loss: firms with >= 3 years of total_assets
ta_notna_count = df.groupby('ric')['total_assets'].transform(lambda x: x.notna().sum())
df = df[ta_notna_count >= 3].copy()
df = df.dropna(subset=['total_assets']).copy()
print(f"After ffill + 3yr filter: {df.shape}")

# 2. Early type conversion
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

# 3. Currency conversion (BEFORE winsorization)
currency_map = {
    'Vietnam': 'VND=X', 'Thailand': 'THB=X', 'Malaysia': 'MYR=X',
    'Singapore': 'SGD=X', 'Indonesia': 'IDR=X', 'Philippines': 'PHP=X'
}

print("Fetching FX data...")
fx_rates = {}
for country, ticker in currency_map.items():
    tk = yf.Ticker(ticker)
    hist = tk.history(period="max")
    if not hist.empty:
        hist['Year'] = hist.index.year
        yearly_avg = hist.groupby('Year')['Close'].mean()
        fx_rates[country] = yearly_avg.to_dict()

# Only monetary columns — exclude ratios
financial_cols_for_fx = [
    'ask_price', 'bid_price', 'capital_expenditures', 'cash',
    'current_assets_total', 'current_liabilities_total',
    'earnings_bef_interest_tax', 'interest_expense_total',
    'long_term_debt', 'market_capitalization', 'market_value',
    'net_cash_flow_operating_actv', 'net_sales_or_revenues',
    'operating_income', 'total_assets', 'total_capital',
    'total_debt', 'total_liabilities'
]

def get_fx_rate(row):
    country = row['country']
    year = row['Year']
    if country in fx_rates and year in fx_rates[country]:
        return fx_rates[country][year]
    return 1.0

df['fx_rate'] = df.apply(get_fx_rate, axis=1)
for col in financial_cols_for_fx:
    if col in df.columns:
        df[col] = df[col] / df['fx_rate']
df.drop(columns=['fx_rate'], inplace=True)
print("FX conversion done (ratios excluded).")

# 4. Winsorization (AFTER FX conversion)
winsorize_vars = [
    'ask_price', 'bid_price', 'total_assets', 'net_sales_or_revenues',
    'cash', 'capital_expenditures', 'long_term_debt', 'total_debt',
    'market_capitalization', 'market_value', 'operating_income',
    'earnings_bef_interest_tax', 'current_assets_total',
    'current_liabilities_total', 'total_liabilities', 'total_capital',
    'emissions_intensity', 'estimated_total_carbon_footprint'
]
ratio_winsorize_vars = ['return_on_assets', 'return_on_equity_total']

for col in winsorize_vars + ratio_winsorize_vars:
    if col in df.columns:
        mask = df[col].notna()
        if mask.sum() > 0:
            df.loc[mask, col] = winsorize(df.loc[mask, col], limits=[0.01, 0.01])
print("Winsorization done (post-FX).")

# 5. ROA/ROE percentage to decimal
for col in ['return_on_assets', 'return_on_equity_total']:
    if col in df.columns:
        df[col] = df[col] / 100.0

# 6. Log transform
df['ln_total_assets'] = np.log(df['total_assets'].replace(0, np.nan))

# 7. Environmental investment encoding
if 'environmental_investment' in df.columns:
    df['environmental_investment'] = df['environmental_investment'].map({'Y': 1, 'N': 0})
    print(f"env_invest: 1={int((df['environmental_investment']==1).sum())}, "
          f"0={int((df['environmental_investment']==0).sum())}, "
          f"NaN={int(df['environmental_investment'].isna().sum())}")

# 8. Types
df['isin'] = df['isin'].astype(str)
df['ric'] = df['ric'].astype(str)
df['country'] = df['country'].astype(str)
df['company'] = df['company'].astype(str)
df['Year'] = df['Year'].astype(int)
if 'gic' in df.columns:
    df['gic'] = df['gic'].astype(str).astype('category')

# 9. Dedup
df = df.sort_values(by=df.columns.tolist()).drop_duplicates(subset=['ric', 'Year'], keep='last')

print(f"\nData Cleaning Complete. Shape: {df.shape}")
print(f"Countries: {df['country'].unique()}")
print(f"Year range: {df['Year'].min()} - {df['Year'].max()}")

# Quick sanity
if 'return_on_assets' in df.columns:
    roa = df['return_on_assets'].dropna()
    print(f"ROA range: [{roa.min():.4f}, {roa.max():.4f}] (decimal)")
