import json
import nbformat as nbf

notebook_path = 'notebooks/data-processing.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

markdown_cell = nbf.v4.new_markdown_cell("""## Variable Engineering
Calculations of intermediate financial and environmental variables for regression models based on the Variable Engineering skill.
Tasks include:
- Calculating Control Variables: Firm Size, Leverage, Profitability, Capital Intensity.
- Green Bond & ESG Processing: Logging severely skewed variables like `emissions_intensity`.
- Lagged Variables: Computing 1-year lagged values for independent variables grouped by firm.
- Creating Country and Year dummy variables for fixed effects.
""")

code_cell = nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# 1. Calculate Control Variables
df['Firm_Size'] = df['ln_total_assets']
df['Leverage'] = df['total_debt'] / df['total_assets']
df['Capital_Intensity'] = df['capital_expenditures'] / df['total_assets']

# 2. Green Bond & ESG Processing
# Assuming emissions_intensity is highly right-skewed and needs log transformation
# Replace 0 with NaN or a small number before log if appropriate
df['ln_emissions_intensity'] = np.log(df['emissions_intensity'].replace(0, np.nan))

# 3. Lagged Variables
# List of independent variables to create 1-year lags for
independent_vars = ['Firm_Size', 'Leverage', 'Capital_Intensity', 'return_on_assets', 
                    'return_on_equity_total', 'ln_emissions_intensity', 'environmental_investment']

for col in independent_vars:
    if col in df.columns:
        df[f'L1_{col}'] = df.groupby('ric')[col].shift(1)

# 4. Country and Year Dummies (Fixed Effects Preparation)
df = pd.get_dummies(df, columns=['country', 'Year'], drop_first=True)

# Final Dataset Cleanup and Saving
df.to_csv('../processed_data/final_engineered_panel_data.csv', index=False)
print("Variable Engineering Complete. Engineered dataset saved.")
print("Summary of newly created variables:")
print(df[['Firm_Size', 'Leverage', 'Capital_Intensity', 'ln_emissions_intensity']].describe())
""")

nb['cells'].extend([markdown_cell, code_cell])

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f"Successfully added Variable Engineering cells to {notebook_path}")
