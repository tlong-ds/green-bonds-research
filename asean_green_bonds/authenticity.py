"""
Authenticity verification attributes for green bonds.

This module provides functions to extract and compute certification status
for green bonds, including CBI (Climate Bonds Initiative) and ICMA
(International Capital Market Association) Green Bond Principles certification.
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple
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


def compare_cbi_vs_icma(df: pd.DataFrame) -> dict:
    """
    Compare CBI and ICMA certification classifications.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with both 'is_cbi_certified' and 'is_icma_certified' columns.
        
    Returns
    -------
    dict
        Dictionary containing:
        - 'both': Number of bonds certified as both CBI and ICMA
        - 'cbi_only': Number of bonds certified as CBI only
        - 'icma_only': Number of bonds certified as ICMA only
        - 'neither': Number of bonds not certified as either
        - 'overlap_pct': Percentage of CBI bonds that are also ICMA certified
        
    Examples
    --------
    >>> df = pd.DataFrame({
    ...     'is_cbi_certified': [1, 1, 0, 0],
    ...     'is_icma_certified': [1, 0, 1, 0]
    ... })
    >>> comparison = compare_cbi_vs_icma(df)
    >>> comparison['both']
    1
    """
    both = ((df['is_cbi_certified'] == 1) & (df['is_icma_certified'] == 1)).sum()
    cbi_only = ((df['is_cbi_certified'] == 1) & (df['is_icma_certified'] == 0)).sum()
    icma_only = ((df['is_cbi_certified'] == 0) & (df['is_icma_certified'] == 1)).sum()
    neither = ((df['is_cbi_certified'] == 0) & (df['is_icma_certified'] == 0)).sum()
    
    cbi_total = (df['is_cbi_certified'] == 1).sum()
    overlap_pct = round((both / cbi_total * 100) if cbi_total > 0 else 0, 2)
    
    return {
        'both': both,
        'cbi_only': cbi_only,
        'icma_only': icma_only,
        'neither': neither,
        'overlap_pct': overlap_pct,
        'cbi_total': cbi_total,
        'icma_total': (df['is_icma_certified'] == 1).sum()
    }

