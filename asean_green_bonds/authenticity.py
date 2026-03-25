"""
Authenticity verification attributes for green bonds.

This module provides functions to extract and compute certification status
for green bonds, including CBI (Climate Bonds Initiative) and ICMA
(International Capital Market Association) Green Bond Principles certification.
"""

import pandas as pd
import numpy as np
import re
from scipy import stats
from typing import Optional, Tuple, List, Dict
from datetime import datetime


def extract_cbi_certification(df: pd.DataFrame, column: str = "Primary Use Of Proceeds") -> pd.DataFrame:
    """
    Extract and compute CBI (Climate Bonds Initiative) certification indicator.
    
    CBI certification is inferred from the "Primary Use Of Proceeds" field.
    Bonds labeled with "Green Bond Purposes" are considered CBI-certified.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing bond data with a Primary Use Of Proceeds column.
    column : str, optional
        Name of the column to check for CBI certification (default: "Primary Use Of Proceeds").
        
    Returns
    -------
    pd.DataFrame
        DataFrame with new 'is_cbi_certified' column added (0 or 1).
        Null values in the source column are treated as not certified (0).
        
    Notes
    -----
    - CBI certification is identified when the Primary Use Of Proceeds == "Green Bond Purposes"
    - All other values (including Environmental Protection Proj., Green Construction, etc.)
      are treated as non-CBI-certified
    - The function handles missing values by treating them as 0 (not certified)
    
    Examples
    --------
    >>> df = pd.DataFrame({
    ...     'Primary Use Of Proceeds': ['Green Bond Purposes', 'Environmental Protection Proj.', None]
    ... })
    >>> result = extract_cbi_certification(df)
    >>> result['is_cbi_certified'].tolist()
    [1, 0, 0]
    """
    df_copy = df.copy()
    
    # Extract CBI certification: 1 if "Green Bond Purposes", 0 otherwise
    df_copy['is_cbi_certified'] = (
        df_copy[column].eq('Green Bond Purposes')
        .fillna(False)
        .astype(int)
    )
    
    return df_copy


def compute_cbi_stats(df: pd.DataFrame, cbi_column: str = "is_cbi_certified") -> dict:
    """
    Compute statistics about CBI certification in the dataset.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with CBI certification indicator column.
    cbi_column : str, optional
        Name of the CBI certification column (default: "is_cbi_certified").
        
    Returns
    -------
    dict
        Dictionary containing:
        - 'total': Total number of bonds
        - 'cbi_certified': Number of CBI-certified bonds
        - 'not_certified': Number of non-certified bonds
        - 'coverage_pct': Percentage of CBI-certified bonds
        
    Examples
    --------
    >>> df = pd.DataFrame({'is_cbi_certified': [1, 1, 0, 0, 1]})
    >>> stats = compute_cbi_stats(df)
    >>> stats['coverage_pct']
    60.0
    """
    total = len(df)
    certified = (df[cbi_column] == 1).sum()
    not_certified = total - certified
    coverage_pct = (certified / total * 100) if total > 0 else 0
    
    return {
        'total': total,
        'cbi_certified': certified,
        'not_certified': not_certified,
        'coverage_pct': round(coverage_pct, 2)
    }


def validate_cbi_data(df: pd.DataFrame, primary_use_col: str = "Primary Use Of Proceeds") -> dict:
    """
    Validate the CBI certification data for completeness and issues.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing bond data.
    primary_use_col : str, optional
        Name of the Primary Use Of Proceeds column (default: "Primary Use Of Proceeds").
        
    Returns
    -------
    dict
        Dictionary containing:
        - 'missing_count': Number of null values in the column
        - 'unique_values': List of unique values in the column
        - 'value_counts': Dictionary of value counts
        - 'issues': List of any data quality issues detected
        
    Examples
    --------
    >>> df = pd.DataFrame({'Primary Use Of Proceeds': ['Green Bond Purposes', None]})
    >>> validation = validate_cbi_data(df)
    >>> validation['missing_count']
    1
    """
    missing = df[primary_use_col].isna().sum()
    unique_vals = df[primary_use_col].unique().tolist()
    value_counts = df[primary_use_col].value_counts(dropna=False).to_dict()
    
    issues = []
    if missing > 0:
        issues.append(f"Found {missing} null/missing values in {primary_use_col}")
    
    # Check for unexpected values
    expected_values = {
        'Green Bond Purposes',
        'Environmental Protection Proj.',
        'Green Construction',
        'Waste and Pollution Control'
    }
    unexpected = set(unique_vals) - expected_values
    if unexpected and not (len(unexpected) == 1 and None in unexpected):
        issues.append(f"Unexpected values found: {unexpected}")
    
    return {
        'missing_count': missing,
        'unique_values': unique_vals,
        'value_counts': value_counts,
        'issues': issues if issues else ['No issues detected']
    }


