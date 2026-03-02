import json
import nbformat as nbf
import os

notebook_path = 'notebooks/data-processing.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

markdown_cell = nbf.v4.new_markdown_cell("""## Econometric Data Cleaning
Applying data cleaning techniques based on the Econometric Data Cleaning skill.
Tasks include:
- Handling missing values using forward fill by `ric`, then dropping rows still missing `total_assets`.
- Winsorizing continuous variables at the 1st and 99th percentiles.
- Currency conversion to USD using `yfinance`.
- Creating `ln_total_assets` transformation.
- Drop duplicate exact firm-year records.

*Note on Missing Data count:* `df.dropna(subset=['total_assets'])` drops rows where `total_assets` is missing. This drops about 29k rows because many companies lack `total_assets` data even after forward filling on their `ric`.""")

code_cell = nbf.v4.new_code_cell("""import pandas as pd
import yfinance as yf
from scipy.stats.mstats import winsorize
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Load data
df = pd.read_csv('../processed_data/final_data.csv')
print(f"Original shape: {df.shape}")

# 1. Handle Missing Values
# Forward fill dynamically logically sound variables, grouped by 'ric' (Reuters Instrument Code)
vars_to_ffill = ['total_assets', 'return_on_equity_total', 'emissions_intensity', 'environmental_investment']
for col in vars_to_ffill:
    if col in df.columns:
        df[col] = df.groupby('ric')[col].transform(lambda x: x.ffill())

# Drop rows missing fundamental financial variables that cannot be safely imputed.
df = df.dropna(subset=['total_assets']).copy()
print(f"Shape after ffill and dropping NaN total_assets: {df.shape}")

# 2. Winsorization
winsorize_vars = ['ask_price', 'bid_price', 'total_assets', 'return_on_assets', 'return_on_equity_total', 'net_sales_or_revenues', 'cash']
for col in winsorize_vars:
    if col in df.columns:
        mask = df[col].notna()
        df.loc[mask, col] = winsorize(df.loc[mask, col], limits=[0.01, 0.01])

# 3. Currency Conversion using yfinance to USD
years = sorted(df['Year'].dropna().unique())
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

financial_cols = [
    'ask_price', 'bid_price', 'capital_expenditures', 'cash', 
    'current_assets_total', 'current_liabilities_total', 'earnings_bef_interest_tax', 
    'interest_expense_total', 'long_term_debt', 'market_capitalization', 'market_value', 
    'net_cash_flow_operating_actv', 'net_sales_or_revenues', 'operating_income', 
    'total_assets', 'total_capital', 'total_debt', 'total_liabilities'
]

def get_fx_rate(row):
    country = row['country']
    year = row['Year']
    if country in fx_rates and year in fx_rates[country]:
        return fx_rates[country][year]
    return 1.0 # fallback

df['fx_rate'] = df.apply(get_fx_rate, axis=1)

for col in financial_cols:
    if col in df.columns:
        df[col] = df[col] / df['fx_rate']

df.drop(columns=['fx_rate'], inplace=True)

# 4. Data Transformation & Normalization
# Log transform total_assets
df['ln_total_assets'] = np.log(df['total_assets'].replace(0, np.nan))

# 5. Data Type Verification
df['isin'] = df['isin'].astype(str)
df['ric'] = df['ric'].astype(str)
df['country'] = df['country'].astype(str)
df['company'] = df['company'].astype(str)
df['Year'] = df['Year'].astype(int)

# 6. Duplicates Resolution
df = df.sort_values(by=df.columns.tolist()).drop_duplicates(subset=['ric', 'Year'], keep='last')

print("Data Cleaning Complete. Final Shape:", df.shape)

# Save the cleaned dataset for the next step 
df.to_csv('../processed_data/cleaned_panel_data.csv', index=False)
""")

nb['cells'].extend([markdown_cell, code_cell])

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f"Successfully added Econometric Data Cleaning cells to {notebook_path}")
