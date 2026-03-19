"""
Test script to verify DiD estimation fix for multicollinearity issue.
"""
import pandas as pd
import numpy as np
from asean_green_bonds.analysis.difference_in_diff import estimate_did, run_multiple_outcomes

# Load data
print("Loading data...")
df = pd.read_csv('processed_data/final_engineered_panel_data.csv')
print(f"✓ Loaded {len(df)} observations")

# Check for required columns
required_cols = ['ric', 'Year', 'green_bond_active', 'return_on_assets', 
                 'L1_Firm_Size', 'L1_Leverage']
missing = [c for c in required_cols if c not in df.columns]
if missing:
    print(f"✗ Missing columns: {missing}")
    print(f"Available columns: {df.columns.tolist()[:20]}...")
    exit(1)

print(f"✓ All required columns present")

# Test single specification
print("\n" + "="*60)
print("Testing single DiD estimation (entity FE)...")
print("="*60)

result = estimate_did(
    df,
    outcome='return_on_assets',
    treatment_col='green_bond_active',
    specification='entity_fe'
)

if 'error' in result:
    print(f"✗ Error: {result['error']}")
else:
    print(f"✓ Estimation successful!")
    print(f"  Coefficient: {result['coefficient']:.6f}")
    print(f"  Std Error: {result['std_error']:.6f}")
    print(f"  T-statistic: {result['t_statistic']:.3f}")
    print(f"  P-value: {result['p_value']:.4f}")
    print(f"  N observations: {result['n_obs']}")
    print(f"  N entities: {result['n_entities']}")
    print(f"  Significant at 5%: {result['significant_5pct']}")

# Test multiple outcomes and specifications
print("\n" + "="*60)
print("Testing multiple outcomes × specifications...")
print("="*60)

outcomes = ['return_on_assets', 'Tobin_Q', 'esg_score']
specs = ['entity_fe', 'time_fe', 'twoway_fe', 'none']

results_df = run_multiple_outcomes(
    df,
    outcomes=outcomes,
    treatment_col='green_bond_active',
    specifications=specs
)

print(f"\n✓ Estimated {len(results_df)} models successfully")
print(f"\nExpected: {len(outcomes) * len(specs)} models")

if len(results_df) > 0:
    print("\nFirst 5 results:")
    print(results_df[['outcome', 'specification', 'coefficient', 
                      'std_error', 'p_value']].head())
    
    # Summary stats
    sig_5pct = results_df['significant_5pct'].sum()
    sig_10pct = results_df['significant_10pct'].sum()
    print(f"\nSignificant at 5%: {sig_5pct}/{len(results_df)}")
    print(f"Significant at 10%: {sig_10pct}/{len(results_df)}")
    
    print("\n" + "="*60)
    print("✓ ALL TESTS PASSED")
    print("="*60)
else:
    print("\n✗ No results returned - check for errors in estimation")
