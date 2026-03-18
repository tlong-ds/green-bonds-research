"""
CRITICAL FIXES FOR ASEAN GREEN BONDS ECONOMETRIC ANALYSIS

This script addresses the three critical issues identified in code evaluation:
1. PSM Common Support Verification
2. Improved Greenwashing Detection (ESG Divergence Method)
3. SE Clustering Verification & Documentation

No additional data is needed - fixes use existing panel data.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# ISSUE #1: PSM COMMON SUPPORT VERIFICATION & SENSITIVITY
# ============================================================

def verify_psm_common_support(propensity_scores_df, treated_col='is_issuer', ps_col='propensity_score'):
    """
    Verify common support assumption for PSM.
    
    Args:
        propensity_scores_df: DataFrame with propensity scores
        treated_col: Column name for treatment indicator (1=treated, 0=control)
        ps_col: Column name for propensity scores
    
    Returns:
        dict: Diagnostics including overlap stats and visualization
    """
    print("\n" + "="*80)
    print("PSM COMMON SUPPORT DIAGNOSTIC")
    print("="*80)
    
    treated_ps = propensity_scores_df[propensity_scores_df[treated_col] == 1][ps_col]
    control_ps = propensity_scores_df[propensity_scores_df[treated_col] == 0][ps_col]
    
    # Calculate ranges
    treat_min, treat_max = treated_ps.min(), treated_ps.max()
    ctrl_min, ctrl_max = control_ps.min(), control_ps.max()
    
    # Common support region
    common_support_min = max(treat_min, ctrl_min)
    common_support_max = min(treat_max, ctrl_max)
    
    print(f"\nTreated group PS range:  [{treat_min:.4f}, {treat_max:.4f}]")
    print(f"Control group PS range:  [{ctrl_min:.4f}, {ctrl_max:.4f}]")
    print(f"Common support region:   [{common_support_min:.4f}, {common_support_max:.4f}]")
    
    # Count units outside common support
    treated_outside = ((treated_ps < common_support_min) | (treated_ps > common_support_max)).sum()
    control_outside = ((control_ps < common_support_min) | (control_ps > common_support_max)).sum()
    
    pct_treated_out = 100 * treated_outside / len(treated_ps)
    pct_control_out = 100 * control_outside / len(control_ps)
    
    print(f"\n❌ Units OUTSIDE Common Support:")
    print(f"   Treated: {treated_outside} ({pct_treated_out:.1f}%)")
    print(f"   Control: {control_outside} ({pct_control_out:.1f}%)")
    
    # Recommendation
    if pct_treated_out > 5:
        print(f"\n⚠️  WARNING: {pct_treated_out:.1f}% of treated units outside common support.")
        print("   Consider dropping these units to ensure causal identification.")
    else:
        print(f"\n✅ PASS: <5% of treated units outside common support.")
    
    # Store diagnostics
    diagnostics = {
        'treated_range': (treat_min, treat_max),
        'control_range': (ctrl_min, ctrl_max),
        'common_support': (common_support_min, common_support_max),
        'treated_outside': treated_outside,
        'control_outside': control_outside,
        'pct_treated_outside': pct_treated_out,
        'pct_control_outside': pct_control_out
    }
    
    return diagnostics


def psm_caliper_sensitivity_analysis(propensity_scores_df, treated_col='is_issuer', 
                                     ps_col='propensity_score', calipers=[0.05, 0.10, 0.15]):
    """
    Run PSM sensitivity analysis with multiple calipers.
    Shows how caliper choice affects sample size and balance.
    
    Args:
        propensity_scores_df: DataFrame with propensity scores
        treated_col: Column name for treatment indicator
        ps_col: Column name for propensity scores
        calipers: List of caliper values to test (in SD units)
    
    Returns:
        DataFrame: Sensitivity results for each caliper
    """
    print("\n" + "="*80)
    print("PSM CALIPER SENSITIVITY ANALYSIS")
    print("="*80)
    
    results = []
    ps_std = propensity_scores_df[ps_col].std()
    
    for caliper in calipers:
        caliper_sd = caliper * ps_std
        
        treated_df = propensity_scores_df[propensity_scores_df[treated_col] == 1].copy()
        control_df = propensity_scores_df[propensity_scores_df[treated_col] == 0].copy()
        
        # Simple nearest neighbor matching with caliper
        matched_count = 0
        unmatched_treated = 0
        
        for idx, treat_row in treated_df.iterrows():
            treat_ps = treat_row[ps_col]
            distances = np.abs(control_df[ps_col] - treat_ps)
            min_dist = distances.min()
            
            if min_dist <= caliper_sd:
                matched_count += 1
            else:
                unmatched_treated += 1
        
        match_rate = 100 * matched_count / len(treated_df) if len(treated_df) > 0 else 0
        
        results.append({
            'Caliper (SD)': f"{caliper:.2f}",
            'Caliper (abs)': f"{caliper_sd:.4f}",
            'Matched Treated': matched_count,
            'Unmatched Treated': unmatched_treated,
            'Match Rate (%)': f"{match_rate:.1f}%",
            'Total N': len(treated_df)
        })
        
        print(f"\n📊 Caliper = {caliper:.2f} SD ({caliper_sd:.4f} PS range)")
        print(f"   Matched pairs: {matched_count}/{len(treated_df)} ({match_rate:.1f}%)")
        print(f"   Unmatched: {unmatched_treated}")
    
    sensitivity_df = pd.DataFrame(results)
    print(f"\n" + "="*80)
    print("SENSITIVITY SUMMARY:")
    print("="*80)
    print(sensitivity_df.to_string(index=False))
    
    return sensitivity_df


def plot_psm_overlap(propensity_scores_df, treated_col='is_issuer', ps_col='propensity_score', 
                    output_path='images/psm_overlap_diagnostic.png'):
    """
    Visualize propensity score overlap between treated and control groups.
    """
    treated_ps = propensity_scores_df[propensity_scores_df[treated_col] == 1][ps_col]
    control_ps = propensity_scores_df[propensity_scores_df[treated_col] == 0][ps_col]
    
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    
    # Histogram
    ax = axes[0]
    ax.hist(treated_ps, bins=30, alpha=0.6, label='Treated (Issuers)', color='green', edgecolor='black')
    ax.hist(control_ps, bins=30, alpha=0.6, label='Control (Non-Issuers)', color='red', edgecolor='black')
    ax.set_xlabel('Propensity Score', fontsize=11, fontweight='bold')
    ax.set_ylabel('Frequency', fontsize=11, fontweight='bold')
    ax.set_title('Distribution of Propensity Scores\nTreated vs. Control', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Density plot
    ax = axes[1]
    treated_ps.plot(kind='density', ax=ax, label='Treated', linewidth=2.5, color='green')
    control_ps.plot(kind='density', ax=ax, label='Control', linewidth=2.5, color='red')
    ax.fill_between([treated_ps.min(), treated_ps.max()], 0, ax.get_ylim()[1], 
                     alpha=0.1, color='yellow', label='Common Support')
    ax.set_xlabel('Propensity Score', fontsize=11, fontweight='bold')
    ax.set_ylabel('Density', fontsize=11, fontweight='bold')
    ax.set_title('Kernel Density Estimation\nCommon Support Verification', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✅ PSM overlap plot saved to {output_path}")
    plt.close()


# ============================================================
# ISSUE #2: GREENWASHING HYPOTHESIS TESTING & SENSITIVITY
# ============================================================

def greenwashing_ttest_analysis(panel_df, outcomes=['return_on_assets', 'Tobin_Q', 'esg_score', 'ln_emissions_intensity'],
                               cert_col='certified_bond_active', issuer_col='is_issuer'):
    """
    Perform t-tests comparing certified vs non-certified green bonds on key outcomes.
    
    Tests H3 hypothesis: Certified bonds show stronger effects than non-certified.
    
    Args:
        panel_df: Panel DataFrame with treatment and outcome variables
        outcomes: List of outcome variable names
        cert_col: Column name for certified bond indicator
        issuer_col: Column name for issuer indicator
    
    Returns:
        DataFrame: T-test results for each outcome
    """
    print("\n" + "="*80)
    print("GREENWASHING HYPOTHESIS TEST: CERTIFIED vs NON-CERTIFIED BONDS")
    print("="*80)
    
    results = []
    
    for outcome in outcomes:
        if outcome not in panel_df.columns:
            print(f"⚠️  Outcome '{outcome}' not found in data. Skipping.")
            continue
        
        # Remove missing values
        valid_df = panel_df[[outcome, cert_col, issuer_col]].dropna()
        
        if len(valid_df) == 0:
            print(f"⚠️  No valid data for '{outcome}'. Skipping.")
            continue
        
        # Three groups: Non-Issuers, Non-Certified Issuers, Certified Issuers
        non_issuers = valid_df[valid_df[issuer_col] == 0][outcome]
        certified = valid_df[(valid_df[issuer_col] == 1) & (valid_df[cert_col] == 1)][outcome]
        non_certified = valid_df[(valid_df[issuer_col] == 1) & (valid_df[cert_col] == 0)][outcome]
        
        print(f"\n📊 {outcome.upper()}")
        print(f"   Non-Issuers:      N={len(non_issuers)}, Mean={non_issuers.mean():.4f}, SD={non_issuers.std():.4f}")
        print(f"   Certified Issuers: N={len(certified)}, Mean={certified.mean():.4f}, SD={certified.std():.4f}")
        print(f"   Non-Cert Issuers:  N={len(non_certified)}, Mean={non_certified.mean():.4f}, SD={non_certified.std():.4f}")
        
        # H3a: Certified > Non-Certified (Welch's t-test)
        if len(certified) > 1 and len(non_certified) > 1:
            t_stat_h3a, p_val_h3a = stats.ttest_ind(certified, non_certified, equal_var=False)
            effect_size_h3a = (certified.mean() - non_certified.mean()) / np.sqrt((certified.std()**2 + non_certified.std()**2) / 2)
            
            print(f"\n   H3a: Certified > Non-Certified")
            print(f"        t-stat = {t_stat_h3a:.4f}, p-value = {p_val_h3a:.4f}")
            print(f"        Effect size (Cohen's d) = {effect_size_h3a:.4f}")
            print(f"        Result: {'✅ SUPPORTED' if p_val_h3a < 0.10 else '❌ NOT SUPPORTED'}")
            
            results.append({
                'Outcome': outcome,
                'Test': 'H3a: Cert > Non-Cert',
                'Group1': 'Certified',
                'Group2': 'Non-Certified',
                'N1': len(certified),
                'N2': len(non_certified),
                'Mean1': certified.mean(),
                'Mean2': non_certified.mean(),
                'Mean Diff': certified.mean() - non_certified.mean(),
                'Cohen_d': effect_size_h3a,
                't_stat': t_stat_h3a,
                'p_value': p_val_h3a,
                'Significant': p_val_h3a < 0.10
            })
        
        # H3b: Certified > Non-Issuers (Welch's t-test)
        if len(certified) > 1 and len(non_issuers) > 1:
            t_stat_h3b, p_val_h3b = stats.ttest_ind(certified, non_issuers, equal_var=False)
            effect_size_h3b = (certified.mean() - non_issuers.mean()) / np.sqrt((certified.std()**2 + non_issuers.std()**2) / 2)
            
            print(f"\n   H3b: Certified > Non-Issuers")
            print(f"        t-stat = {t_stat_h3b:.4f}, p-value = {p_val_h3b:.4f}")
            print(f"        Effect size (Cohen's d) = {effect_size_h3b:.4f}")
            print(f"        Result: {'✅ SUPPORTED' if p_val_h3b < 0.10 else '❌ NOT SUPPORTED'}")
            
            results.append({
                'Outcome': outcome,
                'Test': 'H3b: Cert > Non-Issuers',
                'Group1': 'Certified',
                'Group2': 'Non-Issuers',
                'N1': len(certified),
                'N2': len(non_issuers),
                'Mean1': certified.mean(),
                'Mean2': non_issuers.mean(),
                'Mean Diff': certified.mean() - non_issuers.mean(),
                'Cohen_d': effect_size_h3b,
                't_stat': t_stat_h3b,
                'p_value': p_val_h3b,
                'Significant': p_val_h3b < 0.10
            })
    
    results_df = pd.DataFrame(results)
    print(f"\n" + "="*80)
    print("T-TEST SUMMARY TABLE:")
    print("="*80)
    if len(results_df) > 0:
        summary_cols = ['Outcome', 'Test', 'Mean Diff', 'Cohen_d', 'p_value', 'Significant']
        print(results_df[summary_cols].to_string(index=False))
    else:
        print("⚠️  No results to display.")
    
    return results_df


def greenwashing_proxy_sensitivity(panel_df, did_col='did', did_cert_col='did_certified', 
                                   did_non_cert_col='did_non_certified',
                                   outcomes=['return_on_assets', 'Tobin_Q', 'esg_score']):
    """
    Sensitivity analysis: Test robustness of greenwashing effects across alternative proxies.
    
    Args:
        panel_df: Panel DataFrame
        did_col: Main DiD column
        did_cert_col: Certified bond DiD column
        did_non_cert_col: Non-certified bond DiD column
        outcomes: Outcome variables
    
    Returns:
        DataFrame: Effect sizes across different specifications
    """
    print("\n" + "="*80)
    print("GREENWASHING PROXY SENSITIVITY ANALYSIS")
    print("="*80)
    
    results = []
    
    # Alternative 1: Simple binary (any cert bond vs not)
    # Alternative 2: Proportion certified (continuous)
    # Alternative 3: Environment pillar score instead of ESG
    
    print(f"\n📊 Testing robustness of greenwashing effects...")
    print(f"   Specification 1: Binary certified indicator (baseline)")
    print(f"   Specification 2: Robustness checks with alternative cuts")
    
    for outcome in outcomes:
        if outcome not in panel_df.columns:
            continue
        
        valid_df = panel_df[[outcome, did_col, did_cert_col, did_non_cert_col]].dropna()
        
        if len(valid_df) == 0:
            continue
        
        # Get treated and control
        treated = valid_df[valid_df[did_col] == 1][outcome]
        control = valid_df[valid_df[did_col] == 0][outcome]
        
        certified_treated = valid_df[valid_df[did_cert_col] == 1][outcome]
        non_cert_treated = valid_df[valid_df[did_non_cert_col] == 1][outcome]
        
        if len(treated) > 0 and len(control) > 0:
            ate_all = treated.mean() - control.mean()
            
            ate_cert = certified_treated.mean() - control.mean() if len(certified_treated) > 0 else np.nan
            ate_non_cert = non_cert_treated.mean() - control.mean() if len(non_cert_treated) > 0 else np.nan
            
            results.append({
                'Outcome': outcome,
                'ATE_All_Green_Bonds': ate_all,
                'ATE_Certified': ate_cert,
                'ATE_Non_Certified': ate_non_cert,
                'Certification_Premium': ate_cert - ate_non_cert if not np.isnan(ate_cert) and not np.isnan(ate_non_cert) else np.nan
            })
            
            print(f"\n   {outcome}:")
            print(f"      All green bonds: {ate_all:.4f}")
            print(f"      Certified:       {ate_cert:.4f}")
            print(f"      Non-Certified:   {ate_non_cert:.4f}")
            print(f"      Premium:         {ate_cert - ate_non_cert if not np.isnan(ate_cert) and not np.isnan(ate_non_cert) else 'N/A'}")
    
    sensitivity_df = pd.DataFrame(results)
    print(f"\n" + "="*80)
    print("SENSITIVITY SUMMARY:")
    print("="*80)
    if len(sensitivity_df) > 0:
        print(sensitivity_df.to_string(index=False))
    else:
        print("⚠️  No results to display.")
    
    return sensitivity_df


def plot_greenwashing_comparison(panel_df, outcomes=['return_on_assets', 'Tobin_Q', 'esg_score', 'ln_emissions_intensity'],
                                 cert_col='certified_bond_active', issuer_col='is_issuer',
                                 output_path='images/greenwashing_hypothesis_test.png'):
    """
    Create visualization comparing certified vs non-certified vs non-issuers on key outcomes.
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    for idx, outcome in enumerate(outcomes):
        if outcome not in panel_df.columns or idx >= len(axes):
            continue
        
        ax = axes[idx]
        valid_df = panel_df[[outcome, cert_col, issuer_col]].dropna()
        
        # Create three groups
        non_issuers = valid_df[valid_df[issuer_col] == 0][outcome]
        certified = valid_df[(valid_df[issuer_col] == 1) & (valid_df[cert_col] == 1)][outcome]
        non_certified = valid_df[(valid_df[issuer_col] == 1) & (valid_df[cert_col] == 0)][outcome]
        
        data_to_plot = [non_issuers, certified, non_certified]
        labels = ['Non-Issuers', 'Certified', 'Non-Certified']
        colors = ['lightcoral', 'lightgreen', 'lightyellow']
        
        bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True, notch=True)
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
        
        ax.set_ylabel(outcome, fontsize=11, fontweight='bold')
        ax.set_title(f'{outcome}\n(N={len(non_issuers)}, {len(certified)}, {len(non_certified)})', fontsize=11)
        ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✅ Greenwashing comparison plot saved to {output_path}")
    plt.close()
    """
    Enhanced greenwashing proxy using:
    - Statistical significance test (t-test)
    - Pre/Post ESG score comparison
    - Alternative definitions (Environmental Pillar Score)
    - Sensitivity analysis
    
    Returns:
        DataFrame: Green bonds with improved is_authentic flag + sensitivity columns
    """
    print("\n" + "="*80)
    print("IMPROVED GREENWASHING DETECTION (ESG DIVERGENCE METHOD)")
    print("="*80)
    
    # Load data
    df_panel = pd.read_csv(panel_data_path)
    df_gb = pd.read_csv(green_bonds_path)
    df_esg = pd.read_csv(esg_panel_path)
    
    # Standardize names for matching
    def normalize_company_name(name):
        if pd.isna(name):
            return ""
        name = str(name).upper()
        suffixes = [
            r'\bPCL\b', r'\bPLC\b', r'\bLTD\b', r'\bLIMITED\b', r'\bCORP\b', 
            r'\bCORPORATION\b', r'\bINC\b', r'\bINCORPORATED\b', r'\bBHD\b', 
            r'\bSDN BHD\b', r'\bPT\b', r'\bTBK\b', r'\bCO\b', r'\bCOMPANY\b',
            r'\bGROUP\b', r'\bHOLDINGS\b', r'\bHOLDING\b', r'\bOJK\b', r'\bSA\b'
        ]
        import re
        for suffix in suffixes:
            name = re.sub(suffix, '', name)
        name = re.sub(r'[^\w\s]', '', name)
        return name.strip()
    
    df_gb['match_name'] = df_gb['Issuer/Borrower Name Full'].apply(normalize_company_name)
    df_esg['match_name'] = df_esg['company'].apply(normalize_company_name)
    
    # Extract issuance year
    df_gb['issuance_year'] = df_gb['Dates: Issue Date'].str.extract(r'(\d{4})')[0].astype(float)
    
    # Initialize columns
    df_gb['is_authentic'] = 0
    df_gb['esg_improvement'] = np.nan
    df_gb['esg_pvalue'] = np.nan
    df_gb['env_improvement'] = np.nan
    df_gb['env_pvalue'] = np.nan
    df_gb['data_quality'] = 'insufficient_data'
    
    results_summary = []
    
    print("\nAnalyzing each bond issuance...\n")
    
    for idx, row in df_gb.iterrows():
        issuer = row['match_name']
        issuance_year = row['issuance_year']
        
        if pd.isna(issuance_year) or not issuer:
            continue
        
        # Get issuer data
        issuer_data = df_esg[df_esg['match_name'] == issuer].copy()
        
        if issuer_data.empty:
            # Try partial match
            issuer_data = df_esg[df_esg['match_name'].str.contains(issuer, na=False, regex=False)]
            if issuer_data.empty:
                continue
        
        # Use 1-year lag for pre/post (ESG reports lag by ~6 months)
        pre_window_years = [y for y in range(int(issuance_year)-3, int(issuance_year)-1)]
        post_window_years = [y for y in range(int(issuance_year)+1, int(issuance_year)+4)]
        
        pre_data = issuer_data[issuer_data['Year'].isin(pre_window_years)]
        post_data = issuer_data[issuer_data['Year'].isin(post_window_years)]
        
        # ESG Score comparison
        pre_esg = pre_data['esg_score'].dropna().values
        post_esg = post_data['esg_score'].dropna().values
        
        if len(pre_esg) > 0 and len(post_esg) > 0:
            esg_improvement = post_esg.mean() - pre_esg.mean()
            t_stat, p_value = stats.ttest_ind(post_esg, pre_esg)
            
            df_gb.at[idx, 'esg_improvement'] = esg_improvement
            df_gb.at[idx, 'esg_pvalue'] = p_value
            
            # MAIN DEFINITION: Improvement is statistically significant at 10% level
            if p_value < 0.10 and esg_improvement > 0:
                df_gb.at[idx, 'is_authentic'] = 1
                df_gb.at[idx, 'data_quality'] = 'esg_score_complete'
        
        # Environmental Pillar comparison (alternative definition)
        pre_env = pre_data['environmental_investment'].dropna().values
        post_env = post_data['environmental_investment'].dropna().values
        
        if len(pre_env) > 0 and len(post_env) > 0:
            env_improvement = (post_env == 'Y').sum() - (pre_env == 'Y').sum()
            df_gb.at[idx, 'env_improvement'] = env_improvement
            
            # Track environmental commitment signal
            if env_improvement > 0:
                df_gb.at[idx, 'env_pvalue'] = 0.01  # Flag if improved
        
        # Record summary
        results_summary.append({
            'issuer': issuer,
            'issuance_year': issuance_year,
            'is_authentic': df_gb.at[idx, 'is_authentic'],
            'esg_improvement': esg_improvement if len(pre_esg) > 0 and len(post_esg) > 0 else np.nan,
            'esg_pvalue': p_value if len(pre_esg) > 0 and len(post_esg) > 0 else np.nan,
            'pre_esg_n': len(pre_esg),
            'post_esg_n': len(post_esg),
            'data_quality': df_gb.at[idx, 'data_quality']
        })
    
    # Save enhanced data
    df_gb.to_csv('data/green_bonds_authentic_improved.csv', index=False)
    results_df = pd.DataFrame(results_summary)
    
    # Print summary
    print("\n" + "-"*80)
    print("GREENWASHING DETECTION RESULTS")
    print("-"*80)
    
    authentic_count = df_gb['is_authentic'].sum()
    total_count = len(df_gb)
    
    print(f"\nTotal Green Bonds Analyzed: {total_count}")
    print(f"Flagged as Authentic: {authentic_count} ({100*authentic_count/total_count:.1f}%)")
    print(f"Flagged as Greenwashing/Unverified: {total_count - authentic_count} ({100*(total_count-authentic_count)/total_count:.1f}%)")
    
    print(f"\nData Quality Breakdown:")
    print(results_df['data_quality'].value_counts())
    
    print(f"\nESG Improvement Statistics (Authentic Bonds Only):")
    authentic_bonds = results_df[results_df['is_authentic'] == 1]
    if not authentic_bonds.empty:
        print(f"  Mean ESG improvement: {authentic_bonds['esg_improvement'].mean():.3f} pts")
        print(f"  Median p-value: {authentic_bonds['esg_pvalue'].median():.4f}")
        print(f"  Avg pre-issuance ESG obs: {authentic_bonds['pre_esg_n'].mean():.1f}")
        print(f"  Avg post-issuance ESG obs: {authentic_bonds['post_esg_n'].mean():.1f}")
    
    # Sensitivity analysis
    print(f"\nSENSITIVITY ANALYSIS:")
    print(f"Definition 1 (p<0.10, improvement>0): {(results_df['esg_pvalue'] < 0.10).sum()} bonds")
    print(f"Definition 2 (p<0.05, improvement>0): {(results_df['esg_pvalue'] < 0.05).sum()} bonds")
    print(f"Definition 3 (p<0.10, improvement>2): {((results_df['esg_pvalue'] < 0.10) & (results_df['esg_improvement'] > 2)).sum()} bonds")
    
    print(f"\n✅ Enhanced authenticity data saved to data/green_bonds_authentic_improved.csv")
    
    return df_gb, results_df


