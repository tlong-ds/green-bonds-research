"""
Composite Authenticity Score Module

This module computes a comprehensive authenticity score (0-100) by combining
multiple verification indicators with weighted components.

Scoring Methodology:
- ESG Divergence (40%): Most reliable - statistically significant improvement
- Certifications (35%): CBI and ICMA framework compliance
- Issuer Verification (25%): Issuer credibility and track record

Score Ranges:
- 80-100: High authenticity (robust verification across all indicators)
- 60-79: Medium authenticity (moderate verification)
- 40-59: Low authenticity (limited verification)
- 0-39: Unverified/uncertain (minimal verification indicators)
"""

import pandas as pd
import numpy as np


def compute_authenticity_score(df, tier3_cap_score: int = None):
    """
    Compute a composite authenticity score combining all verification indicators.
    
    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with the following required columns:
        - is_authentic: Binary flag (1=authentic, 0=not)
        - esg_improvement: ESG metric improvement (continuous)
        - esg_pvalue: Statistical p-value for ESG improvement (continuous)
        - is_cbi_certified: Binary flag (1=certified, 0=not)
        - is_icma_certified: Binary flag (1=certified, 0=not)
        - icma_confidence: Confidence score 0-1 for ICMA certification
        - issuer_nation: Issuer country (used for verification)
        - issuer_sector: Issuer sector (used for verification)
        - issuer_type: Issuer type (used for verification)
        - issuer_track_record: Track record indicator (binary or continuous)
        - has_green_framework: Binary flag (1=has framework, 0=not)
        
        Optional columns (for tiered scoring):
        - authenticity_tier: Tier assignment (1, 2, or 3)
        - tier3_cap_score: Per-row cap for Tier 3 bonds (overrides tier3_cap_score param)
    
    tier3_cap_score : int, optional
        Maximum score for Tier 3 bonds (no ESG data). If not provided,
        uses 'tier3_cap_score' column if present, otherwise defaults to 60.
    
    Returns
    -------
    pandas.DataFrame
        Input DataFrame with added columns:
        - esg_component: ESG divergence score (0-40)
        - cert_component: Certification score (0-35)
        - issuer_component: Issuer verification score (0-25)
        - authenticity_score: Final composite score (0-100)
        - authenticity_category: Category label (High/Medium/Low/Unverified)
        - authenticity_tier: Tier assignment (1, 2, or 3) - preserved if input
    
    Notes
    -----
    Missing values are treated as 0 (no verification). NaN values in boolean/flag
    columns are treated as False (0).
    
    Tiered Scoring Adjustments:
    - Tier 1 (Complete): Full score range (0-100)
    - Tier 2 (Partial): ESG component capped at 20 (instead of 40) due to lower confidence
    - Tier 3 (Certification Only): ESG component = 0, total score capped at tier3_cap_score
    """
    
    # Create a working copy to avoid modifying the original
    result_df = df.copy()
    
    # Determine tier information
    has_tier_info = 'authenticity_tier' in result_df.columns
    if not has_tier_info:
        # Default to Tier 1 (original behavior) if no tier info
        result_df['authenticity_tier'] = 1
    
    # Determine tier3 cap
    if 'tier3_cap_score' in result_df.columns:
        tier3_caps = result_df['tier3_cap_score'].fillna(60)
    elif tier3_cap_score is not None:
        tier3_caps = pd.Series(tier3_cap_score, index=result_df.index)
    else:
        tier3_caps = pd.Series(60, index=result_df.index)
    
    # Fill NaN values appropriately for each column
    cols_to_fill = {
        'is_authentic': 0,
        'esg_improvement': 0,
        'esg_pvalue': 1.0,  # High p-value = not significant
        'is_cbi_certified': 0,
        'is_icma_certified': 0,
        'icma_confidence': 0,
        'issuer_track_record': 0,
        'has_green_framework': 0
    }
    
    for col, fill_value in cols_to_fill.items():
        if col in result_df.columns:
            result_df[col] = result_df[col].fillna(fill_value)
    
    # Verify issuer verification: issuer nation must match
    # If issuer_nation is present and matches Issuer/Borrower Nation, count as verified
    issuer_verified = 0
    if 'issuer_nation' in result_df.columns and 'Issuer/Borrower Nation' in result_df.columns:
        issuer_verified = (result_df['issuer_nation'] == result_df['Issuer/Borrower Nation']).astype(int)
    else:
        issuer_verified = pd.Series([0] * len(result_df), index=result_df.index)
    
    # ========== ESG Component (0-40 points) ==========
    esg_component = pd.Series(0, index=result_df.index, dtype=float)
    
    # Base: is_authentic = 1: +30 points
    esg_component += result_df['is_authentic'].fillna(0) * 30
    
    # Bonus: esg_improvement > 10: +5 points
    esg_component += (result_df['esg_improvement'].fillna(0) > 10).astype(int) * 5
    
    # Bonus: esg_pvalue < 0.05: +5 points
    esg_component += (result_df['esg_pvalue'].fillna(1.0) < 0.05).astype(int) * 5
    
    # Cap at 40 points
    esg_component = esg_component.clip(0, 40)
    
    # Apply tier adjustments to ESG component:
    # - Tier 2: Cap ESG component at 20 (lower confidence)
    # - Tier 3: Set ESG component to 0 (no ESG data)
    tier2_mask = result_df['authenticity_tier'] == 2
    tier3_mask = result_df['authenticity_tier'] == 3
    
    esg_component = esg_component.where(~tier2_mask, esg_component.clip(0, 20))
    esg_component = esg_component.where(~tier3_mask, 0)
    
    # ========== Certification Component (0-35 points) ==========
    cert_component = pd.Series(0, index=result_df.index, dtype=float)
    
    # CBI certification: +15 points
    cert_component += result_df['is_cbi_certified'].fillna(0) * 15
    
    # ICMA certification: +15 points
    cert_component += result_df['is_icma_certified'].fillna(0) * 15
    
    # ICMA confidence bonus: icma_confidence > 0.9: +5 points
    cert_component += (result_df['icma_confidence'].fillna(0) > 0.9).astype(int) * 5
    
    # Cap at 35 points
    cert_component = cert_component.clip(0, 35)
    
    # ========== Issuer Component (0-25 points) ==========
    issuer_component = pd.Series(0, index=result_df.index, dtype=float)
    
    # Issuer verified: +10 points
    issuer_component += issuer_verified * 10
    
    # Issuer track record: +10 points (if > 0)
    issuer_component += (result_df['issuer_track_record'].fillna(0) > 0).astype(int) * 10
    
    # Has green framework: +5 points
    issuer_component += result_df['has_green_framework'].fillna(0) * 5
    
    # Cap at 25 points
    issuer_component = issuer_component.clip(0, 25)
    
    # ========== Final Score ==========
    authenticity_score = esg_component + cert_component + issuer_component
    
    # Apply tier3 cap: Tier 3 bonds cannot exceed their cap score
    # This ensures certification-only bonds have bounded authenticity
    tier3_mask = result_df['authenticity_tier'] == 3
    authenticity_score = authenticity_score.where(
        ~tier3_mask, 
        authenticity_score.clip(upper=tier3_caps)
    )
    
    # Create category labels
    def categorize_score(score):
        if score >= 80:
            return 'High'
        elif score >= 60:
            return 'Medium'
        elif score >= 40:
            return 'Low'
        else:
            return 'Unverified'
    
    authenticity_category = authenticity_score.apply(categorize_score)
    
    # Add all new columns to result
    result_df['esg_component'] = esg_component
    result_df['cert_component'] = cert_component
    result_df['issuer_component'] = issuer_component
    result_df['authenticity_score'] = authenticity_score
    result_df['authenticity_category'] = authenticity_category
    
    return result_df


