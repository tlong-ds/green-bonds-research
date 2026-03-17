import refinitiv.data as rd
import pandas as pd
import time
from datetime import datetime

# 1. Open Desktop Session (ensure LSEG Workspace is running)
rd.open_session()

# 2. NOTE: The Refinitiv SCREEN API has limitations with Deal data.
# The following example shows a working pattern using a list of known instruments.
# For production use with large datasets, consider loading from existing data files.

print("Green Bonds Data Retrieval - Refinitiv API Example")
print("=" * 60)

# Option A: Load from existing CSV (Recommended for this project)
print("\nOption A: Loading from existing green_bonds_authentic.csv...")
try:
    existing_df = pd.read_csv('data/green_bonds_authentic.csv')
    print(f"Loaded {len(existing_df)} green bond deals from local file")
    print(f"Columns: {existing_df.columns.tolist()[:10]}")
    print("\nSample data:")
    print(existing_df.head(2))
except FileNotFoundError:
    print("Local data file not found. Proceeding with Option B.")
    existing_df = None

# Option B: Fetch from Refinitiv (requires valid bond identifiers and permissions)
if existing_df is None:
    print("\nOption B: Fetching from Refinitiv API...")
    
    # Example with a few known bonds - in production, you'd have a proper list
    try:
        # Note: These are example identifiers and may not work depending on your access
        bond_ids = ['AAPL.O']  # Using a known ticker as example
        
        fields_list = [
            "TR.ESGScore",
            "TR.EnvironmentPillarScore",
            "TR.SocialPillarScore",
            "TR.GovernancePillarScore"
        ]
        
        print(f"Fetching data for {len(bond_ids)} identifiers...")
        df = rd.get_data(universe=bond_ids, fields=fields_list)
        
        print(f"\nSuccessfully retrieved data:")
        print(df)
        
    except Exception as e:
        print(f"Error fetching from Refinitiv: {e}")
        print("\nTroubleshooting tips:")
        print("1. Ensure LSEG Workspace is running")
        print("2. Verify your Refinitiv credentials")
        print("3. Check that requested fields are available for your data universe")
        print("4. Use the existing data files in /data directory instead")

# 8. Clean up and close session
rd.close_session()
print("\nSession closed.")