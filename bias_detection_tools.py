
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

def apply_authenticity_proxy(panel_data_path, green_bonds_path):
    """
    Applies the ESG Divergence Method to proxy green bond authenticity.
    Creates an 'is_authentic' flag. 1 = Authentic, 0 = Greenwashing/Unverified.
    """
    df_panel = pd.read_csv(panel_data_path)
    df_gb = pd.read_csv(green_bonds_path)
    
    # Standardize names for matching using normalization
    df_gb['match_name'] = df_gb['Issuer/Borrower Name Full'].apply(normalize_company_name)
    df_panel['match_name'] = df_panel['company'].apply(normalize_company_name)
    
    df_gb['is_authentic'] = 0  # Default to 0
    df_gb['issuance_year'] = df_gb['Dates: Issue Date'].str.extract(r'(\d{4})')[0].astype(float)
    
    for idx, row in df_gb.iterrows():
        issuer = row['match_name']
        issuance_year = row['issuance_year']
        
        if pd.isna(issuance_year) or not issuer:
            continue
            
        issuer_data = df_panel[df_panel['match_name'] == issuer]
        if issuer_data.empty: 
            # Try a partial match if exact normalized match fails
            partial_matches = df_panel[df_panel['match_name'].str.contains(issuer, na=False, regex=False)]
            if partial_matches.empty:
                continue
            issuer_data = partial_matches
            
        # Compare ESG score Pre-Issuance vs Post-Issuance
        pre_esg = issuer_data[issuer_data['Year'] < issuance_year]['esg_score'].mean()
        post_esg = issuer_data[issuer_data['Year'] >= issuance_year]['esg_score'].mean()
        
        # If we lack pre-issuance or post-issuance ESG data, we conservatively leave it as 0
        if pd.isna(pre_esg) or pd.isna(post_esg):
            continue
            
        # SIGNAL: If ESG Score improves or stays stable, it's considered authentic
        if post_esg >= pre_esg:
            df_gb.at[idx, 'is_authentic'] = 1

    df_gb = df_gb.drop(columns=['match_name', 'issuance_year'])
    output_path = 'data/green_bonds_authentic.csv'
    df_gb.to_csv(output_path, index=False)
    
    authentic_count = df_gb['is_authentic'].sum()
    total_count = len(df_gb)
    print(f"Saved {output_path}.")
    print(f"Authenticity proxy applied: {authentic_count} out of {total_count} bonds flagged as Authentic (1).")
    
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
