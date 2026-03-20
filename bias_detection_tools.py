
import pandas as pd
import numpy as np

def detect_survivorship_bias(panel_data_path):
    """
    Identifies potential survivorship bias by finding firms that disappear 
    before the end of the sample period (2025).
    """
    df = pd.read_csv(panel_data_path)
    
    # Check for firms that have data in early years but NONE in recent years
    # We'll use 'total_assets' as a proxy for 'existence'
    recent_years = [2023, 2024, 2025]
    early_years = [2015, 2016, 2017]
    
    existence = df.groupby('ticker').apply(lambda x: pd.Series({
        'has_early_data': x[x['Year'].isin(early_years)]['total_assets'].notna().any(),
        'has_recent_data': x[x['Year'].isin(recent_years)]['total_assets'].notna().any(),
        'last_year_with_data': x[x['total_assets'].notna()]['Year'].max()
    }))
    
    # Potential delisted/inactive firms
    potential_dead_firms = existence[(existence['has_early_data']) & (~existence['has_recent_data'])]
    
    print(f"Found {len(potential_dead_firms)} firms that may have been delisted/merged (Survivorship Bias).")
    return potential_dead_firms

import re

def normalize_company_name(name):
    if pd.isna(name):
        return ""
    name = str(name).upper()
    # Remove common corporate suffixes and punctuation
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

def apply_authenticity_proxy(panel_data_path, green_bonds_path, esg_panel_path=None):
    """
    IMPROVED: Applies the ESG Divergence Method to proxy green bond authenticity.
    Creates an 'is_authentic' flag. 1 = Authentic, 0 = Greenwashing/Unverified.
    
    ENHANCEMENTS:
    - Statistical significance testing (t-test on ESG improvement)
    - Pre/Post window with reporting lag adjustment
    - Alternative definitions (environmental commitment signals)
    - Data quality tracking for transparency
    
    Args:
        panel_data_path: Path to panel data (financial metrics)
        green_bonds_path: Path to green bonds universe
        esg_panel_path: Path to ESG panel data (if separate from panel_data)
    """
    from scipy import stats
    
    df_panel = pd.read_csv(panel_data_path)
    df_gb = pd.read_csv(green_bonds_path)
    
    # Use ESG panel if provided, otherwise use panel_data
    if esg_panel_path:
        df_esg = pd.read_csv(esg_panel_path)
    else:
        df_esg = df_panel.copy()
    
    # Standardize names for matching using normalization
    df_gb['match_name'] = df_gb['Issuer/Borrower Name Full'].apply(normalize_company_name)
    df_esg['match_name'] = df_esg['company'].apply(normalize_company_name)
    
    # Initialize columns
    df_gb['is_authentic'] = 0  # Default to 0
    df_gb['esg_improvement'] = np.nan
    df_gb['esg_pvalue'] = np.nan
    df_gb['n_pre_obs'] = 0
    df_gb['n_post_obs'] = 0
    df_gb['data_quality'] = 'insufficient_data'
    
    df_gb['issuance_year'] = df_gb['Dates: Issue Date'].str.extract(r'(\d{4})')[0].astype(float)
    
    print("\nIMPROVED AUTHENTICITY PROXY: ESG Divergence Method")
    print("="*70)
    print("Testing ESG improvement with statistical significance (p < 0.10)\n")
    
    for idx, row in df_gb.iterrows():
        issuer = row['match_name']
        issuance_year = row['issuance_year']
        
        if pd.isna(issuance_year) or not issuer:
            continue
            
        issuer_data = df_esg[df_esg['match_name'] == issuer].copy()
        if issuer_data.empty: 
            # Try a partial match if exact normalized match fails
            partial_matches = df_esg[df_esg['match_name'].str.contains(issuer, na=False, regex=False)]
            if partial_matches.empty:
                continue
            issuer_data = partial_matches
        
        # IMPROVED: Use 1-year lag for pre/post (ESG reports lag by ~6-12 months)
        # Pre-issuance window: [t-3, t-1]
        # Post-issuance window: [t+1, t+3]
        pre_window_years = [y for y in range(int(issuance_year)-3, int(issuance_year)-1)]
        post_window_years = [y for y in range(int(issuance_year)+1, int(issuance_year)+4)]
        
        pre_data = issuer_data[issuer_data['Year'].isin(pre_window_years)]
        post_data = issuer_data[issuer_data['Year'].isin(post_window_years)]
        
        # Extract ESG scores with proper handling
        pre_esg = pre_data['esg_score'].dropna().values
        post_esg = post_data['esg_score'].dropna().values
        
        df_gb.at[idx, 'n_pre_obs'] = len(pre_esg)
        df_gb.at[idx, 'n_post_obs'] = len(post_esg)
        
        # IMPROVED: Only flag as authentic if:
        # 1. We have sufficient pre and post data
        # 2. ESG improvement is statistically significant (p < 0.10)
        # 3. ESG improvement is positive
        
        if len(pre_esg) >= 2 and len(post_esg) >= 2:
            esg_improvement = post_esg.mean() - pre_esg.mean()
            
            # Statistical significance test (independent samples t-test)
            t_stat, p_value = stats.ttest_ind(post_esg, pre_esg)
            
            df_gb.at[idx, 'esg_improvement'] = esg_improvement
            df_gb.at[idx, 'esg_pvalue'] = p_value
            df_gb.at[idx, 'data_quality'] = 'complete'
            
            # AUTHENTICITY CRITERION: p < 0.10 AND positive improvement
            if p_value < 0.10 and esg_improvement > 0:
                df_gb.at[idx, 'is_authentic'] = 1
        else:
            df_gb.at[idx, 'data_quality'] = 'insufficient_esg_data'
    
    # Clean up temporary columns
    df_gb = df_gb.drop(columns=['match_name', 'issuance_year'])
    
    # Save output
    output_path = 'data/green_bonds_authentic.csv'
    df_gb.to_csv(output_path, index=False)
    
    # Print summary statistics
    authentic_count = df_gb['is_authentic'].sum()
    total_count = len(df_gb)
    complete_data = (df_gb['data_quality'] == 'complete').sum()
    
    print(f"\n✅ RESULTS:")
    print(f"   Total bonds: {total_count}")
    print(f"   With complete ESG data: {complete_data} ({100*complete_data/total_count:.1f}%)")
    print(f"   Flagged as Authentic: {authentic_count} ({100*authentic_count/total_count:.1f}%)")
    print(f"   Flagged as Greenwashing/Unverified: {total_count - authentic_count} ({100*(total_count-authentic_count)/total_count:.1f}%)")
    
    if complete_data > 0:
        authentic_subset = df_gb[df_gb['data_quality'] == 'complete']
        print(f"\n   Among bonds with complete data:")
        print(f"     Mean ESG improvement (all): {authentic_subset['esg_improvement'].mean():.3f} pts")
        print(f"     Mean ESG improvement (authentic only): {authentic_subset[authentic_subset['is_authentic']==1]['esg_improvement'].mean():.3f} pts")
        print(f"     Median p-value (all): {authentic_subset['esg_pvalue'].median():.4f}")
    
    print(f"\n✅ Saved to {output_path}")
    print(f"\nNOTE: Use 'is_authentic == 1' to filter for treated group (or 'data_quality == complete' for sensitivity)")
    
    return df_gb

