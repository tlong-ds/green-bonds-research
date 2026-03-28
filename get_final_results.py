import pandas as pd
import numpy as np
from asean_green_bonds.data.processed_loader import load_processed_data
from asean_green_bonds.analysis.difference_in_diff import estimate_did
from asean_green_bonds.analysis.gmm import estimate_system_gmm
from asean_green_bonds import config

# Load data
df = load_processed_data()

outcomes = config.OUTCOME_VARIABLES
controls = config.CONTROL_VARIABLES

print("--- DID RESULTS (TWFE) ---")
for outcome in outcomes:
    try:
        res = estimate_did(df, outcome=outcome, treatment_col='green_bond_active', specification='twoway_fe')
        if 'error' not in res:
            print(f"\nOUTCOME: {outcome}")
            print(f"Coef: {res['coefficient']:.4f}")
            print(f"SE: {res['std_error']:.4f}")
            print(f"P-val: {res['p_value']:.4f}")
            print(f"N-obs: {res['n_obs']}")
            print(f"Absorbed: {res['absorbed_vars']}")
    except:
        pass

print("\n--- GMM RESULTS (FULL) ---")
for outcome in outcomes:
    try:
        res = estimate_system_gmm(df, outcome=outcome, treatment_col='green_bond_active')
        if 'error' in res:
            print(f"\nGMM ERROR for {outcome}: {res['error']}")
        else:
            print(f"\nOUTCOME: {outcome}")
            print(f"Coef: {res['coefficient']:.4f}")
            print(f"SE: {res['std_error']:.4f}")
            print(f"P-val: {res['p_value']:.4f}")
            print(f"N-obs: {res['n_obs']}")
    except Exception as e:
        print(f"Error {outcome}: {e}")
        import traceback
        traceback.print_exc()
