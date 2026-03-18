#!/usr/bin/env python3
"""
Validation utility for green bonds LSEG retrieval output.
Checks data quality and completeness of green_bonds_lseg_full.csv
"""

import pandas as pd
import sys
from pathlib import Path

def validate_output(filepath='data/green_bonds_lseg_full.csv'):
    """Validate the green bonds output CSV file."""
    
    print("\n" + "=" * 70)
    print("Green Bonds LSEG Output Validation")
    print("=" * 70)
    
    # Check file existence
    if not Path(filepath).exists():
        print(f"✗ File not found: {filepath}")
        return False
    
    print(f"\n✓ File found: {filepath}")
    
    try:
        # Load the data
        df = pd.read_csv(filepath)
        print(f"\n[Data Structure]")
        print(f"  Records: {len(df):,}")
        print(f"  Fields: {len(df.columns)}")
        print(f"  Memory: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        # Check key fields
        print(f"\n[Key Fields Validation]")
        key_fields = ['TR.DealPermId', 'TR.FiIssuerName', 'TR.FiIssueDate']
        for field in key_fields:
            if field in df.columns:
                missing = df[field].isnull().sum()
                populated = len(df) - missing
                pct = (populated / len(df) * 100) if len(df) > 0 else 0
                status = "✓" if pct >= 50 else "⚠"
                print(f"  {status} {field}: {populated:,}/{len(df)} ({pct:.1f}%)")
            else:
                print(f"  ✗ {field}: NOT FOUND")
        
        # Missing values analysis
        print(f"\n[Missing Values Analysis]")
        missing_summary = df.isnull().sum()
        missing_by_pct = (missing_summary / len(df) * 100).sort_values(ascending=False)
        
        high_missing = missing_by_pct[missing_by_pct > 50]
        if len(high_missing) > 0:
            print(f"  Fields with >50% missing values: {len(high_missing)}")
            for field, pct in high_missing.head(5).items():
                print(f"    - {field}: {pct:.1f}%")
        else:
            print(f"  ✓ All fields have <50% missing values")
        
        # Field batch coverage
        print(f"\n[Field Batch Coverage]")
        field_batches = {
            "Deal Identifiers & Basic": ["TR.DealPermId", "TR.FiIssueDate", "TR.CouponRate"],
            "Issuer Info": ["TR.FiIssuerName", "TR.FiIssuerPermID", "TR.FiIssueType"],
            "Pricing & Proceeds": ["TR.FiOfferPrice", "TR.FiProceedsAmountIncOverallotment"],
            "ESG & Green": ["TR.EnvironmentPillarScore", "TR.GreenRevenue", "TR.GreenBondFramework"],
            "Market & Geographic": ["TR.FiIssuerSubRegion", "TR.FiIssuerRegion"],
            "Sector & Classification": ["TR.FiIssuerTRBCBusinessSector", "TR.FiMasterDealType"]
        }
        
        for batch_name, sample_fields in field_batches.items():
            found = sum(1 for f in sample_fields if f in df.columns)
            status = "✓" if found == len(sample_fields) else "⚠"
            print(f"  {status} {batch_name}: {found}/{len(sample_fields)} fields")
        
        # Data type summary
        print(f"\n[Data Type Summary]")
        dtype_counts = df.dtypes.value_counts()
        for dtype, count in dtype_counts.items():
            print(f"  {dtype}: {count} fields")
        
        # Sample records
        print(f"\n[Sample Records]")
        print(f"  Showing first 3 records and 5 sample fields:")
        sample_cols = [col for col in df.columns if col in 
                      ['TR.DealPermId', 'TR.FiIssuerName', 'TR.FiIssueDate', 
                       'TR.FiIssueType', 'TR.FiOfferPrice']][:5]
        if sample_cols:
            print(df[sample_cols].head(3).to_string())
        
        print("\n" + "=" * 70)
        print("✓ Validation complete. Output appears valid for analysis.")
        print("=" * 70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error reading file: {e}")
        return False

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else 'data/green_bonds_lseg_full.csv'
    success = validate_output(output_file)
    sys.exit(0 if success else 1)

╭ I see the LSEG retrieval is failing with "Unable to resolve identifiers" and "Inv…╮