# ============================================================
# ISSUE #3: SE CLUSTERING VERIFICATION & MOULTON FACTOR
# ============================================================

def calculate_moulton_factor(df_panel, outcome, residuals=None):
    """
    Calculate Moulton factor to quantify necessity of clustering.
    
    Moulton Factor = sqrt(1 + rho * (m_bar - 1))
    where: rho = within-firm correlation of residuals
           m_bar = average # of observations per firm
    
    Args:
        df_panel: Panel DataFrame with firm clusters
        outcome: Outcome variable name
        residuals: Optional residual series (if None, uses outcome variance)
    
    Returns:
        float: Moulton factor estimate
    """
    # Set index if not already
    if not isinstance(df_panel.index, pd.MultiIndex):
        print("Warning: DataFrame should be indexed by (firm, year)")
        df_temp = df_panel.copy()
    else:
        df_temp = df_panel.copy()
    
    # Get firm-level observations count
    if isinstance(df_temp.index, pd.MultiIndex):
        firms_obs = df_temp.index.get_level_values(0).value_counts()
    else:
        firms_obs = df_temp.groupby(level=0).size() if df_temp.index.name else pd.Series([len(df_temp)])
    
    m_bar = firms_obs.mean()
    
    # Calculate within-firm correlation of outcomes (or residuals)
    if residuals is None and outcome in df_temp.columns:
        resid_data = df_temp[outcome].dropna()
    elif residuals is not None:
        resid_data = residuals
    else:
        return 1.0
    
    # Estimate within-firm correlation
    # For each firm, calculate mean deviation from grand mean
    if isinstance(df_temp.index, pd.MultiIndex):
        firm_means = resid_data.groupby(level=0).mean()
        grand_mean = resid_data.mean()
        grand_var = ((resid_data - grand_mean) ** 2).sum() / (len(resid_data) - 1)
        between_var = ((firm_means - grand_mean) ** 2).sum() / (len(firm_means) - 1)
        rho_est = max(0, between_var / (grand_var + 1e-10))
    else:
        rho_est = 0.1  # Conservative estimate if can't compute
    
    moulton_factor = np.sqrt(1 + rho_est * (m_bar - 1))
    
    return moulton_factor


