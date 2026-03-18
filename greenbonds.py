import refinitiv.data as rd
import pandas as pd
import time
from datetime import datetime
import os

print("Green Bonds Data Retrieval - LSEG Batched Retrieval")
print("=" * 70)

# 1. Open Desktop Session (ensure LSEG Workspace is running)
print("\n[1/5] Opening LSEG Workspace session...")
try:
    rd.open_session()
    print("✓ Session opened successfully")
except Exception as e:
    print(f"✗ Error opening session: {e}")
    print("Ensure LSEG Workspace is running and try again.")
    exit(1)

# 2. Load universe from existing bond data
print("\n[2/5] Loading bond identifiers from existing data...")
try:
    existing_df = pd.read_csv('data/green_bonds_authentic.csv')
    # Extract unique deal identifiers (assuming DealPermId or similar column exists)
    if 'DealPermId' in existing_df.columns:
        universe = existing_df['DealPermId'].unique().tolist()
    else:
        # Fallback: use first available identifier column
        universe = existing_df.iloc[:, 0].unique().tolist()
    print(f"✓ Loaded {len(universe)} bond identifiers")
except FileNotFoundError:
    print("✗ green_bonds_authentic.csv not found. Using example identifiers.")
    universe = []
except Exception as e:
    print(f"✗ Error loading identifiers: {e}")
    universe = []

if not universe:
    print("Warning: No universe loaded. Script will attempt with empty universe.")

# 3. Define field batches to avoid API overload
print("\n[3/5] Preparing field batches (6 batches, 10-15 fields each)...")

field_batches = {
    "Batch 1 - Deal Identifiers & Basic Info": [
        "TR.DealPermId",
        "TR.FiPackageId",
        "TR.FiMasterDealTypeCode",
        "TR.FiAllManagerRolesCode",
        "TR.FiManagerRoleCode",
        "TR.FiIssueDate",
        "TR.FiMaturityDate",
        "TR.CouponRate"
    ],
    "Batch 2 - Issuer Info & Classification": [
        "TR.FiIssuerName",
        "TR.FiIssuerPermID",
        "TR.FiIssueType",
        "TR.FiTransactionStatus",
        "TR.FiIssuerNation",
        "TR.FiFilingDate",
        "TR.FiIssuerExchangeName",
        "TR.FiSecurityTypeAllMkts"
    ],
    "Batch 3 - Pricing & Proceeds": [
        "TR.FiOfferPrice",
        "TR.FiProceedsAmountIncOverallotment",
        "TR.FiProceedsAmountThisMarket",
        "TR.EOMPrice",
        "TR.CurrentYield"
    ],
    "Batch 4 - ESG & Green Bond Specific": [
        "TR.EnvironmentPillarScore",
        "TR.GreenRevenue",
        "TR.FiUseOfProceeds",
        "TR.CBIIndicator",
        "TR.GreenBondFramework",
        "TR.FiOfferingTechnique",
        "TR.FiGrossSpreadPct",
        "TR.FaceIssuedTotal"
    ],
    "Batch 5 - Market & Geographic Info": [
        "TR.FiIssuerSubRegion",
        "TR.FiIssuerRegion",
        "TR.FiIssuerNationRegion",
        "TR.FiLeadLeftBookrunner",
        "TR.FiManagersTier1Tier2",
        "TR.FiECMFlag"
    ],
    "Batch 6 - Sector & Classification": [
        "TR.FiIssuerTRBCBusinessSector",
        "TR.FiIssuerTRBCEconomicSector",
        "TR.FiMasterDealType",
        "TR.FiAllManagerRoles",
        "TR.FiManagerRole"
    ]
}

print(f"✓ Prepared {len(field_batches)} batches")

# 4. Execute batched data retrieval
print("\n[4/5] Executing batched LSEG data retrieval...")
all_data = []
batch_results = {}

for batch_name, fields in field_batches.items():
    print(f"\n  {batch_name} ({len(fields)} fields)")
    try:
        print(f"    → Querying {len(universe)} identifiers...")
        df_batch = rd.get_data(universe=universe, fields=fields)
        batch_results[batch_name] = df_batch
        all_data.append(df_batch)
        print(f"    ✓ Retrieved {len(df_batch)} records")
        
        # Add delay between batch requests to prevent server overload
        time.sleep(1.5)
    except Exception as e:
        print(f"    ✗ Error: {e}")
        print(f"    Continuing with remaining batches...")
        continue

# 5. Consolidate batch results
print("\n[5/5] Consolidating batch results...")
if all_data:
    try:
        # Merge all batches on the index (which typically contains identifiers)
        consolidated_df = all_data[0]
        for i, df_batch in enumerate(all_data[1:], 1):
            consolidated_df = consolidated_df.join(df_batch, how='outer')
        
        # Save to CSV
        output_path = 'data/green_bonds_lseg_full.csv'
        os.makedirs('data', exist_ok=True)
        consolidated_df.to_csv(output_path)
        
        print(f"✓ Consolidated {len(consolidated_df)} records from {len(batch_results)} batches")
        print(f"✓ Total fields retrieved: {len(consolidated_df.columns)}")
        print(f"✓ Saved to: {output_path}")
        
        # Data quality summary
        print(f"\nData Quality Summary:")
        print(f"  - Records: {len(consolidated_df)}")
        print(f"  - Fields: {len(consolidated_df.columns)}")
        print(f"  - Memory usage: {consolidated_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        print(f"  - Missing values: {consolidated_df.isnull().sum().sum()} cells")
        
    except Exception as e:
        print(f"✗ Error consolidating results: {e}")
else:
    print("✗ No data retrieved from any batch.")

# 6. Clean up and close session
print("\n" + "=" * 70)
rd.close_session()
print("✓ Session closed.")