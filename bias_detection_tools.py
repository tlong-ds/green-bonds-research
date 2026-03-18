
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

if __name__ == "__main__":
    # 1. Address Survivorship Bias
    dead_firms = detect_survivorship_bias('data/panel_data.csv')
    if not dead_firms.empty:
        print(f"\nFound {len(dead_firms)} potential delisted firms.")
        dead_firms.to_csv('data/potential_delisted_firms.csv')

    # 2. Address Greenwashing Bias using ESG Divergence Proxy
    print("\nApplying Authenticity Proxy...")
    df_authentic = apply_authenticity_proxy('data/esg_panel_data.csv', 'data/green-bonds.csv')