def generate_authenticity_report(df):
    """
    Generate summary statistics for the authenticity scores.
    
    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with authenticity_score and authenticity_category columns
    
    Returns
    -------
    dict
        Dictionary containing summary statistics
    """
    
    if 'authenticity_score' not in df.columns:
        raise ValueError("DataFrame must contain 'authenticity_score' column")
    
    scores = df['authenticity_score']
    categories = df['authenticity_category']
    
    report = {
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
    
    return report


def print_authenticity_report(report):
    """
    Pretty-print authenticity report.
    
    Parameters
    ----------
    report : dict
        Report dictionary from generate_authenticity_report
    """
    
    print("\n" + "=" * 70)
    print("AUTHENTICITY SCORE REPORT".center(70))
    print("=" * 70)
    
    print(f"\nTotal Bonds Analyzed: {report['total_bonds']}")
    print(f"\nScore Statistics:")
    print(f"  Mean:                {report['score_mean']:>8.2f}")
    print(f"  Median:              {report['score_median']:>8.2f}")
    print(f"  Std Dev:             {report['score_std']:>8.2f}")
    print(f"  Min:                 {report['score_min']:>8.2f}")
    print(f"  Max:                 {report['score_max']:>8.2f}")
    
    print(f"\nAuthenticity Categories:")
    print(f"  High (80-100):       {report['high_authenticity']:>4} ({report['high_authenticity']/report['total_bonds']*100:>5.1f}%)")
    print(f"  Medium (60-79):      {report['medium_authenticity']:>4} ({report['medium_authenticity']/report['total_bonds']*100:>5.1f}%)")
    print(f"  Low (40-59):         {report['low_authenticity']:>4} ({report['low_authenticity']/report['total_bonds']*100:>5.1f}%)")
    print(f"  Unverified (<40):    {report['unverified']:>4} ({report['unverified']/report['total_bonds']*100:>5.1f}%)")
    
    print("\n" + "=" * 70)


if __name__ == '__main__':
    # Example usage
    print("Loading authenticity data...")
    
    # Load base data with ESG divergence
    esg_auth = pd.read_csv('data/green_bonds_authentic.csv')
    
    # Load ICMA certification data
    icma_cert = pd.read_csv('processed_data/bonds_with_icma_certification.csv')
    
    # Load issuer verification data
    issuer_verify = pd.read_csv('data/green_bonds_with_issuer_fields.csv')
    
    # Merge all data on Deal PermID
    merged_df = esg_auth[['Deal PermID', 'Issuer/Borrower Name Full', 'Issuer/Borrower Nation', 
                           'is_authentic', 'esg_improvement', 'esg_pvalue']].copy()
    
    merged_df = merged_df.merge(
        icma_cert[['Deal PermID', 'is_cbi_certified', 'is_icma_certified', 'icma_confidence']],
        on='Deal PermID',
        how='left'
    )
    
    merged_df = merged_df.merge(
        issuer_verify[['Deal PermID', 'issuer_nation', 'issuer_sector', 'issuer_type', 
                       'issuer_track_record', 'has_green_framework']],
        on='Deal PermID',
        how='left'
    )
    
    # Compute authenticity scores
    print("Computing authenticity scores...")
    result_df = compute_authenticity_score(merged_df)
    
    # Generate report
    report = generate_authenticity_report(result_df)
    print_authenticity_report(report)
    
    # Show top bonds by authenticity score
    print("\nTop 10 Bonds by Authenticity Score:")
    print("=" * 70)
    top_bonds = result_df.nlargest(10, 'authenticity_score')[
        ['Issuer/Borrower Name Full', 'authenticity_score', 'authenticity_category']
    ]
    for idx, row in top_bonds.iterrows():
        print(f"  {row['Issuer/Borrower Name Full'][:40]:40} | Score: {row['authenticity_score']:6.1f} | {row['authenticity_category']}")
    
    # Show bottom bonds
    print("\nBottom 10 Bonds by Authenticity Score:")
    print("=" * 70)
    bottom_bonds = result_df.nsmallest(10, 'authenticity_score')[
        ['Issuer/Borrower Name Full', 'authenticity_score', 'authenticity_category']
    ]
    for idx, row in bottom_bonds.iterrows():
        print(f"  {row['Issuer/Borrower Name Full'][:40]:40} | Score: {row['authenticity_score']:6.1f} | {row['authenticity_category']}")
    
    # Save output CSV
    output_path = 'data/green_bonds_with_authenticity_score.csv'
    result_df.to_csv(output_path, index=False)
    print(f"\n✓ Results saved to {output_path}")
    print(f"  Total records: {len(result_df)}")
    print(f"  Columns: {result_df.shape[1]}")