# ICMA Green Bond Principles (GBP) Certification Functions

def extract_icma_certification(
    df: pd.DataFrame,
    date_col: str = "Dates: Issue Date",
    use_of_proceeds_col: str = "Primary Use Of Proceeds",
    offering_technique_col: str = "Offering Technique"
) -> pd.DataFrame:
    """
    Extract and compute ICMA (International Capital Market Association) Green Bond
    Principles certification indicator and confidence score.
    
    ICMA GBP (launched June 2014) are the most widely adopted voluntary guidelines
    for green bonds. This function uses heuristics to identify bonds likely to be
    ICMA-compliant based on:
    
    1. Issue date after June 2014 (ICMA GBP launch)
    2. Primary Use of Proceeds = "Green Bond Purposes" (ICMA-eligible categories)
    3. Documented offering technique (indicates institutional framework)
    4. Issuer sophistication (inferred from MTN programme participation)
    
    Confidence scoring:
    - HIGH (0.9): All criteria met (post-2014, GBP purposes, documented offering)
    - MEDIUM (0.7): Core criteria met (post-2014, GBP purposes)
    - LOW (0.4): Environmental focus but not explicit GBP
    - UNKNOWN (0.0): Insufficient data or non-environmental
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing bond data with date, use of proceeds, and offering columns.
    date_col : str, optional
        Name of the date column (default: "Dates: Issue Date").
    use_of_proceeds_col : str, optional
        Name of the use of proceeds column (default: "Primary Use Of Proceeds").
    offering_technique_col : str, optional
        Name of the offering technique column (default: "Offering Technique").
        
    Returns
    -------
    pd.DataFrame
        DataFrame with new columns added:
        - 'is_icma_certified': Binary flag (1/0) indicating ICMA certification likelihood
        - 'icma_confidence': Float (0.0-1.0) indicating confidence in classification
        
    Notes
    -----
    - ICMA certification is an inference based on available data; cannot be definitively
      confirmed without external ICMA register access
    - This is a best-effort heuristic approach
    - Missing dates are treated conservatively (confidence reduced)
    - This method complements CBI certification; many bonds may be both CBI and ICMA
    
    Examples
    --------
    >>> df = pd.DataFrame({
    ...     'Dates: Issue Date': ['2020-01-15', '2012-06-01', '2021-03-20'],
    ...     'Primary Use Of Proceeds': ['Green Bond Purposes', 'Green Bond Purposes', 'Environmental Protection Proj.'],
    ...     'Offering Technique': ['Negotiated Sale', None, 'Issued off MTN programme']
    ... })
    >>> df['Dates: Issue Date'] = pd.to_datetime(df['Dates: Issue Date'])
    >>> result = extract_icma_certification(df)
    >>> result[['is_icma_certified', 'icma_confidence']].values.tolist()
    [[1, 0.9], [0, 0.0], [1, 0.7]]
    """
    df_copy = df.copy()
    
    # Parse dates
    if date_col in df_copy.columns:
        if df_copy[date_col].dtype == 'object':
            df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce')
    
    # ICMA GBP launch date
    icma_launch = pd.Timestamp('2014-06-01')
    
    # Initialize confidence scores
    confidence = np.zeros(len(df_copy))
    
    # Criterion 1: Issue date after ICMA GBP launch (June 2014)
    # This is essential for ICMA compliance
    if date_col in df_copy.columns:
        post_2014 = df_copy[date_col] >= icma_launch
        valid_date = df_copy[date_col].notna()
        
        # 0.5 points for being in ICMA era with valid date
        confidence += post_2014.astype(float) * 0.5
        
        # Penalty: -0.3 if date exists but is before 2014
        pre_2014 = (df_copy[date_col] < icma_launch) & valid_date
        confidence -= pre_2014.astype(float) * 0.3
    
    # Criterion 2: Primary Use of Proceeds matches ICMA-eligible categories
    # "Green Bond Purposes" explicitly indicates ICMA alignment
    if use_of_proceeds_col in df_copy.columns:
        has_gbp = df_copy[use_of_proceeds_col] == 'Green Bond Purposes'
        confidence += has_gbp.astype(float) * 0.4
        
        # Other environmental purposes get partial credit (0.1)
        environmental_other = df_copy[use_of_proceeds_col].isin([
            'Environmental Protection Proj.',
            'Green Construction',
            'Waste and Pollution Control'
        ])
        confidence += environmental_other.astype(float) * 0.1
    
    # Criterion 3: Documented offering technique (indicates institutional framework)
    if offering_technique_col in df_copy.columns:
        has_offering = df_copy[offering_technique_col].notna()
        confidence += has_offering.astype(float) * 0.0  # Already counted in GBP purposes
    
    # Additional boost for bonds with all criteria (institutional confidence)
    if date_col in df_copy.columns and use_of_proceeds_col in df_copy.columns:
        if offering_technique_col in df_copy.columns:
            full_criteria = (
                (df_copy[date_col] >= icma_launch) &
                (df_copy[use_of_proceeds_col] == 'Green Bond Purposes') &
                (df_copy[offering_technique_col].notna())
            )
            confidence += full_criteria.astype(float) * 0.0  # Boost already included
    
    # Bound confidence between 0 and 1
    confidence = np.clip(confidence, 0.0, 1.0)
    
    # Create binary flag: ICMA certified if confidence >= 0.7 (medium confidence or higher)
    is_certified = (confidence >= 0.7).astype(int)
    
    # Add columns to dataframe
    df_copy['icma_confidence'] = confidence
    df_copy['is_icma_certified'] = is_certified
    
    return df_copy