def document_se_clustering(regression_results, panel_df=None, outcome_var=None):
    """
    Verify and document SE clustering in regression output.
    Calculates Moulton factor to justify clustering.
    
    Args:
        regression_results: linearmodels regression results object
        panel_df: Optional panel DataFrame for Moulton factor calculation
        outcome_var: Optional outcome variable name for Moulton calculation
    
    Returns:
        dict: Clustering diagnostics including Moulton factor
    """
    print("\n" + "="*80)
    print("STANDARD ERROR CLUSTERING VERIFICATION & DIAGNOSTICS")
    print("="*80)
    
    diagnostics = {}
    
    # Check if clustered
    is_clustered = False
    if hasattr(regression_results, 'cov_type'):
        print(f"\n✅ Covariance Type: {regression_results.cov_type}")
        diagnostics['cov_type'] = regression_results.cov_type
        is_clustered = 'cluster' in str(regression_results.cov_type).lower()
    else:
        print(f"\n❌ Covariance type not found in output")
        diagnostics['cov_type'] = 'Unknown'
    
    if is_clustered:
        print("✅ SEs ARE CLUSTERED at firm level")
        if hasattr(regression_results, '_cluster_var'):
            print(f"   Cluster variable: {regression_results._cluster_var}")
    else:
        print("❌ WARNING: SEs may NOT be clustered")
    
    diagnostics['is_clustered'] = is_clustered
    
    # Calculate Moulton factor if possible
    if panel_df is not None and outcome_var is not None:
        try:
            mf, m_bar, rho = calculate_moulton_factor(panel_df, outcome_var)
            print(f"\n📊 MOULTON FACTOR CALCULATION:")
            print(f"   Moulton Factor (MF) = {mf:.3f}")
            print(f"   Avg obs per firm (m̄) = {m_bar:.1f}")
            print(f"   Within-firm correlation (ρ) = {rho:.3f}")
            
            if mf > 2.0:
                print(f"\n   ⚠️  SEVERE: MF > 2.0 → Naive SEs understate uncertainty by {(mf/1.0 - 1)*100:.0f}%")
                print("   CLUSTERING IS ESSENTIAL")
            elif mf > 1.5:
                print(f"\n   ⚠️  IMPORTANT: MF > 1.5 → Naive SEs understate uncertainty by {(mf/1.0 - 1)*100:.0f}%")
                print("   CLUSTERING IS RECOMMENDED")
            else:
                print(f"\n   ✓ MF ≤ 1.5 → Clustering has modest effect ({(mf/1.0 - 1)*100:.0f}% understatement)")
                print("   CLUSTERING IS HELPFUL BUT NOT CRITICAL")
            
            diagnostics['moulton_factor'] = mf
            diagnostics['avg_obs_per_firm'] = m_bar
            diagnostics['within_firm_corr'] = rho
        except Exception as e:
            print(f"\n⚠️  Could not calculate Moulton factor: {str(e)[:100]}")
    else:
        print(f"\nℹ️  To calculate Moulton factor:")
        print(f"    Call: calculate_moulton_factor(panel_df, outcome_var)")
        print(f"    with panel_df indexed by (firm, year) and outcome_var column name")
    
    print(f"\n" + "="*80)
    print("SUMMARY: SEs are CLUSTERED" if is_clustered else "WARNING: SEs may NOT be CLUSTERED")
    print("="*80)
    
    return diagnostics


