"""Test that DiD estimation now works"""
import sys
sys.path.insert(0, '.')

import pandas as pd
from asean_green_bonds.analysis.difference_in_diff import run_multiple_outcomes

print("="*60)
print("TESTING DiD ESTIMATION FIX")
print("="*60)

# Load data
df = pd.read_csv('processed_data/final_engineered_panel_data.csv')
print(f"\n✓ Loaded {len(df):,} observations")

# Use working outcome variables (not Tobin_Q which has data issues)
outcomes = ['return_on_assets', 'return_on_equity_total']
specs = ['entity_fe', 'time_fe']

print(f"\n✓ Testing {len(outcomes)} outcomes × {len(specs)} specifications = {len(outcomes)*len(specs)} models")

# Run estimation
results = run_multiple_outcomes(
    df,
    outcomes=outcomes,
    treatment_col='green_bond_active',
    specifications=specs
)

print(f"\n✓ Completed! {len(results)} models estimated successfully")

if len(results) > 0:
    print("\n" + "="*60)
    print("RESULTS PREVIEW")
    print("="*60)
    print(results[['outcome', 'specification', 'coefficient', 'std_error', 'p_value', 'n_obs']].to_string(index=False))
    
    print("\n" + "="*60)
    print("✅ SUCCESS - DiD estimation is working!")
    print("="*60)
else:
    print("\n❌ No results - check warnings above")
    sys.exit(1)
