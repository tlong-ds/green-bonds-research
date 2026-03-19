"""
Calculate Tobin's Q and add it to the panel data.

Tobin's Q = (Market Value of Equity + Total Liabilities) / Total Assets
"""
import pandas as pd
import numpy as np

print("Loading data...")
df = pd.read_csv('processed_data/final_engineered_panel_data.csv')
print(f"✓ Loaded {len(df)} observations")

# Calculate Tobin's Q
print("\nCalculating Tobin's Q...")

# Method 1: Using market_capitalization (market value of equity)
if 'market_capitalization' in df.columns and 'total_liabilities' in df.columns and 'total_assets' in df.columns:
    df['Tobin_Q'] = (df['market_capitalization'] + df['total_liabilities']) / df['total_assets']
    print("✓ Calculated Tobin_Q using market_capitalization")
# Method 2: Fallback to market_value if market_capitalization not available
elif 'market_value' in df.columns and 'total_liabilities' in df.columns and 'total_assets' in df.columns:
    df['Tobin_Q'] = (df['market_value'] + df['total_liabilities']) / df['total_assets']
    print("✓ Calculated Tobin_Q using market_value")
else:
    print("✗ Cannot calculate Tobin_Q - missing required columns")
    exit(1)

# Check the results
non_null = df['Tobin_Q'].notna().sum()
print(f"✓ Tobin_Q has {non_null:,} non-null values ({non_null/len(df)*100:.1f}%)")

# Show some statistics
print("\nTobin's Q statistics:")
print(df['Tobin_Q'].describe())

# Check for outliers
q1 = df['Tobin_Q'].quantile(0.01)
q99 = df['Tobin_Q'].quantile(0.99)
print(f"\n1st percentile: {q1:.2f}")
print(f"99th percentile: {q99:.2f}")

# Winsorize extreme values (optional - comment out if you want raw values)
outliers_before = ((df['Tobin_Q'] < 0) | (df['Tobin_Q'] > 10)).sum()
df.loc[df['Tobin_Q'] < 0, 'Tobin_Q'] = np.nan
df.loc[df['Tobin_Q'] > 10, 'Tobin_Q'] = 10  # Cap at 10
outliers_after = df['Tobin_Q'].isna().sum() - (df['total_assets'].isna().sum())
print(f"\n⚠️  Removed {outliers_before} extreme/negative values")
print(f"✓ Final Tobin_Q has {df['Tobin_Q'].notna().sum():,} valid values")

# Save updated data
output_path = 'processed_data/final_engineered_panel_data.csv'
df.to_csv(output_path, index=False)
print(f"\n✓ Saved updated data to {output_path}")
print(f"✓ Added column: Tobin_Q")
