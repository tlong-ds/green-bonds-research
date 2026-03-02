import json
import nbformat as nbf

notebook_path = 'notebooks/data-processing.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

markdown_cell = nbf.v4.new_markdown_cell("""## Panel Data Validation
Structurally validating the firm-year panel dataset.

Tasks include:
- Setting the multi-index (`['ric', 'Year']`).
- Checking if the panel is severely unbalanced.
- Generating descriptive statistics (Table 1) including engineered variables.
- Producing a correlation matrix.
- Before/after diagnostics for key variables.
""")

code_cell = nbf.v4.new_code_cell("""import pandas as pd
import numpy as np

# Load the cleaned dataset
df = pd.read_csv('../processed_data/cleaned_panel_data.csv')

# ============================================================
# 1. Set Multi-Index
# ============================================================
panel = df.set_index(['ric', 'Year']).sort_index()

# ============================================================
# 2. Panel Structure Check
# ============================================================
obs_per_firm = panel.groupby(level='ric').size()
print("=" * 60)
print("PANEL STRUCTURE CHECK")
print("=" * 60)
print(f"Total Firms (RICs): {panel.index.get_level_values('ric').nunique()}")
print(f"Total Firm-Year Observations: {len(panel)}")
print(f"Average Years per Firm: {obs_per_firm.mean():.2f}")
print(f"Temporal Range: {panel.index.get_level_values('Year').min()} to {panel.index.get_level_values('Year').max()}")
print(f"Min Years for a single firm: {obs_per_firm.min()}")
print(f"Max Years for a single firm: {obs_per_firm.max()}")

# Verify no non-ASEAN countries
if 'country' in df.columns:
    print(f"\\nCountries in dataset: {sorted(df['country'].unique())}")

# ============================================================
# 3. Descriptive Statistics (Table 1)
# ============================================================
primary_vars = [
    'total_assets', 'ln_total_assets', 'total_debt',
    'return_on_assets', 'return_on_equity_total',
    'emissions_intensity', 'esg_score',
    'estimated_total_carbon_footprint',
    'net_sales_or_revenues', 'market_capitalization',
    'capital_expenditures'
]

# Filter to only existing columns
primary_vars = [c for c in primary_vars if c in df.columns]

# Ensure primary variables are numeric
for col in primary_vars:
    df[col] = pd.to_numeric(df[col], errors='coerce')

desc_stats = df[primary_vars].describe().T
desc_stats['skewness'] = df[primary_vars].skew()
desc_stats['kurtosis'] = df[primary_vars].kurt()
desc_stats['missing_pct'] = (df[primary_vars].isna().sum() / len(df) * 100).round(1)

print("\\n" + "=" * 60)
print("DESCRIPTIVE STATISTICS")
print("=" * 60)
display(desc_stats)

# ============================================================
# 4. Sanity Checks on Key Variables
# ============================================================
print("\\n" + "=" * 60)
print("SANITY CHECKS")
print("=" * 60)

# ROA/ROE should be in decimal range (after /100)
if 'return_on_assets' in df.columns:
    roa = df['return_on_assets'].dropna()
    print(f"ROA range: [{roa.min():.4f}, {roa.max():.4f}] (should be decimal, e.g. 0.05 = 5%)")

if 'return_on_equity_total' in df.columns:
    roe = df['return_on_equity_total'].dropna()
    print(f"ROE range: [{roe.min():.4f}, {roe.max():.4f}]")

# Check environmental_investment encoding
if 'environmental_investment' in df.columns:
    print(f"\\nenvironmental_investment value counts (NaN should exist, not be 0):")
    print(df['environmental_investment'].value_counts(dropna=False))

# Check for any remaining non-ASEAN
if 'country' in df.columns:
    non_asean = df[df['country'] == 'Other']
    print(f"\\nNon-ASEAN ('Other') rows remaining: {len(non_asean)} (should be 0)")

# ============================================================
# 5. Correlation Matrix
# ============================================================
corr_vars = [c for c in primary_vars if c in df.columns and df[c].notna().sum() > 100]
corr_matrix = df[corr_vars].corr(method='pearson')
print("\\n" + "=" * 60)
print("PEARSON CORRELATION MATRIX")
print("=" * 60)
display(corr_matrix)

# Flag high multicollinearity
print("\\nHigh correlations (|r| > 0.8):")
for i in range(len(corr_matrix)):
    for j in range(i+1, len(corr_matrix)):
        r = corr_matrix.iloc[i, j]
        if abs(r) > 0.8:
            print(f"  {corr_matrix.index[i]} ↔ {corr_matrix.columns[j]}: {r:.3f}")
""")

nb['cells'].extend([markdown_cell, code_cell])

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f"Successfully added Panel Data Validation cells to {notebook_path}")