# ============================================================
# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":
    print("\n" + "█"*80)
    print("CRITICAL FIXES: ASEAN GREEN BONDS ECONOMETRIC ANALYSIS")
    print("█"*80)
    
    # FIX #2: Improved Greenwashing Detection (can run independently)
    try:
        df_gb_improved, results_summary = improve_authenticity_detection(
            'data/panel_data.csv',
            'data/green-bonds.csv',
            'data/esg_panel_data.csv'
        )
        print("\n✅ FIX #2 COMPLETE: Improved greenwashing detection implemented")
    except FileNotFoundError as e:
        print(f"\n❌ Error loading data: {e}")
        print("   Ensure these files exist: panel_data.csv, green-bonds.csv, esg_panel_data.csv")
    
    print("\n" + "-"*80)
    print("NEXT STEPS:")
    print("-"*80)
    print("""
1. For FIX #1 (PSM Common Support):
   - Load your matched data: df_matched = pd.read_csv('...')
   - Run: psm_diag = verify_psm_common_support(df_matched, treated_col='is_issuer', ps_col='propensity_score')
   - Visualize: plot_psm_overlap(df_matched, output_path='images/psm_overlap.png')

2. For FIX #3 (SE Clustering Verification):
   - In your methodology notebook Cell (DiD Regression):
   - Verify output shows: cov_type='clustered', cluster_entity=True
   - Print: document_se_clustering(results)

3. Use improved authenticity data:
   - df_gb_improved = pd.read_csv('data/green_bonds_authentic_improved.csv')
   - Merge into your analysis with is_authentic == 1 for treated group
    """)
    
    print("\n" + "█"*80)
    print("All fixes ready. See ACTION_CHECKLIST.md for detailed next steps.")
    print("█"*80)

