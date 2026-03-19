"""
Regenerate final_engineered_panel_data.csv with the winsorize bug fixed.
"""
import pandas as pd
import sys
sys.path.insert(0, '.')
from asean_green_bonds import config, data

print("="*70)
print("REGENERATING FINAL ENGINEERED PANEL DATA")
print("="*70)

# Load cleaned data
print("\n1. Loading cleaned data...")
df = pd.read_csv(config.PROCESSED_DATA_FILES["cleaned"])
print(f"   ✓ Loaded: {df.shape}")
print(f"   ✓ total_assets: std={df['total_assets'].std():.2f}, unique={df['total_assets'].nunique()}")

# Create financial ratios
print("\n2. Creating financial ratios...")
df = data.create_financial_ratios(df)
print(f"   ✓ Done: Firm_Size std={df['Firm_Size'].std():.4f}")

# Create lagged features
print("\n3. Creating lagged features...")
df = data.create_lagged_features(
    df,
    firm_col='ric',
    vars_to_lag=['Firm_Size', 'Leverage', 'Asset_Turnover', 'Cash_Ratio', 'Capital_Intensity',
                 'return_on_assets', 'esg_score'],
    lags=[1]
)
print(f"   ✓ Done: L1_Firm_Size std={df['L1_Firm_Size'].std():.4f}, unique={df['L1_Firm_Size'].nunique()}")

# Create log features
print("\n4. Creating log features...")
df = data.create_log_features(df, cols_to_log=['total_assets', 'employees', 'net_sales_or_revenues'])
print(f"   ✓ Done")

# Normalize percentages
print("\n5. Normalizing percentages...")
df = data.normalize_percentages(df, pct_cols=['return_on_assets', 'return_on_equity_total'])
print(f"   ✓ Done")

# Winsorize outliers (with the FIX!)
print("\n6. Winsorizing outliers (FIXED)...")
df = data.winsorize_outliers(df)
print(f"   ✓ Done: total_assets std={df['total_assets'].std():.2f}, unique={df['total_assets'].nunique()}")
print(f"   ✓ Firm_Size std={df['Firm_Size'].std():.4f}")
print(f"   ✓ L1_Firm_Size std={df['L1_Firm_Size'].std():.4f}")

# Encode categorical
print("\n7. Encoding categorical features...")
df = data.encode_categorical_features(df)
print(f"   ✓ Done")

# Save
print("\n8. Saving...")
df.to_csv(config.PROCESSED_DATA_FILES["engineered"], index=False)
print(f"   ✓ Saved to: {config.PROCESSED_DATA_FILES['engineered']}")

# Verify
print("\n" + "="*70)
print("VERIFICATION")
print("="*70)

vars_to_check = ['total_assets', 'Firm_Size', 'Leverage', 'L1_Firm_Size', 'L1_Leverage']
for var in vars_to_check:
    if var in df.columns:
        std = df[var].std()
        unique = df[var].nunique()
        status = '✅' if std > 0.001 else '❌'
        print(f"{status} {var:20s}: std={std:12.4f}, unique={unique:6d}")

print("\n✅ REGENERATION COMPLETE!")
