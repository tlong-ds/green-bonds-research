#!/usr/bin/env python3
"""
Example: Using PSM Feature Engineering in Data Preparation

This example demonstrates how to use the feature_engineering module
to generate the 4 missing PSM attributes for your analysis.

Usage:
    python psm_feature_engineering_example.py
"""

import pandas as pd
from asean_green_bonds.data.feature_engineering import engineer_psm_attributes


def main():
    """Run the feature engineering pipeline."""
    
    print("="*70)
    print("PSM FEATURE ENGINEERING EXAMPLE")
    print("="*70)
    
    # Step 1: Load data
    print("\nStep 1: Loading data...")
    gb_df = pd.read_csv('data/green_bonds_with_authenticity_score.csv')
    gb_raw = pd.read_csv('data/green-bonds.csv')
    print(f"  ✓ Green bonds dataset: {gb_df.shape}")
    print(f"  ✓ Raw green bonds data: {gb_raw.shape}")
    
    # Step 2: Engineer PSM attributes
    print("\nStep 2: Engineering PSM attributes...")
    df_engineered, metadata = engineer_psm_attributes(
        gb_df,
        gb_raw=gb_raw,
        verbose=True
    )
    
    # Step 3: Save engineered dataset
    print("\nStep 3: Saving engineered dataset...")
    output_path = 'data/green_bonds_with_psm_features.csv'
    df_engineered.to_csv(output_path, index=False)
    print(f"  ✓ Saved to: {output_path}")
    print(f"  ✓ Shape: {df_engineered.shape}")
    
    # Step 4: Display engineering summary
    print("\n" + "="*70)
    print("ENGINEERING SUMMARY")
    print("="*70)
    
    for var, desc in metadata.items():
        print(f"\n{var}:")
        print(f"  Method: {desc}")
        print(f"  Non-null: {df_engineered[var].notna().sum()}/{len(df_engineered)}")
    
    # Step 5: Display sample data
    print("\n" + "="*70)
    print("SAMPLE DATA (First 5 rows with PSM features)")
    print("="*70)
    
    sample_cols = [
        'Deal PermID',
        'Issuer/Borrower Name Full',
        'Has_Green_Framework',
        'Asset_Tangibility',
        'Issuer_Track_Record',
        'Prior_Green_Bonds',
    ]
    print(df_engineered[sample_cols].head().to_string())
    
    # Step 6: Validation
    print("\n" + "="*70)
    print("VALIDATION")
    print("="*70)
    
    # Check ranges
    checks = [
        ("Has_Green_Framework in {0,1}", 
         df_engineered['Has_Green_Framework'].isin([0, 1]).all()),
        ("Asset_Tangibility in [0,1]", 
         ((df_engineered['Asset_Tangibility'] >= 0) & (df_engineered['Asset_Tangibility'] <= 1)).all()),
        ("Issuer_Track_Record >= 0", 
         (df_engineered['Issuer_Track_Record'] >= 0).all()),
        ("Prior_Green_Bonds >= 0", 
         (df_engineered['Prior_Green_Bonds'] >= 0).all()),
        ("No missing values", 
         df_engineered[['Has_Green_Framework', 'Asset_Tangibility', 'Issuer_Track_Record', 'Prior_Green_Bonds']].notna().all().all()),
    ]
    
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"  {status} {check_name}")
    
    print("\n✅ Feature engineering completed successfully!")
    print(f"\nYour engineered dataset is ready for PSM-DiD analysis.")
    print(f"Use: df = pd.read_csv('data/green_bonds_with_psm_features.csv')")
    
    return df_engineered


if __name__ == '__main__':
    main()
