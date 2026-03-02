import json
import nbformat as nbf

notebook_path = 'notebooks/data-processing.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

markdown_cell = nbf.v4.new_markdown_cell("""## Variable Engineering
Calculations of intermediate financial and environmental variables for regression models.

Tasks include:
- Calculating Control Variables: Firm Size, Leverage, Profitability, Capital Intensity.
- Green Bond & ESG Processing: Log-transforming severely skewed `emissions_intensity`.
- Lagged Variables: Computing 1-year lagged values for independent variables grouped by firm.
- Creating Country and Year dummy variables for fixed effects.

**Evaluation Report fixes applied:**
- `Firm_Size` is a proper `.copy()` (Issue #26)
- `Leverage` and `Capital_Intensity` clipped to [0, 1] (Issues #24, #27)
- `gic` treated as categorical (Issue #14)
- `pd.get_dummies` no longer applied on `environmental_investment` (already binary from cleaning)
""")

code_cell = nbf.v4.new_code_cell("""import pandas as pd
import numpy as np

# Load cleaned data (environmental_investment already encoded as 1/0/NaN)
df = pd.read_csv('../processed_data/cleaned_panel_data.csv')
print(f"Loaded cleaned data: {df.shape}")

# ============================================================
# 1. Calculate Control Variables
# ============================================================
# Firm_Size: proper copy, not a reference (Issue #26)
df['Firm_Size'] = df['ln_total_assets'].copy()

# Leverage: clip to [0, 1] — values > 1 indicate total_debt > total_assets,
# which is possible for distressed firms but likely data error at extreme values (Issue #24)
df['Leverage'] = (df['total_debt'] / df['total_assets']).clip(lower=0, upper=1)

# Capital_Intensity: cap at [0, 1] — CapEx/Assets > 1 is almost certainly
# a data error (Issue #27)
df['Capital_Intensity'] = (df['capital_expenditures'].abs() / df['total_assets']).clip(lower=0, upper=1)

print("Control variables calculated:")
print(df[['Firm_Size', 'Leverage', 'Capital_Intensity']].describe())

# ============================================================
# 2. Green Bond & ESG Processing
# ============================================================
# Log-transform emissions_intensity (extreme skewness = 33.5, Issue #25)
# Already winsorized in cleaning step; log calms remaining skewness
if 'emissions_intensity' in df.columns:
    df['ln_emissions_intensity'] = np.log(df['emissions_intensity'].replace(0, np.nan))

# Log-transform estimated_total_carbon_footprint if present
if 'estimated_total_carbon_footprint' in df.columns:
    df['ln_carbon_footprint'] = np.log(
        df['estimated_total_carbon_footprint'].replace(0, np.nan)
    )

# ============================================================
# 3. Lagged Variables (1-year lag grouped by firm)
# ============================================================
independent_vars = [
    'Firm_Size', 'Leverage', 'Capital_Intensity',
    'return_on_assets', 'return_on_equity_total',
    'ln_emissions_intensity', 'environmental_investment',
    'esg_score'
]

for col in independent_vars:
    if col in df.columns:
        df[f'L1_{col}'] = df.groupby('ric')[col].shift(1)

print(f"\\nLagged variables created for: {[c for c in independent_vars if c in df.columns]}")

# ============================================================
# 4. GIC as categorical (Issue #14)
# ============================================================
if 'gic' in df.columns:
    df['gic'] = df['gic'].astype(str).astype('category')
    print(f"GIC categories: {df['gic'].nunique()} unique industry codes")

# ============================================================
# 5. Country and Year Dummies (Fixed Effects Preparation)
# Note: 'Other' country already filtered in cleaning. Year 2025 removed.
# environmental_investment is already 1/0/NaN — no get_dummies needed for it.
# ============================================================
df = pd.get_dummies(df, columns=['country', 'Year'], drop_first=True, dtype=int)

# ============================================================
# Final Dataset Cleanup and Saving
# ============================================================
df.to_csv('../processed_data/final_engineered_panel_data.csv', index=False)
print(f"\\nVariable Engineering Complete. Final shape: {df.shape}")
print("\\nSummary of key engineered variables:")
summary_cols = ['Firm_Size', 'Leverage', 'Capital_Intensity', 'ln_emissions_intensity']
summary_cols = [c for c in summary_cols if c in df.columns]
print(df[summary_cols].describe())
""")

nb['cells'].extend([markdown_cell, code_cell])

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f"Successfully added Variable Engineering cells to {notebook_path}")