def calculate_authenticity_tiered(
    df_gb: pd.DataFrame,
    df_esg: pd.DataFrame,
    tier1_min_obs: int = 2,
    tier2_min_obs: int = 1,
    tier3_cap_score: int = 60,
) -> pd.DataFrame:
    """
    Calculate authenticity with tiered approach based on ESG data availability.
    
    Tiers:
    - Tier 1 (Complete): ≥tier1_min_obs pre AND post → t-test method, full score range
    - Tier 2 (Partial): ≥tier2_min_obs pre AND post → point estimate, capped confidence
    - Tier 3 (Certification only): No ESG data → CBI/ICMA flags only, capped at tier3_cap_score
    
    Parameters
    ----------
    df_gb : pd.DataFrame
        Green bonds data with certification flags. Must contain:
        - 'Issuer/Borrower Name Full': Issuer name for matching
        - 'Dates: Issue Date': Issuance date (YYYY format extractable)
        - Optional: 'is_cbi_certified', 'is_icma_certified' for Tier 3
    df_esg : pd.DataFrame
        ESG panel data. Must contain:
        - 'company': Company name for matching
        - 'Year': Year of observation
        - 'esg_score': ESG score value
    tier1_min_obs : int, default=2
        Minimum pre/post observations for Tier 1 (full statistical test)
    tier2_min_obs : int, default=1
        Minimum pre/post observations for Tier 2 (point estimate)
    tier3_cap_score : int, default=60
        Maximum authenticity score for Tier 3 bonds (no ESG data)
    
    Returns
    -------
    pd.DataFrame
        Copy of df_gb with added columns:
        - is_authentic: Binary (1 if statistically significant improvement or positive for Tier 2)
        - esg_improvement: Numeric improvement (post - pre mean)
        - esg_pvalue: p-value from t-test (Tier 1 only, NaN for others)
        - authenticity_tier: 1, 2, or 3
        - tier_description: 'Complete', 'Partial', or 'Certification_Only'
        - data_quality_notes: Details about data availability
        - n_pre_obs: Number of pre-issuance observations
        - n_post_obs: Number of post-issuance observations
    """
    from scipy import stats
    
    result_df = df_gb.copy()
    
    # Standardize names for matching
    result_df['match_name'] = result_df['Issuer/Borrower Name Full'].apply(normalize_company_name)
    df_esg = df_esg.copy()
    df_esg['match_name'] = df_esg['company'].apply(normalize_company_name)
    
    # Initialize output columns
    result_df['is_authentic'] = 0
    result_df['esg_improvement'] = np.nan
    result_df['esg_pvalue'] = np.nan
    result_df['authenticity_tier'] = 3  # Default to Tier 3
    result_df['tier_description'] = 'Certification_Only'
    result_df['data_quality_notes'] = 'No ESG data available'
    result_df['n_pre_obs'] = 0
    result_df['n_post_obs'] = 0
    
    # Extract issuance year
    result_df['_issuance_year'] = result_df['Dates: Issue Date'].str.extract(r'(\d{4})')[0].astype(float)
    
    # Early exit if no ESG data at all
    if df_esg.empty:
        result_df = result_df.drop(columns=['match_name', '_issuance_year'])
        return result_df
    
    for idx, row in result_df.iterrows():
        issuer = row['match_name']
        issuance_year = row['_issuance_year']
        
        if pd.isna(issuance_year) or not issuer:
            continue
        
        # Find issuer ESG data
        issuer_data = df_esg[df_esg['match_name'] == issuer].copy()
        if issuer_data.empty:
            # Try partial match
            partial_matches = df_esg[df_esg['match_name'].str.contains(issuer, na=False, regex=False)]
            if partial_matches.empty:
                continue
            issuer_data = partial_matches
        
        # Define pre/post windows (with 1-year lag adjustment)
        pre_window_years = list(range(int(issuance_year) - 3, int(issuance_year)))
        post_window_years = list(range(int(issuance_year) + 1, int(issuance_year) + 4))
        
        pre_data = issuer_data[issuer_data['Year'].isin(pre_window_years)]
        post_data = issuer_data[issuer_data['Year'].isin(post_window_years)]
        
        pre_esg = pre_data['esg_score'].dropna().values
        post_esg = post_data['esg_score'].dropna().values
        
        n_pre = len(pre_esg)
        n_post = len(post_esg)
        
        result_df.at[idx, 'n_pre_obs'] = n_pre
        result_df.at[idx, 'n_post_obs'] = n_post
        
        # Tier 1: Complete data - statistical testing
        if n_pre >= tier1_min_obs and n_post >= tier1_min_obs:
            esg_improvement = float(post_esg.mean() - pre_esg.mean())
            t_stat, p_value = stats.ttest_ind(post_esg, pre_esg)
            
            result_df.at[idx, 'esg_improvement'] = esg_improvement
            result_df.at[idx, 'esg_pvalue'] = p_value
            result_df.at[idx, 'authenticity_tier'] = 1
            result_df.at[idx, 'tier_description'] = 'Complete'
            result_df.at[idx, 'data_quality_notes'] = f'Tier 1: {n_pre} pre, {n_post} post observations'
            
            # Authentic if p < 0.10 AND positive improvement
            if p_value < 0.10 and esg_improvement > 0:
                result_df.at[idx, 'is_authentic'] = 1
        
        # Tier 2: Partial data - point estimate only
        elif n_pre >= tier2_min_obs and n_post >= tier2_min_obs:
            esg_improvement = float(post_esg.mean() - pre_esg.mean())
            
            result_df.at[idx, 'esg_improvement'] = esg_improvement
            result_df.at[idx, 'esg_pvalue'] = np.nan  # No statistical test
            result_df.at[idx, 'authenticity_tier'] = 2
            result_df.at[idx, 'tier_description'] = 'Partial'
            result_df.at[idx, 'data_quality_notes'] = f'Tier 2: {n_pre} pre, {n_post} post observations (insufficient for t-test)'
            
            # For Tier 2, mark as authentic if improvement is positive
            # (lower confidence, will be capped in scoring)
            if esg_improvement > 0:
                result_df.at[idx, 'is_authentic'] = 1
        
        # Tier 3: No sufficient ESG data - fall back to certifications
        else:
            notes_parts = []
            if n_pre > 0 or n_post > 0:
                notes_parts.append(f'{n_pre} pre, {n_post} post observations')
            notes_parts.append('insufficient for ESG analysis')
            result_df.at[idx, 'data_quality_notes'] = 'Tier 3: ' + '; '.join(notes_parts)
            # Tier 3 is_authentic stays 0 (ESG not verified), but certifications may contribute
    
    # Clean up temporary columns
    result_df = result_df.drop(columns=['match_name', '_issuance_year'])
    
    return result_df


