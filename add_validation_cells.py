import json
import nbformat as nbf

notebook_path = 'notebooks/data-processing.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

markdown_cell = nbf.v4.new_markdown_cell("""## Panel Data Validation
Structurally validating the firm-year panel dataset based on the Panel Data Validation skill.
Tasks include:
- Setting the multi-index (`['ric', 'Year']`).
- Checking if the panel is severely unbalanced.
- Generating descriptive statistics (Table 1).
- Producing a correlation matrix.
""")

code_cell = nbf.v4.new_code_cell("""import pandas as pd
import numpy as np

# Load the cleaned dataset
df = pd.read_csv('../processed_data/cleaned_panel_data.csv')

# 1. Set Multi-Index
panel = df.set_index(['ric', 'Year']).sort_index()

# 2. Check Unbalanced Panel
obs_per_firm = panel.groupby(level='ric').size()
print("Panel Structure Check:")
print(f"Total Firms (RICs): {panel.index.get_level_values('ric').nunique()}")
print(f"Total Firm-Year Observations: {len(panel)}")
print(f"Average Years per Firm: {obs_per_firm.mean():.2f}")
print(f"Temporal Range: {panel.index.get_level_values('Year').min()} to {panel.index.get_level_values('Year').max()}")
print(f"Minimum Years for a single firm: {obs_per_firm.min()}")
print(f"Maximum Years for a single firm: {obs_per_firm.max()}")

# 3. Descriptive Statistics (Table 1)
primary_vars = [
    'total_assets', 'ln_total_assets', 'total_debt', 'return_on_assets', 
    'return_on_equity_total', 'emissions_intensity', 'environmental_investment'
]

# Ensure primary variables are numeric
for col in primary_vars:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

desc_stats = df[primary_vars].describe().T
desc_stats['skewness'] = df[primary_vars].skew()
desc_stats['kurtosis'] = df[primary_vars].kurt()
print("\\nDescriptive Statistics:")
display(desc_stats)

# 4. Correlation Matrix
corr_matrix = df[primary_vars].corr(method='pearson')
print("\\nPearson Correlation Matrix:")
display(corr_matrix)
""")

nb['cells'].extend([markdown_cell, code_cell])

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f"Successfully added Panel Data Validation cells to {notebook_path}")
