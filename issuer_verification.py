"""
Issuer Verification Fields Extraction Module

This module provides functions to extract and prepare issuer verification attributes
from bond data to support authenticity verification.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple


def compute_issuer_track_record(df: pd.DataFrame) -> pd.Series:
    """
    Compute the track record (prior issuances) for each issuer.
    
    This counts the cumulative number of green bond issuances per issuer,
    where each bond's track record is the count of all prior bonds by that issuer
    (sorted by issue date). Bonds issued on the same date are ordered by their
    original position in the DataFrame.
    
    Args:
        df: DataFrame with 'Issuer/Borrower Name Full' and 'Dates: Issue Date' columns
        
    Returns:
        pd.Series: issuer_track_record values indexed by original df index
    """
    df_work = df.copy()
    df_work['_orig_idx'] = range(len(df_work))
    df_work['Dates: Issue Date'] = pd.to_datetime(df_work['Dates: Issue Date'])
    
    # Sort by issuer, date, and original index for stable ordering
    df_sorted = df_work.sort_values(
        ['Issuer/Borrower Name Full', 'Dates: Issue Date', '_orig_idx'],
        kind='stable'
    )
    
    # Count cumulative issuances per issuer (cumcount gives 0 for first, 1 for second, etc.)
    track_record = df_sorted.groupby('Issuer/Borrower Name Full', sort=False).cumcount()
    
    # Map back to original index positions
    track_record_dict = dict(zip(df_sorted['_orig_idx'], track_record.values))
    result = pd.Series([track_record_dict[i] for i in range(len(df))], index=df.index)
    
    return result


def classify_issuer_type(issue_type: str) -> str:
    """
    Classify bond issue type into standardized categories.
    
    Args:
        issue_type: Raw issue type from data
        
    Returns:
        str: Standardized issuer type (sovereign, corporate, agency, or other)
    """
    if pd.isna(issue_type):
        return 'unknown'
    
    issue_type_lower = str(issue_type).lower()
    
    # Check for sovereign
    if 'sovereign' in issue_type_lower:
        return 'sovereign'
    
    # Check for agency/supranational
    if 'agency' in issue_type_lower or 'supranational' in issue_type_lower:
        return 'agency'
    
    # Check for corporate variants
    if 'corporate' in issue_type_lower:
        return 'corporate'
    
    return 'other'


def has_green_framework(primary_use: str) -> int:
    """
    Determine if issuer has documented green bond framework.
    
    Assumes "Green Bond Purposes" indicates framework existence.
    
    Args:
        primary_use: Primary use of proceeds value
        
    Returns:
        int: 1 if framework exists, 0 otherwise
    """
    if pd.isna(primary_use):
        return 0
    
    primary_use_str = str(primary_use).lower()
    return 1 if 'green bond purposes' in primary_use_str else 0


def extract_issuer_verification_fields(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract issuer verification fields from bond data.
    
    This function adds the following fields to the input DataFrame:
    - issuer_nation: Country of issuer (from Issuer/Borrower Nation)
    - issuer_sector: TRBC Business Sector classification
    - issuer_type: Standardized bond type (sovereign, corporate, agency, other)
    - issuer_track_record: Cumulative count of prior green bond issuances by issuer
    - has_green_framework: Binary indicator (1/0) of documented green bond framework
    
    Args:
        df: DataFrame with bond data containing columns:
            - Issuer/Borrower Nation
            - Issuer/Borrower TRBC Business Sector
            - Issue Type
            - Issuer/Borrower Name Full
            - Dates: Issue Date
            - Primary Use Of Proceeds
            
    Returns:
        pd.DataFrame: Input DataFrame with new issuer verification columns added
        
    Raises:
        ValueError: If required columns are missing from input DataFrame
    """
    result = df.copy()
    
    # Verify required columns
    required_cols = [
        'Issuer/Borrower Nation',
        'Issuer/Borrower TRBC Business Sector',
        'Issue Type',
        'Issuer/Borrower Name Full',
        'Dates: Issue Date',
        'Primary Use Of Proceeds'
    ]
    
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Extract issuer_nation
    result['issuer_nation'] = df['Issuer/Borrower Nation'].fillna('Unknown')
    
    # Extract issuer_sector
    result['issuer_sector'] = df['Issuer/Borrower TRBC Business Sector'].fillna('Unknown')
    
    # Extract and classify issuer_type
    result['issuer_type'] = df['Issue Type'].apply(classify_issuer_type)
    
    # Compute issuer_track_record
    result['issuer_track_record'] = compute_issuer_track_record(df)
    
    # Extract has_green_framework
    result['has_green_framework'] = df['Primary Use Of Proceeds'].apply(has_green_framework)
    
    return result