def get_esg_coverage_by_country(
    df_esg: pd.DataFrame,
    df_gb: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate ESG data coverage statistics by country.
    
    Parameters
    ----------
    df_esg : pd.DataFrame
        ESG panel data with 'company' and 'Year' columns
    df_gb : pd.DataFrame
        Green bonds data with 'Issuer/Borrower Name Full' and 
        'Issuer/Borrower Nation' columns
    
    Returns
    -------
    pd.DataFrame
        Coverage statistics with columns:
        - country: Country name
        - total_bonds: Total bonds from that country
        - bonds_with_complete_esg: Bonds with Tier 1 data (≥2 pre AND ≥2 post)
        - bonds_with_partial_esg: Bonds with Tier 2 data (≥1 pre AND ≥1 post but not Tier 1)
        - bonds_with_no_esg: Bonds with Tier 3 (no sufficient ESG data)
        - coverage_rate: Percentage of bonds with any ESG data (Tier 1 + Tier 2)
    """
    # First, calculate tiers for all bonds
    df_tiered = calculate_authenticity_tiered(df_gb, df_esg)
    
    # Add country info
    df_tiered['country'] = df_gb['Issuer/Borrower Nation']
    
    # Group by country
    coverage = df_tiered.groupby('country').agg(
        total_bonds=('authenticity_tier', 'count'),
        bonds_with_complete_esg=('authenticity_tier', lambda x: (x == 1).sum()),
        bonds_with_partial_esg=('authenticity_tier', lambda x: (x == 2).sum()),
        bonds_with_no_esg=('authenticity_tier', lambda x: (x == 3).sum()),
    ).reset_index()
    
    # Calculate coverage rate (Tier 1 + Tier 2)
    coverage['coverage_rate'] = (
        (coverage['bonds_with_complete_esg'] + coverage['bonds_with_partial_esg']) 
        / coverage['total_bonds'] * 100
    ).round(2)
    
    # Handle edge case where total_bonds = 0
    coverage['coverage_rate'] = coverage['coverage_rate'].fillna(0)
    
    return coverage


def apply_authenticity_with_fallbacks(
    panel_data_path: str,
    green_bonds_path: str,
    esg_panel_path: str = None,
    fallback: str = 'tiered',
    tier1_min_obs: int = 2,
    tier2_min_obs: int = 1,
    tier3_cap_score: int = 60,
) -> pd.DataFrame:
    """
    Apply authenticity scoring with configurable fallback behavior.
    
    This function provides flexibility in handling ESG data gaps by offering
    three modes of operation.
    
    Parameters
    ----------
    panel_data_path : str
        Path to panel data CSV (used if esg_panel_path not provided)
    green_bonds_path : str
        Path to green bonds universe CSV
    esg_panel_path : str, optional
        Path to ESG panel data CSV (if separate from panel_data)
    fallback : str, default='tiered'
        Fallback strategy:
        - 'strict': Only Tier 1 (original behavior, requires ≥2 pre AND ≥2 post)
        - 'tiered': Use all 3 tiers with appropriate caps
        - 'certification_only': Use only CBI/ICMA flags, no ESG analysis
    tier1_min_obs : int, default=2
        Minimum observations for Tier 1 (only used if fallback='tiered')
    tier2_min_obs : int, default=1
        Minimum observations for Tier 2 (only used if fallback='tiered')
    tier3_cap_score : int, default=60
        Maximum score for Tier 3 bonds (only used if fallback='tiered')
    
    Returns
    -------
    pd.DataFrame
        Green bonds DataFrame with authenticity columns:
        - is_authentic: Binary flag
        - esg_improvement: ESG improvement value
        - esg_pvalue: Statistical p-value (if applicable)
        - authenticity_tier: Tier assignment (1, 2, or 3)
        - tier_description: Human-readable tier name
        - data_quality_notes: Details about data availability
        - tier3_cap_score: Cap applied to Tier 3 bonds (for downstream scoring)
    
    Raises
    ------
    ValueError
        If fallback is not one of 'strict', 'tiered', or 'certification_only'
    """
    if fallback not in ('strict', 'tiered', 'certification_only'):
        raise ValueError(f"fallback must be 'strict', 'tiered', or 'certification_only', got '{fallback}'")
    
    df_gb = pd.read_csv(green_bonds_path)
    
    if esg_panel_path:
        df_esg = pd.read_csv(esg_panel_path)
    else:
        df_esg = pd.read_csv(panel_data_path)
    
    if fallback == 'certification_only':
        # No ESG analysis - all bonds are Tier 3
        result_df = df_gb.copy()
        result_df['is_authentic'] = 0  # Will be determined by certifications only
        result_df['esg_improvement'] = np.nan
        result_df['esg_pvalue'] = np.nan
        result_df['authenticity_tier'] = 3
        result_df['tier_description'] = 'Certification_Only'
        result_df['data_quality_notes'] = 'Certification-only mode: ESG analysis disabled'
        result_df['n_pre_obs'] = 0
        result_df['n_post_obs'] = 0
        result_df['tier3_cap_score'] = tier3_cap_score
        
    elif fallback == 'strict':
        # Original behavior - only Tier 1
        result_df = calculate_authenticity_tiered(
            df_gb, df_esg, 
            tier1_min_obs=tier1_min_obs, 
            tier2_min_obs=tier1_min_obs,  # Same threshold = effectively no Tier 2
            tier3_cap_score=0  # Tier 3 gets no score in strict mode
        )
        # In strict mode, demote Tier 2 to Tier 3
        tier2_mask = result_df['authenticity_tier'] == 2
        result_df.loc[tier2_mask, 'authenticity_tier'] = 3
        result_df.loc[tier2_mask, 'tier_description'] = 'Certification_Only'
        result_df.loc[tier2_mask, 'is_authentic'] = 0
        result_df.loc[tier2_mask, 'data_quality_notes'] = result_df.loc[tier2_mask, 'data_quality_notes'].str.replace('Tier 2', 'Strict mode: insufficient data')
        result_df['tier3_cap_score'] = 0  # No score for non-Tier-1 in strict mode
        
    else:  # 'tiered'
        result_df = calculate_authenticity_tiered(
            df_gb, df_esg,
            tier1_min_obs=tier1_min_obs,
            tier2_min_obs=tier2_min_obs,
            tier3_cap_score=tier3_cap_score
        )
        result_df['tier3_cap_score'] = tier3_cap_score
    
    # Save output
    output_path = 'data/green_bonds_authentic_tiered.csv'
    result_df.to_csv(output_path, index=False)
    
    # Print summary
    print("\nAUTHENTICITY SCORING RESULTS")
    print("=" * 70)
    print(f"Fallback mode: {fallback}")
    print(f"\nTier Distribution:")
    tier_counts = result_df['authenticity_tier'].value_counts().sort_index()
    for tier, count in tier_counts.items():
        pct = 100 * count / len(result_df)
        desc = result_df[result_df['authenticity_tier'] == tier]['tier_description'].iloc[0]
        print(f"  Tier {tier} ({desc}): {count} ({pct:.1f}%)")
    
    print(f"\nAuthenticity Status:")
    auth_count = result_df['is_authentic'].sum()
    print(f"  Authentic: {auth_count} ({100*auth_count/len(result_df):.1f}%)")
    print(f"  Not Authentic/Unverified: {len(result_df) - auth_count} ({100*(len(result_df)-auth_count)/len(result_df):.1f}%)")
    
    print(f"\n✅ Saved to {output_path}")
    
    return result_df


if __name__ == "__main__":
    # 1. Address Survivorship Bias
    dead_firms = detect_survivorship_bias('data/panel_data.csv')
    if not dead_firms.empty:
        print(f"\nFound {len(dead_firms)} potential delisted firms.")
        dead_firms.to_csv('data/potential_delisted_firms.csv')

    # 2. Address Greenwashing Bias using ESG Divergence Proxy
    print("\nApplying Authenticity Proxy...")
    df_authentic = apply_authenticity_proxy('data/esg_panel_data.csv', 'data/green-bonds.csv')
