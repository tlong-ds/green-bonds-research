"""
Feature Engineering Module for PSM Attributes

Handles engineering of missing PSM (Propensity Score Matching) attributes:
- Has_Green_Framework (existing, rename)
- Issuer_Track_Record (existing, rename)
- Asset_Tangibility (engineer from sector proxy)
- Prior_Green_Bonds (engineer from issuance history)
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple


# Sector-based tangibility ratios for Asset_Tangibility engineering
SECTOR_TANGIBILITY = {
    'Utilities': 0.70,
    'Energy': 0.75,
    'Infrastructure': 0.72,
    'Real Estate': 0.85,
    'Manufacturing': 0.65,
    'Transportation': 0.68,
    'Finance': 0.35,
    'Financial Services': 0.35,
    'Technology': 0.25,
    'Healthcare': 0.40,
    'Consumer': 0.45,
    'Telecommunications': 0.55,
    'Diversified': 0.50,
}

DEFAULT_TANGIBILITY = 0.55  # Cross-sector average fallback


def engineer_psm_attributes(
    gb_df: pd.DataFrame,
    gb_raw: pd.DataFrame = None,
    verbose: bool = True
) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    Engineer all missing PSM attributes for green bonds dataset.
    
    Parameters
    ----------
    gb_df : pd.DataFrame
        Green bonds dataframe with authenticity scores
        (e.g., green_bonds_with_authenticity_score.csv)
    gb_raw : pd.DataFrame, optional
        Raw green bonds dataframe with issue dates
        If None, will try to load from data directory
    verbose : bool
        If True, print detailed status messages
        
    Returns
    -------
    tuple
        (engineered_df, engineering_metadata)
        - engineered_df: DataFrame with 4 new PSM attributes
        - engineering_metadata: Dict with engineering method details
    """
    
    if verbose:
        print("="*70)
        print("ENGINEERING MISSING PSM ATTRIBUTES")
        print("="*70)
    
    df = gb_df.copy()
    metadata = {}
    
    # ========================================================================
    # Step 1: Ensure we have issue dates
    # ========================================================================
    
    if 'Dates: Issue Date' not in df.columns:
        if gb_raw is not None and 'Dates: Issue Date' in gb_raw.columns:
            # Determine which columns to merge
            merge_cols = ['Deal PermID', 'Dates: Issue Date']
            if 'Issuer/Borrower TRBC Economic Sector' not in df.columns and 'Issuer/Borrower TRBC Economic Sector' in gb_raw.columns:
                merge_cols.append('Issuer/Borrower TRBC Economic Sector')
            if 'Issuer/Borrower PermID' not in df.columns and 'Issuer/Borrower PermID' in gb_raw.columns:
                merge_cols.append('Issuer/Borrower PermID')
            
            df = df.merge(
                gb_raw[merge_cols],
                on='Deal PermID',
                how='left'
            )
        else:
            if verbose:
                print("\n⚠ Warning: No issue date information available")
                print("  Prior_Green_Bonds will be set to 0 for all records")
            df['Dates: Issue Date'] = None
    
    # ========================================================================
    # Step 1: Standardize existing attributes
    # ========================================================================
    
    if verbose:
        print("\nStep 1: Standardizing existing attributes (lowercase)...")
    
    if 'has_green_framework' in df.columns:
        # Already lowercase, just ensure it's present
        metadata['has_green_framework'] = 'From issuer verification (already present)'
        if verbose:
            print(f"  ✓ has_green_framework: {df['has_green_framework'].sum()} issuers")
    else:
        raise ValueError("Missing column: has_green_framework")
    
    if 'issuer_track_record' in df.columns:
        # Already lowercase, just ensure it's present
        metadata['issuer_track_record'] = 'From issuer verification (already present)'
        if verbose:
            print(f"  ✓ issuer_track_record: min={df['issuer_track_record'].min()}, max={df['issuer_track_record'].max()}")
    else:
        raise ValueError("Missing column: issuer_track_record")
    
    # ========================================================================
    # Step 2: Engineer Prior_Green_Bonds from issuance history
    # ========================================================================
    
    if verbose:
        print("\nStep 2: Engineering prior_green_bonds from issuance history...")
    
    if df['Dates: Issue Date'].notna().sum() > 0:
        # Parse dates and sort
        df['Issue_Date_Parsed'] = pd.to_datetime(df['Dates: Issue Date'], errors='coerce')
        df_sorted = df.sort_values(['Issuer/Borrower Name Full', 'Issue_Date_Parsed']).reset_index(drop=True)
        
        # Count prior issues per issuer
        prior_bonds_values = df_sorted.groupby('Issuer/Borrower Name Full').cumcount()
        
        # Map back to original order
        df = df.sort_values(['Issuer/Borrower Name Full', 'Issue_Date_Parsed']).reset_index(drop=True)
        df['prior_green_bonds'] = df.groupby('Issuer/Borrower Name Full').cumcount().values
        df = df.sort_values('Deal PermID').reset_index(drop=True)
        
        metadata['prior_green_bonds'] = 'Count of prior issuances by issuer (from issue date history)'
        
        if verbose:
            print(f"  ✓ prior_green_bonds: 0 to {df['prior_green_bonds'].max()}")
            print(f"    - First-time issuers: {(df['prior_green_bonds'] == 0).sum()}")
            print(f"    - Repeat issuers: {(df['prior_green_bonds'] > 0).sum()}")
    else:
        # No date information available
        df['prior_green_bonds'] = 0
        metadata['prior_green_bonds'] = 'Set to 0 (no issue date data available)'
        if verbose:
            print("  ⚠ No issue date data - setting all to 0")
    
    # ========================================================================
    # Step 3: Engineer Asset_Tangibility from sector proxy
    # ========================================================================
    
    if verbose:
        print("\nStep 3: Estimating asset_tangibility by sector...")
    
    if 'Issuer/Borrower TRBC Economic Sector' not in df.columns:
        if verbose:
            print("  ⚠ Missing economic sector info - using default tangibility")
        df['asset_tangibility'] = DEFAULT_TANGIBILITY
        metadata['asset_tangibility'] = f'Default value ({DEFAULT_TANGIBILITY})'
    else:
        df['asset_tangibility'] = (
            df['Issuer/Borrower TRBC Economic Sector']
            .map(SECTOR_TANGIBILITY)
            .fillna(DEFAULT_TANGIBILITY)
        )
        metadata['asset_tangibility'] = 'Sector-based proxy (theory: sector determines asset composition)'
        
        if verbose:
            print(f"  ✓ asset_tangibility: {df['asset_tangibility'].mean():.3f} (mean)")
            print(f"    Range: {df['asset_tangibility'].min():.2f} - {df['asset_tangibility'].max():.2f}")
            print(f"    Sectors mapped: {len(df[df['Issuer/Borrower TRBC Economic Sector'].isin(SECTOR_TANGIBILITY.keys())])}")
            print(f"    Using fallback: {(df['asset_tangibility'] == DEFAULT_TANGIBILITY).sum()}")
    
    # ========================================================================
    # Verification
    # ========================================================================
    
    if verbose:
        print("\n" + "="*70)
        print("VERIFICATION: All PSM Attributes Present")
        print("="*70)
    
    required_vars = [
        'has_green_framework',
        'asset_tangibility',
        'issuer_track_record',
        'prior_green_bonds',
    ]
    
    missing = []
    for var in required_vars:
        if var in df.columns:
            non_null = df[var].notna().sum()
            if verbose:
                status = "✓" if non_null == len(df) else "⚠"
                print(f"  {status} {var:30s} - {non_null:3d}/{len(df)} non-null")
            if non_null < len(df):
                missing.append(var)
        else:
            if verbose:
                print(f"  ✗ {var:30s} - MISSING")
            missing.append(var)
    
    if not missing:
        if verbose:
            print(f"\n✅ SUCCESS: All {len(required_vars)} PSM attributes engineered!")
    else:
        if verbose:
            print(f"\n❌ Missing: {missing}")
    
    # Clean up temporary columns
    df = df.drop(columns=['Issue_Date_Parsed'], errors='ignore')
    
    return df, metadata


