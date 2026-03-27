import pandas as pd
import numpy as np
import os

def check_data():
    path = "processed_data/full_panel_data.csv"
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    df = pd.read_csv(path)
    print(f"Loaded {path}, shape: {df.shape}")
    
    hetero_var = 'share_certified_proceeds'
    treatment_col = 'green_bond_active'
    
    if hetero_var not in df.columns:
        print(f"Column {hetero_var} not found")
        return
    
    # Replication of the binning logic
    n_bins = 2
    non_na = df[hetero_var].dropna()
    print(f"Non-NA {hetero_var} count: {len(non_na)}")
    print(f"Unique values in {hetero_var}: {non_na.nunique()}")
    print(f"Value counts for {hetero_var}:\n{non_na.value_counts()}")

    df_binned = df.copy()
    group_var = f'{hetero_var}_bin'
    df_binned[group_var] = pd.qcut(
        df_binned[hetero_var],
        q=n_bins,
        labels=False,
        duplicates='drop',
    )
    
    print(f"\nCreated bins for {group_var}:")
    print(df_binned[group_var].value_counts(dropna=False))
    
    for group_val in df_binned[group_var].unique():
        if pd.isna(group_val):
            continue
        
        df_group = df_binned[df_binned[group_var] == group_val]
        n_obs = len(df_group)
        n_treated = df_group[treatment_col].sum()
        n_unique_treatment = df_group[treatment_col].nunique()
        
        print(f"\nGroup {group_val}:")
        print(f"  Observations: {n_obs}")
        print(f"  Treated observations (sum of {treatment_col}): {n_treated}")
        print(f"  Unique values in {treatment_col}: {n_unique_treatment}")
        
        if n_unique_treatment < 2:
            print(f"  !!! NO VARIATION in {treatment_col} for group {group_val}")

if __name__ == "__main__":
    check_data()