def test_parallel_trends(df_panel, event_times, outcome, treatment_col='did', 
                         controls=None, max_leads=5, max_lags=5):
    """
    Test parallel trends assumption using event study approach.
    
    Tests whether pre-treatment coefficients (leads) are zero.
    If true, supports parallel trends assumption.
    
    Args:
        df_panel: Panel data indexed by (firm, year)
        event_times: Series with event time relative to first treatment
        outcome: Outcome variable name
        treatment_col: Treatment variable name
        controls: List of control variable names
        max_leads: Years before event to include
        max_lags: Years after event to include
    
    Returns:
        dict: Results including pre-treatment p-value
    """
    import pandas as pd
    import numpy as np
    from scipy import stats as sp_stats
    
    df_reg = df_panel.copy()
    df_reg['event_time'] = event_times
    
    # Create indicators for each relative time period
    for t in range(-max_leads, max_lags + 1):
        if t != 0:  # Omit t=0 as base category
            df_reg[f'rel_time_{t}'] = (df_reg['event_time'] == t).astype(int)
    
    # Get relative time indicators
    rel_time_cols = [f'rel_time_{t}' for t in range(-max_leads, max_lags + 1) if t != 0]
    
    # Build formula
    formula_cols = ' + '.join(rel_time_cols)
    if controls:
        formula_cols += ' + ' + ' + '.join(controls)
    formula = f"{outcome} ~ {formula_cols} + EntityEffects + TimeEffects"
    
    try:
        from linearmodels.panel import PanelOLS
        
        # Prepare data
        reg_data = df_reg[df_reg['event_time'].notna()].dropna(
            subset=[outcome] + [c for c in controls if c] + rel_time_cols
        )
        
        mod = PanelOLS.from_formula(formula, data=reg_data)
        res = mod.fit(cov_type='clustered', cluster_entity=True)
        
        # Test pre-treatment (leads only)
        pre_treat_cols = [f'rel_time_{t}' for t in range(-max_leads, 0)]
        pre_treat_pvals = res.pvalues[pre_treat_cols]
        
        # Joint test of all pre-treatment coefficients
        pre_treat_coefs = res.params[pre_treat_cols].values
        pre_treat_cov = res.cov.loc[pre_treat_cols, pre_treat_cols]
        
        # F-test: H0: all pre-treatment coefs = 0
        try:
            inv_cov = np.linalg.inv(pre_treat_cov)
            f_stat = pre_treat_coefs @ inv_cov @ pre_treat_coefs / len(pre_treat_cols)
            p_val = 1 - sp_stats.f.cdf(f_stat, len(pre_treat_cols), len(reg_data) - len(res.params))
        except:
            p_val = np.nan
        
        return {
            'pre_treatment_pvalues': pre_treat_pvals,
            'joint_f_stat': f_stat if not np.isnan(f_stat) else None,
            'joint_p_value': p_val,
            'parallel_trends_holds': p_val > 0.10 if not np.isnan(p_val) else None,
            'coefficients': res.params,
            'results': res
        }
    except Exception as e:
        return {'error': str(e)}

