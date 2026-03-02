import pandas as pd
import yfinance as yf
from scipy.stats.mstats import winsorize
import numpy as np

# Load data
df = pd.read_csv('processed_data/final_data.csv')

print("Years present:", sorted(df['Year'].dropna().unique()))

# 1. Handle Missing Values
vars_to_ffill = ['total_assets', 'return_on_equity_total', 'emissions_intensity', 'environmental_investment']
for col in vars_to_ffill:
    if col in df.columns:
        df[col] = df.groupby('ric')[col].transform(lambda x: x.ffill())

df = df.dropna(subset=['total_assets']).copy()

# 2. Winsorization
winsorize_vars = ['ask_price', 'bid_price', 'total_assets', 'return_on_assets', 'return_on_equity_total', 'net_sales_or_revenues', 'cash']
for col in winsorize_vars:
    if col in df.columns:
        mask = df[col].notna()
        df.loc[mask, col] = winsorize(df.loc[mask, col], limits=[0.01, 0.01])

# 3. Currency Conversion using yfinance to USD
# Find unique years. Say 2010 to 2024.
years = sorted(df['Year'].dropna().unique())
currency_map = {
    'Vietnam': 'VND=X',
    'Thailand': 'THB=X',
    'Malaysia': 'MYR=X',
    'Singapore': 'SGD=X',
    'Indonesia': 'IDR=X',
    'Philippines': 'PHP=X'
}

print("Fetching FX data...")
fx_rates = {}
for country, ticker in currency_map.items():
    tk = yf.Ticker(ticker)
    hist = tk.history(period="max")
    if not hist.empty:
        # Group by year and take the mean exchange rate
        hist['Year'] = hist.index.year
        yearly_avg = hist.groupby('Year')['Close'].mean()
        # Varies by definition: 'VND=X' is USD/VND (how many VND for 1 USD).
        # To convert VND to USD, we divide by this rate.
        fx_rates[country] = yearly_avg.to_dict()

# Add a default rate (e.g., 1.0) for years not found or 'Other' country
financial_cols = [
    'ask_price', 'bid_price', 'capital_expenditures', 'cash', 
    'current_assets_total', 'current_liabilities_total', 'earnings_bef_interest_tax', 
    'interest_expense_total', 'long_term_debt', 'market_capitalization', 'market_value', 
    'net_cash_flow_operating_actv', 'net_sales_or_revenues', 'operating_income', 
    'total_assets', 'total_capital', 'total_debt', 'total_liabilities'
]
# Ensure we don't convert green bond proceeds or anything else.

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

print("Data Cleaning Complete. Shape:", df.shape)