def validate_issuer_fields(df: pd.DataFrame) -> Dict[str, any]:
    """
    Validate extracted issuer verification fields for data quality.
    
    Args:
        df: DataFrame with extracted issuer verification fields
        
    Returns:
        dict: Validation report with statistics and potential issues
    """
    report = {}
    
    fields = ['issuer_nation', 'issuer_sector', 'issuer_type', 'issuer_track_record', 'has_green_framework']
    
    for field in fields:
        if field not in df.columns:
            report[field] = {'status': 'missing', 'error': f'Column {field} not found'}
            continue
        
        col_data = df[field]
        report[field] = {
            'status': 'ok',
            'total_records': len(col_data),
            'non_null': col_data.notna().sum(),
            'null_count': col_data.isna().sum(),
            'null_pct': round((col_data.isna().sum() / len(col_data)) * 100, 2),
            'unique_values': col_data.nunique(),
        }
        
        if field == 'issuer_track_record':
            report[field].update({
                'min': int(col_data.min()),
                'max': int(col_data.max()),
                'mean': round(col_data.mean(), 2),
                'median': int(col_data.median()),
            })
        elif field == 'has_green_framework':
            report[field]['value_counts'] = col_data.value_counts().to_dict()
    
    return report


def generate_field_statistics(df: pd.DataFrame) -> Dict[str, any]:
    """
    Generate detailed statistics on extracted issuer fields.
    
    Args:
        df: DataFrame with extracted issuer verification fields
        
    Returns:
        dict: Detailed statistics for each field
    """
    stats = {}
    
    # issuer_nation statistics
    if 'issuer_nation' in df.columns:
        stats['issuer_nation'] = {
            'unique_nations': df['issuer_nation'].nunique(),
            'top_nations': df['issuer_nation'].value_counts().head(10).to_dict(),
        }
    
    # issuer_sector statistics
    if 'issuer_sector' in df.columns:
        stats['issuer_sector'] = {
            'unique_sectors': df['issuer_sector'].nunique(),
            'top_sectors': df['issuer_sector'].value_counts().head(10).to_dict(),
        }
    
    # issuer_type statistics
    if 'issuer_type' in df.columns:
        stats['issuer_type'] = {
            'unique_types': df['issuer_type'].nunique(),
            'type_distribution': df['issuer_type'].value_counts().to_dict(),
        }
    
    # issuer_track_record statistics
    if 'issuer_track_record' in df.columns:
        stats['issuer_track_record'] = {
            'mean': round(df['issuer_track_record'].mean(), 2),
            'median': int(df['issuer_track_record'].median()),
            'min': int(df['issuer_track_record'].min()),
            'max': int(df['issuer_track_record'].max()),
            'std': round(df['issuer_track_record'].std(), 2),
            'distribution': df['issuer_track_record'].value_counts().sort_index().to_dict(),
        }
    
    # has_green_framework statistics
    if 'has_green_framework' in df.columns:
        total = len(df)
        with_framework = (df['has_green_framework'] == 1).sum()
        stats['has_green_framework'] = {
            'total_issuers': total,
            'with_framework': with_framework,
            'without_framework': total - with_framework,
            'pct_with_framework': round((with_framework / total) * 100, 2),
        }
    
    return stats
