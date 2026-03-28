import pandas as pd
import numpy as np
from asean_green_bonds.data.processed_loader import load_processed_data
from asean_green_bonds.analysis.difference_in_diff import prepare_panel_for_regression
from asean_green_bonds import config

# Load data
df = load_processed_data()
entity_col = 'org_permid'
time_col = 'Year'

outcomes = config.OUTCOME_VARIABLES
controls = config.CONTROL_VARIABLES

for outcome in outcomes:
    print(f"\n--- COLLINEARITY DIAGNOSTICS: {outcome} ---")
    
    # Simple check for DiD (TWFE) setup
    df_reg = prepare_panel_for_regression(df, entity_col, time_col, set_index=True)
    
    # Prepare regressors
    treatment_col = 'green_bond_active'
    regressors = [treatment_col] + controls
    regressors = [r for r in regressors if r in df_reg.columns]
    
    # Check data for this outcome
    data = df_reg[[outcome] + regressors].dropna()
    if len(data) < 30:
        print(f"Skipping {outcome}: insufficient data ({len(data)})")
        continue
        
    print(f"Observations: {len(data)}")
    
    # Correlation with treatment
    corr = data.corr()
    print("\nCorrelation with treatment:")
    print(corr[treatment_col].sort_values(ascending=False))
    
    # Check for near-perfect collinearity
    upper = corr.abs().where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    high_corr = []
    for col in upper.columns:
        for idx in upper.index:
            if upper.loc[idx, col] > 0.9:
                high_corr.append((idx, col, upper.loc[idx, col]))
    
    if high_corr:
        print("\nHigh Correlations (>0.9):")
        for c1, c2, val in high_corr:
            print(f"  {c1} <-> {c2}: {val:.4f}")
    else:
        print("\nNo correlations > 0.9 found.")

    # Check variation within treatment=1
    treated_data = data[data[treatment_col] > 0]
    print(f"\nVariation in controls for treated units (N={len(treated_data)}):")
    for ctrl in controls:
        if ctrl in treated_data.columns:
            std = treated_data[ctrl].std()
            print(f"  {ctrl}: std={std:.4f}")
