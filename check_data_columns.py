"""
Quick diagnostic script to check available columns in the panel data.
"""
import pandas as pd

print("Loading data...")
df = pd.read_csv('processed_data/final_engineered_panel_data.csv')

print(f"\n✓ Loaded {len(df)} observations")
print(f"✓ Shape: {df.shape}")

print("\n" + "="*60)
print("AVAILABLE COLUMNS")
print("="*60)

# Show all columns
print(f"\nTotal columns: {len(df.columns)}")
print("\nAll columns:")
for i, col in enumerate(df.columns, 1):
    print(f"  {i:3d}. {col}")

# Check for the requested outcome variables
print("\n" + "="*60)
print("CHECKING REQUESTED OUTCOME VARIABLES")
print("="*60)

requested_outcomes = ['return_on_assets', 'Tobin_Q', 'esg_score']

for outcome in requested_outcomes:
    if outcome in df.columns:
        non_null = df[outcome].notna().sum()
        print(f"✅ {outcome:20s} - Found ({non_null:,} non-null values)")
    else:
        # Try to find similar column names
        similar = [c for c in df.columns if outcome.lower() in c.lower() or c.lower() in outcome.lower()]
        if similar:
            print(f"❌ {outcome:20s} - NOT FOUND. Similar: {similar}")
        else:
            print(f"❌ {outcome:20s} - NOT FOUND")

# Check for common financial metrics that might be alternatives
print("\n" + "="*60)
print("COMMON FINANCIAL METRICS IN DATA")
print("="*60)

common_metrics = ['roa', 'roe', 'tobin', 'esg', 'return', 'profit', 'asset']
found_metrics = []

for metric in common_metrics:
    matching = [c for c in df.columns if metric.lower() in c.lower()]
    if matching:
        found_metrics.extend(matching)

found_metrics = sorted(set(found_metrics))
if found_metrics:
    print("\nFinancial/performance columns found:")
    for col in found_metrics:
        non_null = df[col].notna().sum()
        print(f"  • {col:40s} ({non_null:,} non-null)")
else:
    print("No common financial metrics found")

# Check required variables
print("\n" + "="*60)
print("CHECKING REQUIRED VARIABLES")
print("="*60)

required = ['ric', 'Year', 'green_bond_active', 'L1_Firm_Size', 'L1_Leverage']
for var in required:
    if var in df.columns:
        non_null = df[var].notna().sum()
        print(f"✅ {var:20s} - Found ({non_null:,} non-null values)")
    else:
        print(f"❌ {var:20s} - NOT FOUND")