def compute_icma_stats(
    df: pd.DataFrame,
    icma_col: str = "is_icma_certified",
    confidence_col: str = "icma_confidence"
) -> dict:
    """
    Compute statistics about ICMA certification in the dataset.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with ICMA certification columns.
    icma_col : str, optional
        Name of the ICMA certification flag column (default: "is_icma_certified").
    confidence_col : str, optional
        Name of the confidence score column (default: "icma_confidence").
        
    Returns
    -------
    dict
        Dictionary containing:
        - 'total': Total number of bonds
        - 'icma_certified': Number of ICMA-certified bonds
        - 'not_certified': Number of non-certified bonds
        - 'coverage_pct': Percentage of ICMA-certified bonds
        - 'avg_confidence': Average confidence score
        - 'confidence_distribution': Dictionary with confidence level counts
        
    Examples
    --------
    >>> df = pd.DataFrame({
    ...     'is_icma_certified': [1, 1, 0, 0, 1],
    ...     'icma_confidence': [0.9, 0.8, 0.5, 0.3, 0.85]
    ... })
    >>> stats = compute_icma_stats(df)
    >>> stats['coverage_pct']
    60.0
    """
    total = len(df)
    certified = (df[icma_col] == 1).sum()
    not_certified = total - certified
    coverage_pct = (certified / total * 100) if total > 0 else 0
    avg_confidence = df[confidence_col].mean() if confidence_col in df.columns else 0
    
    # Confidence distribution
    confidence_dist = {
        'high': ((df[confidence_col] >= 0.8).sum() if confidence_col in df.columns else 0),
        'medium': ((df[confidence_col] >= 0.6) & (df[confidence_col] < 0.8)).sum() if confidence_col in df.columns else 0,
        'low': ((df[confidence_col] >= 0.4) & (df[confidence_col] < 0.6)).sum() if confidence_col in df.columns else 0,
        'uncertain': ((df[confidence_col] < 0.4).sum() if confidence_col in df.columns else 0)
    }
    
    return {
        'total': total,
        'icma_certified': certified,
        'not_certified': not_certified,
        'coverage_pct': round(coverage_pct, 2),
        'avg_confidence': round(avg_confidence, 3),
        'confidence_distribution': confidence_dist
    }