def get_sector_tangibility_map() -> Dict[str, float]:
    """Get the sector tangibility mapping dictionary."""
    return SECTOR_TANGIBILITY.copy()


def get_default_tangibility() -> float:
    """Get the default tangibility value for unmapped sectors."""
    return DEFAULT_TANGIBILITY


def merge_psm_into_panel(
    panel_df: pd.DataFrame,
    gb_engineered_df: pd.DataFrame,
    market_df: pd.DataFrame,
    verbose: bool = True
) -> pd.DataFrame:
    """
    Merge engineered PSM attributes into the main panel dataset.
    
    Parameters
    ----------
    panel_df : pd.DataFrame
        Main panel dataset with firm-year observations
    gb_engineered_df : pd.DataFrame
        Green bonds data with engineered PSM attributes
    market_df : pd.DataFrame
        Market data with ric-org_permid mapping
    verbose : bool
        If True, print detailed status messages
        
    Returns
    -------
    pd.DataFrame
        Panel with merged PSM attributes
    """
    
    if verbose:
        print("="*70)
        print("MERGING PSM ATTRIBUTES INTO FINAL PANEL")
        print("="*70)
    
    def _first_non_null(series: pd.Series):
        non_null = series.dropna()
        if len(non_null) == 0:
            return np.nan
        return non_null.iloc[0]

    df = panel_df.copy()

    # Step 1: Add org_permid from market_df if not present
    if 'org_permid' not in df.columns:
        market_org_permid = market_df[['ric', 'org_permid']].drop_duplicates()
        df = df.merge(market_org_permid, on='ric', how='left')
        if verbose:
            print(f"\nStep 1: Added org_permid: {df['org_permid'].notna().sum()}/{len(df)} non-null")
    else:
        df['org_permid'] = pd.to_numeric(df['org_permid'], errors='coerce')
        if verbose:
            print(f"\nStep 1: org_permid already present: {df['org_permid'].notna().sum()}/{len(df)}")

    # Step 2: Prepare issuer-year PSM signals (avoid post-treatment leakage)
    if verbose:
        print("\nStep 2: Building issuer-year PSM attributes (time-varying)...")

    gb_prepared = gb_engineered_df.copy()
    gb_prepared['issue_year'] = pd.to_datetime(gb_prepared.get('Dates: Issue Date'), errors='coerce').dt.year
    gb_prepared['org_permid'] = pd.to_numeric(gb_prepared.get('Issuer/Borrower PermID'), errors='coerce')
    for col in ['has_green_framework', 'issuer_track_record', 'asset_tangibility']:
        if col not in gb_prepared.columns:
            gb_prepared[col] = np.nan
        gb_prepared[col] = pd.to_numeric(gb_prepared[col], errors='coerce')
    gb_prepared = gb_prepared.dropna(subset=['org_permid', 'issue_year'])
    gb_prepared['issue_year'] = gb_prepared['issue_year'].astype(int)

    if gb_prepared.empty:
        if verbose:
            print("  ⚠ No valid issue-year data found; using defaults only.")
        df['has_green_framework'] = 0
        df['asset_tangibility'] = DEFAULT_TANGIBILITY
        df['issuer_track_record'] = 0
        df['prior_green_bonds'] = 0
        return df

    # Issue counts by issuer-year
    issue_counts = gb_prepared.groupby(['org_permid', 'issue_year']).size().reset_index(name='issue_count')

    # Year-specific flags (max within year)
    year_flags = gb_prepared.groupby(['org_permid', 'issue_year']).agg(
        has_green_framework=('has_green_framework', 'max'),
        issuer_track_record=('issuer_track_record', 'max'),
    ).reset_index()

    issuer_year = issue_counts.merge(year_flags, on=['org_permid', 'issue_year'], how='left')
    issuer_year = issuer_year.sort_values(['org_permid', 'issue_year'])
    issuer_year['cumulative_issues'] = issuer_year.groupby('org_permid')['issue_count'].cumsum()
    issuer_year['prior_green_bonds'] = issuer_year.groupby('org_permid')['cumulative_issues'].shift(1).fillna(0)
    issuer_year['has_green_framework'] = issuer_year.groupby('org_permid')['has_green_framework'].cummax()
    issuer_year['issuer_track_record'] = issuer_year.groupby('org_permid')['issuer_track_record'].cummax()

    # Asset tangibility (issuer-level static proxy)
    asset_map = (
        gb_prepared.groupby('org_permid')['asset_tangibility']
        .agg(_first_non_null)
        .reset_index()
    )

    if verbose:
        print(f"  ✓ Issuer-year rows: {len(issuer_year)}")
        print(f"  ✓ Issuers with asset tangibility: {asset_map['asset_tangibility'].notna().sum()}")

    # Step 3: Merge issuer-year signals into panel (as-of by year)
    df['org_permid'] = pd.to_numeric(df['org_permid'], errors='coerce')
    df = df.merge(
        issuer_year,
        left_on=['org_permid', 'Year'],
        right_on=['org_permid', 'issue_year'],
        how='left'
    )
    df = df.drop(columns=['issue_year', 'issue_count', 'cumulative_issues'], errors='ignore')

    df = df.sort_values(['org_permid', 'Year'])
    for col in ['has_green_framework', 'issuer_track_record', 'prior_green_bonds']:
        if col in df.columns:
            df[col] = df.groupby('org_permid')[col].ffill()

    # Step 4: Merge asset tangibility (issuer-level)
    if 'asset_tangibility' in df.columns:
        df = df.merge(asset_map, on='org_permid', how='left', suffixes=('', '_issuer'))
        df['asset_tangibility'] = df['asset_tangibility'].fillna(df['asset_tangibility_issuer'])
        df = df.drop(columns=['asset_tangibility_issuer'], errors='ignore')
    else:
        df = df.merge(asset_map, on='org_permid', how='left')

    # Step 5: Fill defaults for controls and pre-issuance years
    df['has_green_framework'] = df['has_green_framework'].fillna(0).astype(int)
    df['issuer_track_record'] = df['issuer_track_record'].fillna(0).astype(int)
    df['prior_green_bonds'] = df['prior_green_bonds'].fillna(0).astype(int)
    df['asset_tangibility'] = df['asset_tangibility'].fillna(DEFAULT_TANGIBILITY)

    if verbose:
        print(f"  ✓ Merged into panel: {df.shape}")
        print("\nStep 5: Verification")
        psm_cols = ['has_green_framework', 'asset_tangibility', 'issuer_track_record', 'prior_green_bonds']
        for col in psm_cols:
            if col in df.columns:
                non_null = df[col].notna().sum()
                print(f"  ✓ {col:35s} - {non_null}/{len(df)} non-null")

    return df


