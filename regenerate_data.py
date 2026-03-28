from asean_green_bonds.data.processing import prepare_full_panel_data
from pathlib import Path
import os

print("Regenerating full panel data with outlier handling for implied_cost_of_debt...")
df = prepare_full_panel_data(min_years_per_firm=3)
print(f"Data regeneration complete. Shape: {df.shape}")

# Also update the full_panel_data.csv specifically to be sure
# prepare_full_panel_data should have written it to processed_data/full_panel_data.csv
# but let's double check if it actually exists there.
output_path = Path("processed_data/full_panel_data.csv")
if output_path.exists():
    print(f"Verified: {output_path} updated.")
else:
    print(f"Warning: {output_path} not found. Saving manually...")
    df.to_csv(output_path, index=False)