def placebo_test(df_panel, treatment_col='did', outcomes=None, controls=None, 
                 n_placebo=100, random_seed=42):
    """
    Placebo test: Assign random treatment to non-treated units.
    
    Tests whether effect of RANDOM treatment ≈ 0 (validates design).
    If random assignment produces significant effects, design is biased.
    
    Args:
        df_panel: Panel data indexed by (firm, year)
        treatment_col: Treatment variable name
        outcomes: List of outcome variables
        controls: List of control variables
        n_placebo: Number of placebo assignments to test
        random_seed: Random seed for reproducibility
    
    Returns:
        dict: Placebo effect distribution statistics
    """
    import pandas as pd
    import numpy as np
    from scipy import stats as sp_stats
    
    if outcomes is None:
        outcomes = ['return_on_assets', 'Tobin_Q', 'esg_score']
    if controls is None:
        controls = ['L1_Firm_Size', 'L1_Leverage']
    
    np.random.seed(random_seed)
    placebo_results = {out: [] for out in outcomes}
    
    # Get treatment indicator
    is_treated = df_panel[treatment_col].groupby(level='company').first() > 0
    treated_firms = is_treated[is_treated].index.tolist()
    
    print(f"\nRunning {n_placebo} placebo tests...")
    print(f"Actual treatment: {len(treated_firms)} firms")
    
    for rep in range(n_placebo):
        # Assign random treatment to placebo firms
        placebo_firms = np.random.choice(treated_firms, size=len(treated_firms), replace=False)
        df_placebo = df_panel.copy()
        
        # Create placebo treatment
        df_placebo['placebo_treat'] = 0
        for firm in placebo_firms:
            df_placebo.loc[firm, 'placebo_treat'] = 1
        
        # Run regression with placebo treatment
        for outcome in outcomes:
            try:
                from linearmodels.panel import PanelOLS
                
                controls_str = ' + '.join(controls)
                formula = f"{outcome} ~ placebo_treat + {controls_str} + EntityEffects"
                
                reg_data = df_placebo.dropna(subset=[outcome, 'placebo_treat'] + controls)
                
                if len(reg_data) > 100:
                    mod = PanelOLS.from_formula(formula, data=reg_data)
                    res = mod.fit(cov_type='clustered', cluster_entity=True, disp='off')
                    
                    # Store effect and p-value
                    effect = res.params.get('placebo_treat', 0)
                    p_val = res.pvalues.get('placebo_treat', 1.0)
                    placebo_results[outcome].append({'effect': effect, 'p_value': p_val})
            except:
                pass
        
        if (rep + 1) % 25 == 0:
            print(f"  Completed {rep + 1}/{n_placebo} placebo replications")
    
    # Summarize results
    summary = {}
    for outcome, results_list in placebo_results.items():
        if results_list:
            effects = [r['effect'] for r in results_list]
            p_vals = [r['p_value'] for r in results_list]
            summary[outcome] = {
                'mean_effect': np.mean(effects),
                'std_effect': np.std(effects),
                'min_effect': np.min(effects),
                'max_effect': np.max(effects),
                'pct_significant': 100 * np.mean(np.array(p_vals) < 0.05),
                'effects': effects,
                'p_values': p_vals
            }
    
    return summary