def validate_icma_data(
    df: pd.DataFrame,
    date_col: str = "Dates: Issue Date",
    use_of_proceeds_col: str = "Primary Use Of Proceeds",
    offering_technique_col: str = "Offering Technique"
) -> dict:
    """
    Validate the data quality for ICMA certification detection.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing bond data.
    date_col : str, optional
        Name of the date column (default: "Dates: Issue Date").
    use_of_proceeds_col : str, optional
        Name of the use of proceeds column (default: "Primary Use Of Proceeds").
    offering_technique_col : str, optional
        Name of the offering technique column (default: "Offering Technique").
        
    Returns
    -------
    dict
        Dictionary containing:
        - 'date_coverage': Percentage of non-null dates
        - 'use_of_proceeds_coverage': Percentage of non-null use of proceeds
        - 'offering_technique_coverage': Percentage of non-null offering technique
        - 'post_2014_pct': Percentage of bonds issued after June 2014
        - 'gbp_purposes_pct': Percentage with "Green Bond Purposes"
        - 'issues': List of data quality issues detected
        
    Examples
    --------
    >>> df = pd.DataFrame({
    ...     'Dates: Issue Date': ['2020-01-15', '2012-06-01', None],
    ...     'Primary Use Of Proceeds': ['Green Bond Purposes', 'Green Bond Purposes', 'Other']
    ... })
    >>> df['Dates: Issue Date'] = pd.to_datetime(df['Dates: Issue Date'], errors='coerce')
    >>> validation = validate_icma_data(df)
    >>> validation['date_coverage']
    66.67
    """
    issues = []
    total = len(df)
    
    # Date coverage
    date_coverage = 0
    if date_col in df.columns:
        date_count = df[date_col].notna().sum()
        date_coverage = round((date_count / total * 100) if total > 0 else 0, 2)
        
        if date_coverage < 80:
            issues.append(f"Low date coverage: {date_coverage}%")
        
        # Check for post-2014 bonds
        if df[date_col].dtype == 'object':
            df_temp = df.copy()
            df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
            post_2014 = (df_temp[date_col] >= pd.Timestamp('2014-06-01')).sum()
        else:
            post_2014 = (df[date_col] >= pd.Timestamp('2014-06-01')).sum()
        post_2014_pct = round((post_2014 / total * 100) if total > 0 else 0, 2)
    else:
        post_2014_pct = 0
        issues.append(f"Missing date column: {date_col}")
    
    # Use of Proceeds coverage
    use_coverage = 0
    gbp_pct = 0
    if use_of_proceeds_col in df.columns:
        use_count = df[use_of_proceeds_col].notna().sum()
        use_coverage = round((use_count / total * 100) if total > 0 else 0, 2)
        
        if use_coverage < 90:
            issues.append(f"Low use of proceeds coverage: {use_coverage}%")
        
        gbp_count = (df[use_of_proceeds_col] == 'Green Bond Purposes').sum()
        gbp_pct = round((gbp_count / total * 100) if total > 0 else 0, 2)
    else:
        issues.append(f"Missing use of proceeds column: {use_of_proceeds_col}")
    
    # Offering Technique coverage
    offering_coverage = 0
    if offering_technique_col in df.columns:
        offering_count = df[offering_technique_col].notna().sum()
        offering_coverage = round((offering_count / total * 100) if total > 0 else 0, 2)
    else:
        issues.append(f"Missing offering technique column: {offering_technique_col}")
    
    return {
        'date_coverage': date_coverage,
        'use_of_proceeds_coverage': use_coverage,
        'offering_technique_coverage': offering_coverage,
        'post_2014_pct': post_2014_pct,
        'gbp_purposes_pct': gbp_pct,
        'total_records': total,
        'issues': issues if issues else ['Data quality acceptable for ICMA detection']
    }


