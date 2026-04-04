"""
Validation Script: Verify Professor Feedback Fixes

This script validates that all data quality improvements have been successfully
applied to the processed dataset.
"""

import pandas as pd
import numpy as np
from pathlib import Path

def validate_fixes():
    """Run all validation checks."""
    
    print("="*70)
    print("VALIDATION REPORT: PROFESSOR FEEDBACK FIXES")
    print("="*70)
    print()
    
    # Load processed data
    data_path = Path("processed_data/full_panel_data.csv")
    if not data_path.exists():
        print("❌ ERROR: processed_data/full_panel_data.csv not found!")
        return False
    
    df = pd.read_csv(data_path, low_memory=False)
    print(f"✓ Loaded data: {df.shape[0]:,} rows × {df.shape[1]} columns")
    print()
    
    all_passed = True
    
    # =========================================================================
    # Test 1: asset_tangibility - Must have meaningful variance
    # =========================================================================
    print("-" * 70)
    print("TEST 1: asset_tangibility Zero-Variance Fix")
    print("-" * 70)
    
    if 'asset_tangibility' in df.columns:
        tang_stats = df['asset_tangibility'].describe()
        tang_std = df['asset_tangibility'].std()
        tang_unique = df['asset_tangibility'].nunique()
        
        print(f"  Mean:    {tang_stats['mean']:.3f}")
        print(f"  Std:     {tang_stats['std']:.3f}")
        print(f"  Min:     {tang_stats['min']:.3f}")
        print(f"  25%:     {tang_stats['25%']:.3f}")
        print(f"  Median:  {tang_stats['50%']:.3f}")
        print(f"  75%:     {tang_stats['75%']:.3f}")
        print(f"  Max:     {tang_stats['max']:.3f}")
        print(f"  Unique:  {tang_unique:,} values")
        print()
        
        # Check for meaningful variance (std > 0.05)
        if tang_std > 0.05:
            print(f"  ✅ PASS: Standard deviation ({tang_std:.3f}) > 0.05")
        else:
            print(f"  ❌ FAIL: Standard deviation ({tang_std:.3f}) ≤ 0.05")
            all_passed = False
        
        # Check that not all values are the same
        if tang_unique > 100:
            print(f"  ✅ PASS: {tang_unique:,} unique values (not constant)")
        else:
            print(f"  ⚠️  WARNING: Only {tang_unique} unique values")
            
        # Check for the old problem (most values = 0.55)
        pct_at_default = (df['asset_tangibility'] == 0.55).sum() / len(df) * 100
        if pct_at_default < 50:
            print(f"  ✅ PASS: Only {pct_at_default:.1f}% at default value (0.55)")
        else:
            print(f"  ❌ FAIL: {pct_at_default:.1f}% still at default (0.55)")
            all_passed = False
    else:
        print("  ❌ FAIL: asset_tangibility column not found")
        all_passed = False
    
    print()
    
    # =========================================================================
    # Test 2: Capital_Intensity - Must be capped at 100
    # =========================================================================
    print("-" * 70)
    print("TEST 2: Capital_Intensity Extreme Value Cap")
    print("-" * 70)
    
    cap_int_cols = ['Capital_Intensity', 'L1_Capital_Intensity']
    for col in cap_int_cols:
        if col in df.columns:
            cap_max = df[col].max()
            cap_mean = df[col].mean()
            cap_median = df[col].median()
            
            print(f"  {col}:")
            print(f"    Mean:   {cap_mean:.2f}")
            print(f"    Median: {cap_median:.2f}")
            print(f"    Max:    {cap_max:.2f}")
            
            if cap_max <= 100:
                print(f"    ✅ PASS: Max ({cap_max:.2f}) ≤ 100")
            else:
                print(f"    ❌ FAIL: Max ({cap_max:.2f}) > 100")
                all_passed = False
            print()
    
    # =========================================================================
    # Test 3: Cash_Ratio - Must be capped at 5.0
    # =========================================================================
    print("-" * 70)
    print("TEST 3: Cash_Ratio Outlier Cap")
    print("-" * 70)
    
    cash_cols = ['Cash_Ratio', 'L1_Cash_Ratio']
    for col in cash_cols:
        if col in df.columns:
            cash_max = df[col].max()
            cash_mean = df[col].mean()
            cash_median = df[col].median()
            
            print(f"  {col}:")
            print(f"    Mean:   {cash_mean:.2f}")
            print(f"    Median: {cash_median:.2f}")
            print(f"    Max:    {cash_max:.2f}")
            
            if cash_max <= 5.0:
                print(f"    ✅ PASS: Max ({cash_max:.2f}) ≤ 5.0")
            else:
                print(f"    ❌ FAIL: Max ({cash_max:.2f}) > 5.0")
                all_passed = False
            print()
    
    # =========================================================================
    # Test 4: ESG Score - Check normalization to 0-1
    # =========================================================================
    print("-" * 70)
    print("TEST 4: ESG Score Normalization")
    print("-" * 70)
    
    if 'esg_score' in df.columns:
        esg_stats = df['esg_score'].describe()
        print(f"  Mean:  {esg_stats['mean']:.3f}")
        print(f"  Min:   {esg_stats['min']:.3f}")
        print(f"  Max:   {esg_stats['max']:.3f}")
        
        if esg_stats['max'] <= 1.0 and esg_stats['min'] >= 0:
            print(f"  ✅ PASS: ESG Score in [0, 1] range")
        else:
            print(f"  ⚠️  WARNING: ESG Score outside [0, 1] range")
        print()
    
    # =========================================================================
    # Test 5: ROA - Can be negative
    # =========================================================================
    print("-" * 70)
    print("TEST 5: ROA Can Be Negative (Loss-Making Firms)")
    print("-" * 70)
    
    if 'return_on_assets' in df.columns:
        roa_stats = df['return_on_assets'].describe()
        roa_negative_pct = (df['return_on_assets'] < 0).sum() / df['return_on_assets'].notna().sum() * 100
        
        print(f"  Mean:     {roa_stats['mean']:.4f}")
        print(f"  Min:      {roa_stats['min']:.4f}")
        print(f"  Max:      {roa_stats['max']:.4f}")
        print(f"  Negative: {roa_negative_pct:.1f}% of firms")
        
        if roa_stats['min'] < 0:
            print(f"  ✅ PASS: ROA can be negative (captures losses)")
        else:
            print(f"  ⚠️  INFO: No negative ROA values in sample")
        print()
    
    # =========================================================================
    # Test 6: Tobin's Q - Check cap at 10
    # =========================================================================
    print("-" * 70)
    print("TEST 6: Tobin's Q Cap")
    print("-" * 70)
    
    if 'Tobin_Q' in df.columns:
        tobin_max = df['Tobin_Q'].max()
        tobin_mean = df['Tobin_Q'].mean()
        
        print(f"  Mean: {tobin_mean:.2f}")
        print(f"  Max:  {tobin_max:.2f}")
        
        if tobin_max <= 10.0:
            print(f"  ✅ PASS: Max ({tobin_max:.2f}) ≤ 10.0")
        else:
            print(f"  ❌ FAIL: Max ({tobin_max:.2f}) > 10.0")
            all_passed = False
        print()
    
    # =========================================================================
    # Test 7: Cost of Debt - Check cap at 0.5
    # =========================================================================
    print("-" * 70)
    print("TEST 7: Cost of Debt Cap")
    print("-" * 70)
    
    if 'implied_cost_of_debt' in df.columns:
        cod_max = df['implied_cost_of_debt'].max()
        cod_mean = df['implied_cost_of_debt'].mean()
        cod_count = df['implied_cost_of_debt'].notna().sum()
        
        print(f"  Mean:        {cod_mean:.4f}")
        print(f"  Max:         {cod_max:.4f}")
        print(f"  Observations: {cod_count:,}")
        
        if cod_max <= 0.5:
            print(f"  ✅ PASS: Max ({cod_max:.4f}) ≤ 0.50")
        else:
            print(f"  ❌ FAIL: Max ({cod_max:.4f}) > 0.50")
            all_passed = False
        print()
    
    # =========================================================================
    # Summary
    # =========================================================================
    print("="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print()
        print("All data quality fixes have been successfully applied.")
        print("The processed data is ready for analysis.")
    else:
        print("❌ SOME TESTS FAILED")
        print()
        print("Please review the failures above and re-run the data pipeline.")
    
    print("="*70)
    
    return all_passed


if __name__ == "__main__":
    success = validate_fixes()
    exit(0 if success else 1)