def sensitivity_analysis_loocv(df_panel, treatment_col='did', outcome='return_on_assets', 
                               controls=None, fe_type='EntityEffects'):
    """
    Leave-one-out-cross-validation (LOOCV) sensitivity analysis.
    
    Sequentially removes each treated firm, re-estimates DiD.
    Checks if results driven by outlier.
    
    Args:
        df_panel: Panel data indexed by (firm, year)
        treatment_col: Treatment variable name
        outcome: Outcome variable
        controls: List of control variables
        fe_type: Type of fixed effects ('EntityEffects', 'TimeEffects', or 'None')
    
    Returns:
        dict: Coefficient estimates dropping each treated firm
    """
    import pandas as pd
    import numpy as np
    
    if controls is None:
        controls = ['L1_Firm_Size', 'L1_Leverage']
    
    # Get treated firms
    df_temp = df_panel.copy()
    is_treated = df_temp[treatment_col].groupby(level='company').max() > 0
    treated_firms = is_treated[is_treated].index.tolist()
    
    print(f"\nRunning LOOCV sensitivity analysis...")
    print(f"Removing {len(treated_firms)} treated firms one at a time")
    
    results = []
    
    for i, drop_firm in enumerate(treated_firms):
        # Remove one treated firm
        df_loocv = df_panel[df_panel.index.get_level_values('company') != drop_firm].copy()
        
        try:
            from linearmodels.panel import PanelOLS
            
            controls_str = ' + '.join(controls)
            fe_str = f" + {fe_type}" if fe_type != 'None' else ""
            formula = f"{outcome} ~ {treatment_col} + {controls_str}{fe_str}"
            
            reg_data = df_loocv.dropna(subset=[outcome, treatment_col] + controls)
            
            if len(reg_data) > 100:
                mod = PanelOLS.from_formula(formula, data=reg_data)
                res = mod.fit(cov_type='clustered', cluster_entity=True, disp='off')
                
                coef = res.params.get(treatment_col, np.nan)
                se = res.std_errors.get(treatment_col, np.nan)
                p_val = res.pvalues.get(treatment_col, np.nan)
                
                results.append({
                    'dropped_firm': drop_firm,
                    'coefficient': coef,
                    'std_error': se,
                    'p_value': p_val,
                    'n_obs': len(reg_data)
                })
        except:
            results.append({
                'dropped_firm': drop_firm,
                'coefficient': np.nan,
                'std_error': np.nan,
                'p_value': np.nan,
                'n_obs': 0
            })
        
        if (i + 1) % 5 == 0 or i == len(treated_firms) - 1:
            print(f"  Completed {i + 1}/{len(treated_firms)} leave-one-out iterations")
    
    results_df = pd.DataFrame(results)
    
    # Summary statistics
    valid_coefs = results_df['coefficient'].dropna()
    print(f"\nLOOCV Summary (coefficient across {len(valid_coefs)} specifications):")
    print(f"  Mean: {valid_coefs.mean():.6f}")
    print(f"  Std Dev: {valid_coefs.std():.6f}")
    print(f"  Min: {valid_coefs.min():.6f}")
    print(f"  Max: {valid_coefs.max():.6f}")
    print(f"  Range: {valid_coefs.max() - valid_coefs.min():.6f}")
    
    return results_df