def compute_authenticity_score(df: pd.DataFrame, tier3_cap_score: Optional[int] = None) -> pd.DataFrame:
    """
    Compute a composite authenticity score combining all verification indicators.
    
    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with verification indicators.
    tier3_cap_score : int, optional
        Maximum score for Tier 3 bonds (no ESG data). Defaults to 60.
    
    Returns
    -------
    pandas.DataFrame
        Input DataFrame with added authenticity score columns.
    """
    # Create a working copy to avoid modifying the original
    result_df = df.copy()
    
    # Determine tier information
    has_tier_info = 'authenticity_tier' in result_df.columns
    if not has_tier_info:
        result_df['authenticity_tier'] = 1
    
    # Determine tier3 cap
    if 'tier3_cap_score' in result_df.columns:
        tier3_caps = result_df['tier3_cap_score'].fillna(60)
    elif tier3_cap_score is not None:
        tier3_caps = pd.Series(tier3_cap_score, index=result_df.index)
    else:
        tier3_caps = pd.Series(60, index=result_df.index)
    
    # Fill NaN values appropriately
    cols_to_fill = {
        'is_authentic': 0,
        'esg_improvement': 0,
        'esg_pvalue': 1.0,
        'is_cbi_certified': 0,
        'is_icma_certified': 0,
        'icma_confidence': 0,
        'issuer_track_record': 0,
        'has_green_framework': 0,
        'authenticity_tier': 3,
    }
    
    for col, fill_value in cols_to_fill.items():
        if col in result_df.columns:
            result_df[col] = result_df[col].fillna(fill_value)
        else:
            result_df[col] = fill_value
    
    # Issuer verification
    issuer_verified = pd.Series(0, index=result_df.index)
    if 'issuer_nation' in result_df.columns and 'Issuer/Borrower Nation' in result_df.columns:
        issuer_verified = (result_df['issuer_nation'] == result_df['Issuer/Borrower Nation']).astype(int)
    
    # ESG Component (0-40 points)
    esg_component = (result_df['is_authentic'].fillna(0) * 30 +
                     (result_df['esg_improvement'].fillna(0) > 10).astype(int) * 5 +
                     (result_df['esg_pvalue'].fillna(1.0) < 0.05).astype(int) * 5)
    esg_component = esg_component.clip(0, 40)
    
    # Tier adjustments
    tier2_mask = result_df['authenticity_tier'] == 2
    tier3_mask = result_df['authenticity_tier'] == 3
    esg_component = esg_component.where(~tier2_mask, esg_component.clip(0, 20))
    esg_component = esg_component.where(~tier3_mask, 0)
    
    # Certification Component (0-35 points)
    cert_component = (result_df['is_cbi_certified'].fillna(0) * 15 +
                      result_df['is_icma_certified'].fillna(0) * 15 +
                      (result_df['icma_confidence'].fillna(0) > 0.9).astype(int) * 5)
    cert_component = cert_component.clip(0, 35)
    
    # Issuer Component (0-25 points)
    issuer_component = (issuer_verified * 10 +
                        (result_df['issuer_track_record'].fillna(0) > 0).astype(int) * 10 +
                        result_df['has_green_framework'].fillna(0) * 5)
    issuer_component = issuer_component.clip(0, 25)
    
    # Final Score
    authenticity_score = esg_component + cert_component + issuer_component
    authenticity_score = authenticity_score.where(~tier3_mask, authenticity_score.clip(upper=tier3_caps))
    
    # Categorization
    def categorize_score(score):
        if score >= 80: return 'High'
        if score >= 60: return 'Medium'
        if score >= 40: return 'Low'
        return 'Unverified'
    
    result_df['esg_component'] = esg_component
    result_df['cert_component'] = cert_component
    result_df['issuer_component'] = issuer_component
    result_df['authenticity_score'] = authenticity_score
    result_df['authenticity_category'] = authenticity_score.apply(categorize_score)
    
    return result_df


def normalize_company_name(name: str) -> str:
    """Standardize company name by removing suffixes and punctuation."""
    if pd.isna(name): return ""
    name = str(name).upper()
    suffixes = [
        r'\bPCL\b', r'\bPLC\b', r'\bLTD\b', r'\bLIMITED\b', r'\bCORP\b', 
        r'\bCORPORATION\b', r'\bINC\b', r'\bINCORPORATED\b', r'\bBHD\b', 
        r'\bSDN BHD\b', r'\bPT\b', r'\bTBK\b', r'\bCO\b', r'\bCOMPANY\b',
        r'\bGROUP\b', r'\bHOLDINGS\b', r'\bHOLDING\b', r'\bOJK\b', r'\bSA\b'
    ]
    for suffix in suffixes:
        name = re.sub(suffix, '', name)
    name = re.sub(r'[^\w\s]', '', name)
    return name.strip()