def calculate_tobin_q(df: pd.DataFrame, winsorize: bool = True) -> pd.DataFrame:
    """
    Calculate Tobin's Q and add it to the panel data.
    
    Tobin's Q = (Market Value of Equity + Total Liabilities) / Total Assets
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with required financial columns.
    winsorize : bool, optional
        If True, cap Tobin's Q at 10 and remove negative values.
        
    Returns
    -------
    pd.DataFrame
        DataFrame with added 'Tobin_Q' column.
    """
    df_copy = df.copy()
    
    # Method 1: Using market_capitalization
    if 'market_capitalization' in df_copy.columns and 'total_liabilities' in df_copy.columns and 'total_assets' in df_copy.columns:
        df_copy['Tobin_Q'] = (df_copy['market_capitalization'] + df_copy['total_liabilities']) / df_copy['total_assets']
    # Method 2: Fallback to market_value
    elif 'market_value' in df_copy.columns and 'total_liabilities' in df_copy.columns and 'total_assets' in df_copy.columns:
        df_copy['Tobin_Q'] = (df_copy['market_value'] + df_copy['total_liabilities']) / df_copy['total_assets']
    else:
        # Warning if columns are missing
        print("Warning: Missing columns for Tobin's Q calculation")
        return df_copy

    if winsorize:
        # Remove negative values and cap at 10
        df_copy.loc[df_copy['Tobin_Q'] < 0, 'Tobin_Q'] = np.nan
        df_copy.loc[df_copy['Tobin_Q'] > 10, 'Tobin_Q'] = 10
        
    return df_copy


def normalize_psm_attributes(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """
    Normalize PSM attribute names to lowercase and ensure consistency.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with PSM attributes (any case)
    verbose : bool
        If True, print normalization messages
        
    Returns
    -------
    pd.DataFrame
        DataFrame with normalized lowercase column names
    """
    
    df = df.copy()
    
    # Mapping of possible column name variations to lowercase standard names
    psm_mappings = {
        'Has_Green_Framework': 'has_green_framework',
        'has_green_framework': 'has_green_framework',
        'Asset_Tangibility': 'asset_tangibility',
        'asset_tangibility': 'asset_tangibility',
        'Issuer_Track_Record': 'issuer_track_record',
        'issuer_track_record': 'issuer_track_record',
        'Prior_Green_Bonds': 'prior_green_bonds',
        'prior_green_bonds': 'prior_green_bonds',
    }
    
    # Rename columns
    rename_map = {}
    for old_name, new_name in psm_mappings.items():
        if old_name in df.columns and old_name != new_name:
            rename_map[old_name] = new_name
    
    if rename_map:
        df = df.rename(columns=rename_map)
        if verbose:
            print("Normalized PSM attribute names to lowercase:")
            for old, new in rename_map.items():
                print(f"  {old} → {new}")
    
    return df