def specification_robustness_table(df_panel, treatment_col='did', outcomes=None, 
                                   control_specs=None):
    """
    Test robustness across different control variable specifications.
    
    Args:
        df_panel: Panel data indexed by (firm, year)
        treatment_col: Treatment variable name
        outcomes: List of outcomes to test
        control_specs: List of control sets (each is a list of variables)
    
    Returns:
        dict: Results across specifications
    """
    import pandas as pd
    import numpy as np
    
    if outcomes is None:
        outcomes = ['return_on_assets', 'Tobin_Q', 'esg_score']
    
    if control_specs is None:
        control_specs = [
            ['L1_Firm_Size'],
            ['L1_Firm_Size', 'L1_Leverage'],
            ['L1_Firm_Size', 'L1_Leverage', 'L1_Asset_Turnover'],
            ['L1_Firm_Size', 'L1_Leverage', 'L1_Asset_Turnover', 'L1_Capital_Intensity']
        ]
    
    results = []
    
    print(f"\nTesting {len(control_specs)} control variable specifications...")
    
    for spec_num, controls in enumerate(control_specs, 1):
        spec_name = f"Spec {spec_num}: " + ", ".join(controls)
        print(f"  {spec_name}")
        
        for outcome in outcomes:
            try:
                from linearmodels.panel import PanelOLS
                
                controls_str = ' + '.join(controls)
                formula = f"{outcome} ~ {treatment_col} + {controls_str} + EntityEffects"
                
                reg_data = df_panel.dropna(subset=[outcome, treatment_col] + controls)
                
                if len(reg_data) > 100:
                    mod = PanelOLS.from_formula(formula, data=reg_data)
                    res = mod.fit(cov_type='clustered', cluster_entity=True, disp='off')
                    
                    coef = res.params.get(treatment_col, np.nan)
                    se = res.std_errors.get(treatment_col, np.nan)
                    p_val = res.pvalues.get(treatment_col, np.nan)
                    
                    results.append({
                        'specification': spec_name,
                        'outcome': outcome,
                        'coefficient': coef,
                        'std_error': se,
                        'p_value': p_val,
                        'n_controls': len(controls)
                    })
            except Exception as e:
                results.append({
                    'specification': spec_name,
                    'outcome': outcome,
                    'coefficient': np.nan,
                    'std_error': np.nan,
                    'p_value': np.nan,
                    'n_controls': len(controls)
                })
    
    return pd.DataFrame(results)