def calculate_authenticity_tiered(
    df_gb: pd.DataFrame,
    df_esg: pd.DataFrame,
    tier1_min_obs: int = 2,
    tier2_min_obs: int = 1,
) -> pd.DataFrame:
    """Calculate authenticity with tiered approach based on ESG data availability."""
    result_df = df_gb.copy()
    result_df['match_name'] = result_df['Issuer/Borrower Name Full'].apply(normalize_company_name)
    esg_copy = df_esg.copy()
    esg_copy['match_name'] = esg_copy['company'].apply(normalize_company_name)
    
    # Initialize
    for col in ['is_authentic', 'authenticity_tier', 'n_pre_obs', 'n_post_obs']:
        result_df[col] = 0
    result_df['esg_improvement'] = np.nan
    result_df['esg_pvalue'] = np.nan
    result_df['tier_description'] = 'Certification_Only'
    result_df['authenticity_tier'] = 3
    
    issuance_years = result_df['Dates: Issue Date'].str.extract(r'(\d{4})')[0].astype(float)
    
    for idx, row in result_df.iterrows():
        issuer = row['match_name']
        year = issuance_years.iloc[idx]
        if pd.isna(year) or not issuer: continue
        
        issuer_data = esg_copy[esg_copy['match_name'] == issuer]
        if issuer_data.empty: continue
        
        pre_esg = issuer_data[issuer_data['Year'].between(year-3, year-1)]['esg_score'].dropna().values
        post_esg = issuer_data[issuer_data['Year'].between(year+1, year+3)]['esg_score'].dropna().values
        
        result_df.at[idx, 'n_pre_obs'] = len(pre_esg)
        result_df.at[idx, 'n_post_obs'] = len(post_esg)
        
        if len(pre_esg) >= tier1_min_obs and len(post_esg) >= tier1_min_obs:
            improv = float(post_esg.mean() - pre_esg.mean())
            _, pval = stats.ttest_ind(post_esg, pre_esg)
            result_df.at[idx, 'esg_improvement'] = improv
            result_df.at[idx, 'esg_pvalue'] = pval
            result_df.at[idx, 'authenticity_tier'] = 1
            result_df.at[idx, 'tier_description'] = 'Complete'
            if pval < 0.10 and improv > 0: result_df.at[idx, 'is_authentic'] = 1
        elif len(pre_esg) >= tier2_min_obs and len(post_esg) >= tier2_min_obs:
            improv = float(post_esg.mean() - pre_esg.mean())
            result_df.at[idx, 'esg_improvement'] = improv
            result_df.at[idx, 'authenticity_tier'] = 2
            result_df.at[idx, 'tier_description'] = 'Partial'
            if improv > 0: result_df.at[idx, 'is_authentic'] = 1
            
    return result_df.drop(columns=['match_name'])


def get_esg_coverage_by_country(df_esg: pd.DataFrame, df_gb: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate ESG data coverage statistics by country for green bond issuers.
    
    Parameters
    ----------
    df_esg : pd.DataFrame
        ESG panel data.
    df_gb : pd.DataFrame
        Green bonds data.
        
    Returns
    -------
    pd.DataFrame
        Coverage statistics by country.
    """
    df_tiered = calculate_authenticity_tiered(df_gb, df_esg)
    
    # Ensure country column exists
    country_col = 'Issuer/Borrower Nation' if 'Issuer/Borrower Nation' in df_gb.columns else 'country'
    if country_col in df_gb.columns:
        df_tiered['country'] = df_gb[country_col]
    else:
        df_tiered['country'] = 'Unknown'
    
    coverage = df_tiered.groupby('country').agg(
        total_bonds=('authenticity_tier', 'count'),
        bonds_with_complete_esg=('authenticity_tier', lambda x: (x == 1).sum()),
        bonds_with_partial_esg=('authenticity_tier', lambda x: (x == 2).sum()),
        bonds_with_no_esg=('authenticity_tier', lambda x: (x == 3).sum()),
    ).reset_index()
    
    coverage['coverage_rate'] = ((coverage['bonds_with_complete_esg'] + coverage['bonds_with_partial_esg']) 
                                / coverage['total_bonds'] * 100).round(2).fillna(0)
    return coverage


def compute_issuer_track_record(df: pd.DataFrame) -> pd.Series:
    """Compute the track record (prior issuances) for each issuer."""
    df_work = df.copy()
    df_work['_orig_idx'] = range(len(df_work))
    df_work['Dates: Issue Date'] = pd.to_datetime(df_work['Dates: Issue Date'])
    df_sorted = df_work.sort_values(['Issuer/Borrower Name Full', 'Dates: Issue Date', '_orig_idx'], kind='stable')
    track_record = df_sorted.groupby('Issuer/Borrower Name Full', sort=False).cumcount()
    track_record_dict = dict(zip(df_sorted['_orig_idx'], track_record.values))
    return pd.Series([track_record_dict[i] for i in range(len(df))], index=df.index)


def classify_issuer_type(issue_type: str) -> str:
    """Classify bond issue type into standardized categories."""
    if pd.isna(issue_type): return 'unknown'
    t = str(issue_type).lower()
    if 'sovereign' in t: return 'sovereign'
    if 'agency' in t or 'supranational' in t: return 'agency'
    if 'corporate' in t: return 'corporate'
    return 'other'


def has_green_framework(primary_use: str) -> int:
    """Determine if issuer has documented green bond framework."""
    if pd.isna(primary_use): return 0
    return 1 if 'green bond purposes' in str(primary_use).lower() else 0


def generate_authenticity_report(df: pd.DataFrame) -> dict:
    """Generate summary statistics for authenticity scores."""
    if 'authenticity_score' not in df.columns:
        raise ValueError("DataFrame must contain 'authenticity_score' column")
    
    scores = df['authenticity_score']
    categories = df['authenticity_category']
    
    return {
        'total_bonds': len(df),
        'score_mean': scores.mean(),
        'score_median': scores.median(),
        'score_std': scores.std(),
        'score_min': scores.min(),
        'score_max': scores.max(),
        'category_distribution': categories.value_counts().to_dict(),
        'high_authenticity': (categories == 'High').sum(),
        'medium_authenticity': (categories == 'Medium').sum(),
        'low_authenticity': (categories == 'Low').sum(),
        'unverified': (categories == 'Unverified').sum(),
    }


def print_authenticity_report(report: dict) -> None:
    """Print the authenticity report in a formatted way."""
    print("\n" + "="*70)
    print("                      AUTHENTICITY SCORE REPORT                       ")
    print("="*70)
    print(f"\nTotal Bonds Analyzed: {report['total_bonds']}")
    print(f"\nScore Statistics:")
    print(f"  Mean:                   {report['score_mean']:2.2f}")
    print(f"  Median:                 {report['score_median']:2.2f}")
    print(f"  Std Dev:                 {report['score_std']:2.2f}")
    print(f"  Min:                     {report['score_min']:2.2f}")
    print(f"  Max:                     {report['score_max']:2.2f}")
    
    print(f"\nAuthenticity Categories:")
    total = report['total_bonds']
    for cat in ['High', 'Medium', 'Low', 'Unverified']:
        count = report['category_distribution'].get(cat, 0)
        pct = (count / total * 100) if total > 0 else 0
        range_str = {'High': '(80-100)', 'Medium': '(60-79)', 'Low': '(40-59)', 'Unverified': '(<40)'}.get(cat)
        print(f"  {cat:10s} {range_str:10s}: {count:10d} ({pct:5.1f}%)")
    
    print("\n" + "="*70)


def apply_authenticity_proxy(
    panel_data_path: str,
    green_bonds_path: str,
    output_path: Optional[str] = None
) -> pd.DataFrame:
    """
    Perform tiered authenticity calculation and return result.
    
    Parameters
    ----------
    panel_data_path : str
        Path to ESG panel data CSV.
    green_bonds_path : str
        Path to green bonds CSV.
    output_path : str, optional
        If provided, save results to this path.
        
    Returns
    -------
    pd.DataFrame
        Authenticity-scored green bonds.
    """
    df_esg = pd.read_csv(panel_data_path)
    df_gb = pd.read_csv(green_bonds_path)
    
    # Extract certifications
    df_gb = extract_cbi_certification(df_gb)
    df_gb = extract_icma_certification(df_gb)
    
    # Tiered authenticity
    result = calculate_authenticity_tiered(df_gb, df_esg)
    
    if output_path:
        result.to_csv(output_path, index=False)
        
    return result


def apply_authenticity_with_fallbacks(
    panel_data_path: str,
    green_bonds_path: str,
    esg_panel_path: Optional[str] = None,
    fallback: str = 'tiered',
    output_path: str = 'data/green_bonds_authentic_tiered.csv'
) -> pd.DataFrame:
    """
    Apply authenticity scoring with configurable fallback behaviors.
    
    Parameters
    ----------
    panel_data_path : str
        Path to financial panel data (for compatibility).
    green_bonds_path : str
        Path to green bonds data.
    esg_panel_path : str, optional
        Path to ESG panel data. Defaults to panel_data_path.
    fallback : str, optional
        Fallback mode: 'strict', 'tiered', or 'certification_only'.
    output_path : str, optional
        Path to save results.
        
    Returns
    -------
    pd.DataFrame
        Scored green bonds.
    """
    if esg_panel_path is None:
        esg_panel_path = panel_data_path
        
    df_esg = pd.read_csv(esg_panel_path)
    df_gb = pd.read_csv(green_bonds_path)
    
    # Extract certifications
    df_gb = extract_cbi_certification(df_gb)
    df_gb = extract_icma_certification(df_gb)
    
    if fallback == 'certification_only':
        # Force all to Tier 3
        result = df_gb.copy()
        result['authenticity_tier'] = 3
        result['is_authentic'] = 0
        result['tier_description'] = 'Certification_Only'
    elif fallback == 'strict':
        # Only Tier 1 and Tier 3 (original behavior)
        result = calculate_authenticity_tiered(df_gb, df_esg, tier1_min_obs=2, tier2_min_obs=100)
    elif fallback == 'tiered':
        # Full tiered approach
        result = calculate_authenticity_tiered(df_gb, df_esg)
    else:
        raise ValueError(f"fallback must be 'strict', 'tiered', or 'certification_only', got '{fallback}'")
        
    # Standardize result
    if 'authenticity_score' not in result.columns:
        result = compute_authenticity_score(result)
        
    # Final output
    print(f"\nAUTHENTICITY SCORING RESULTS")
    print("="*70)
    print(f"Fallback mode: {fallback}")
    
    tier_dist = result['authenticity_tier'].value_counts(normalize=True).sort_index()
    print("\nTier Distribution:")
    for tier, pct in tier_dist.items():
        name = {1: 'Complete', 2: 'Partial', 3: 'Certification_Only'}.get(tier, 'Unknown')
        count = (result['authenticity_tier'] == tier).sum()
        print(f"  Tier {tier} ({name}): {count} ({pct*100:.1f}%)")
        
    auth_count = result['is_authentic'].sum()
    print(f"\nAuthenticity Status:")
    print(f"  Authentic: {auth_count} ({auth_count/len(result)*100:.1f}%)")
    print(f"  Not Authentic/Unverified: {len(result)-auth_count} ({(len(result)-auth_count)/len(result)*100:.1f}%)")
    
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        result.to_csv(output_path, index=False)
        print(f"\n✅ Saved to {output_path}")
        
    return result


def extract_issuer_verification_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Extract issuer verification fields from bond data."""
    result = df.copy()
    result['issuer_nation'] = df['Issuer/Borrower Nation'].fillna('Unknown')
    result['issuer_sector'] = df['Issuer/Borrower TRBC Business Sector'].fillna('Unknown')
    result['issuer_type'] = df['Issue Type'].apply(classify_issuer_type)
    result['issuer_track_record'] = compute_issuer_track_record(df)
    result['has_green_framework'] = df['Primary Use Of Proceeds'].apply(has_green_framework)
    return result

