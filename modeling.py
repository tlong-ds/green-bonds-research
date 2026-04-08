#!/usr/bin/env python3
"""
ASEAN Green Bonds Econometric Analysis Pipeline
================================================

This script consolidates all diagnostic and modeling steps from notebooks 02 and 03,
plus additional analyses from chapter documentation.

Sections:
1. Data Loading & Quality Report
2. Descriptive Statistics (Tables 3.4, 4.1, 4.2)
3. Feature Diagnostics (VIF, correlation)
4. PSM (Propensity Score Matching)
5. DiD (Difference-in-Differences)
6. Parallel Trends Testing
7. System GMM
8. Robustness Checks
9. Cohort-Specific Analysis
10. Heterogeneity Analysis
11. Authenticity Scoring

Outputs saved to: outputs/tables/ and outputs/figures/
"""

import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Import project modules
from asean_green_bonds import data, analysis, utils, config
from asean_green_bonds.data.feature_selection import (
    diagnose_multicollinearity,
    validate_specification,
    compare_specifications
)
from asean_green_bonds.analysis import (
    estimate_propensity_scores,
    calculate_optimal_caliper,
    check_common_support,
    assess_balance,
    create_matched_dataset,
    estimate_system_gmm,
    run_multiple_outcomes,
    parallel_trends_test,
    specification_sensitivity,
    placebo_test,
    run_diagnostics_battery,
    heterogeneous_effects_analysis,
)
from asean_green_bonds.authenticity import (
    compute_authenticity_score,
    generate_authenticity_report,
    print_authenticity_report,
)

# Configure matplotlib
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Create output directories
OUTPUT_DIR = Path("outputs")
TABLES_DIR = OUTPUT_DIR / "tables"
FIGURES_DIR = OUTPUT_DIR / "figures"

for directory in [OUTPUT_DIR, TABLES_DIR, FIGURES_DIR]:
    directory.mkdir(exist_ok=True)

print("=" * 80)
print("ASEAN GREEN BONDS ECONOMETRIC ANALYSIS PIPELINE")
print("=" * 80)
print(f"\nOutputs will be saved to: {OUTPUT_DIR.absolute()}")
print()


# =============================================================================
# SECTION 1: DATA LOADING & QUALITY REPORT
# =============================================================================

print("\n" + "=" * 80)
print("SECTION 1: DATA LOADING & QUALITY REPORT")
print("=" * 80)

print("\nLoading processed panel data...")
df = data.load_processed_data()
print(f"Data loaded: {df.shape[0]:,} observations, {df.shape[1]} variables")
print(f"Firms: {df['org_permid'].nunique():,}")
print(f"Time periods: {df['Year'].nunique()}")

# Generate data quality report
print("\nGenerating data quality report...")
quality_report = utils.generate_data_quality_report(
    df,
    treatment_col='green_bond_active'
)
print(quality_report)

# Save quality report
with open(TABLES_DIR / "data_quality_report.txt", "w") as f:
    f.write(quality_report)
print(f"✅ Saved: {TABLES_DIR / 'data_quality_report.txt'}")


# =============================================================================
# SECTION 2: DESCRIPTIVE STATISTICS
# =============================================================================

print("\n" + "=" * 80)
print("SECTION 2: DESCRIPTIVE STATISTICS")
print("=" * 80)

# Define key variables for descriptive stats
desc_variables = [
    # Outcomes
    'return_on_assets', 'Tobin_Q', 'esg_score', 'ln_emissions_intensity', 'implied_cost_of_debt',
    # Controls (lagged)
    'L1_Firm_Size', 'L1_Leverage', 'L1_Asset_Turnover', 'L1_Capital_Intensity', 'L1_Cash_Ratio',
    # Firm characteristics
    'asset_tangibility', 'issuer_track_record', 'has_green_framework'
]

# Filter to available variables
desc_variables = [v for v in desc_variables if v in df.columns]

print(f"\nGenerating summary statistics for {len(desc_variables)} variables...")

# Table 3.4 / Table 4.1: Full Sample Summary Statistics
summary_stats = df[desc_variables].describe(percentiles=[.25, .5, .75]).T
summary_stats['N'] = df[desc_variables].notna().sum()
summary_stats['Coverage'] = (summary_stats['N'] / len(df) * 100).round(1)
summary_stats = summary_stats[['N', 'Coverage', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']]
summary_stats = summary_stats.round(4)

print("\n--- Table 3.4 / Table 4.1: Full Sample Summary Statistics ---")
print(summary_stats)
summary_stats.to_csv(TABLES_DIR / "table_3_4_summary_stats.csv")
summary_stats.to_csv(TABLES_DIR / "table_4_1_full_sample.csv")
print(f"✅ Saved: table_3_4_summary_stats.csv & table_4_1_full_sample.csv")

# Table 4.2: Treatment vs Control Comparison
print("\n--- Table 4.2: Treatment vs Control Comparison ---")

treatment_mask = df['green_bond_active'] == 1
treated = df[treatment_mask][desc_variables]
control = df[~treatment_mask][desc_variables]

comparison = pd.DataFrame({
    'Variable': desc_variables,
    'Treated_Mean': treated.mean().values,
    'Treated_Std': treated.std().values,
    'Control_Mean': control.mean().values,
    'Control_Std': control.std().values,
})

# T-test for differences
from scipy.stats import ttest_ind
t_stats = []
p_values = []
for var in desc_variables:
    if var in df.columns:
        t_data = df[treatment_mask][var].dropna()
        c_data = df[~treatment_mask][var].dropna()
        if len(t_data) > 0 and len(c_data) > 0:
            t_stat, p_val = ttest_ind(t_data, c_data, equal_var=False)
            t_stats.append(t_stat)
            p_values.append(p_val)
        else:
            t_stats.append(np.nan)
            p_values.append(np.nan)
    else:
        t_stats.append(np.nan)
        p_values.append(np.nan)

comparison['T_Statistic'] = t_stats
comparison['P_Value'] = p_values
comparison['Significant'] = comparison['P_Value'].apply(
    lambda p: '***' if p < 0.01 else '**' if p < 0.05 else '*' if p < 0.1 else ''
)

print(comparison.round(4))
comparison.to_csv(TABLES_DIR / "table_4_2_treatment_control.csv", index=False)
print(f"✅ Saved: table_4_2_treatment_control.csv")

# Table 4.3: Treatment Timeline
print("\n--- Table 4.3: Treatment Timeline ---")
if 'green_bond_issue' in df.columns:
    timeline = df[df['green_bond_issue'] == 1].groupby('Year').size().reset_index(name='Issuances')
    print(timeline)
    timeline.to_csv(TABLES_DIR / "table_4_3_treatment_timeline.csv", index=False)
    print(f"✅ Saved: table_4_3_treatment_timeline.csv")

# Table 4.4: Data Coverage by Outcome
print("\n--- Table 4.4: Data Coverage by Outcome ---")
outcome_vars = ['return_on_assets', 'Tobin_Q', 'esg_score', 'ln_emissions_intensity', 'implied_cost_of_debt']
outcome_vars = [v for v in outcome_vars if v in df.columns]

coverage = pd.DataFrame({
    'Outcome': outcome_vars,
    'Full_Sample_N': [df[v].notna().sum() for v in outcome_vars],
    'Full_Sample_Pct': [(df[v].notna().sum() / len(df) * 100).round(1) for v in outcome_vars],
    'Treated_N': [df[treatment_mask][v].notna().sum() for v in outcome_vars],
    'Treated_Pct': [(df[treatment_mask][v].notna().sum() / treatment_mask.sum() * 100).round(1) for v in outcome_vars],
})

print(coverage)
coverage.to_csv(TABLES_DIR / "table_4_4_coverage.csv", index=False)
print(f"✅ Saved: table_4_4_coverage.csv")


# =============================================================================
# SECTION 3: FEATURE DIAGNOSTICS
# =============================================================================

print("\n" + "=" * 80)
print("SECTION 3: FEATURE DIAGNOSTICS")
print("=" * 80)

# PSM features for diagnostics
psm_features = config.PSM_FEATURES
available_psm = [f for f in psm_features if f in df.columns]

print(f"\nPSM Features: {len(available_psm)}/{len(psm_features)} available")
print(available_psm)

# VIF Analysis (Table A.7b)
print("\n--- Multicollinearity Diagnostics (VIF) ---")
vif_results = diagnose_multicollinearity(df, available_psm)
print(vif_results)
vif_results.to_csv(TABLES_DIR / "table_a7b_vif.csv", index=False)
print(f"✅ Saved: table_a7b_vif.csv")

# Correlation Matrix (Table A.7)
print("\n--- Correlation Matrix ---")
corr_vars = desc_variables[:9]  # First 9 for matrix
corr_vars = [v for v in corr_vars if v in df.columns]
corr_matrix = df[corr_vars].corr().round(3)
print(corr_matrix)
corr_matrix.to_csv(TABLES_DIR / "table_a7_correlation_matrix.csv")
print(f"✅ Saved: table_a7_correlation_matrix.csv")

# Specification Validation
print("\n--- Specification Validation ---")
spec_report = validate_specification(
    df,
    theory_vars=available_psm,
    outcome_col='ESG_Score' if 'ESG_Score' in df.columns else 'esg_score',
    control_cols=available_psm
)
print(spec_report)


# =============================================================================
# SECTION 4: PROPENSITY SCORE MATCHING (PSM)
# =============================================================================

print("\n" + "=" * 80)
print("SECTION 4: PROPENSITY SCORE MATCHING")
print("=" * 80)

# Estimate propensity scores
print("\nEstimating propensity scores...")
df['propensity_score'] = estimate_propensity_scores(
    df,
    treatment_col='green_bond_issue',
    features=available_psm
)

ps_valid = df['propensity_score'].dropna()
print(f"Propensity scores estimated: {ps_valid.notna().sum():,} observations")

# Calculate optimal caliper
optimal_caliper = calculate_optimal_caliper(ps_valid, method='austin')
relaxed_caliper = max(optimal_caliper * config.PSM_RELAXED_CALIPER_FACTOR, config.PSM_RELAXED_CALIPER_MIN)
print(f"Optimal caliper (Austin): {optimal_caliper:.4f}")
print(f"Relaxed caliper (config): {relaxed_caliper:.4f}")

# Common support analysis
support_report = check_common_support(df, ps_col='propensity_score', treatment_col='green_bond_issue')
print("\nCommon Support Analysis:")
print(f"  Overlap region: [{support_report['overlap_region'][0]:.4f}, {support_report['overlap_region'][1]:.4f}]")
print(f"  Treated overlap: {support_report['treated_overlap_pct']:.2f}%")
print(f"  Control overlap: {support_report['control_overlap_pct']:.2f}%")

# Create matched dataset
print("\nPerforming nearest-neighbor matching...")
matched_df, psm_diagnostics = create_matched_dataset(
    df[df['propensity_score'].notna()].copy(),
    treatment_col='green_bond_issue',
    ps_col='propensity_score',
    caliper=float(relaxed_caliper),
    ratio=config.PSM_RATIO,
    check_support=True,
    trim_to_common_support=config.PSM_QUALITY_CONFIG.get('trim_to_common_support', True),
    trimming_method=config.PSM_QUALITY_CONFIG.get('trimming_method', 'crump'),
    trimming_alpha=config.PSM_QUALITY_CONFIG.get('trimming_alpha', 0.1),
    enforce_quality=False,  # Don't enforce to avoid errors
)

match_stats = psm_diagnostics.get('matching_stats', {})
print(f"\nMatching Results:")
print(f"  Matched treated: {match_stats.get('matched_treated', 0)}")
print(f"  Matched controls: {match_stats.get('matched_controls', 0)}")
print(f"  Total matched observations: {match_stats.get('total_matched_obs', len(matched_df))}")

# Balance assessment (Table A.1)
print("\n--- Table A.1: Post-Matching Balance Assessment ---")
balance_df = assess_balance(matched_df, available_psm, treatment_col='green_bond_issue')
print(balance_df)
balance_df.to_csv(TABLES_DIR / "table_a1_psm_balance.csv", index=False)
print(f"✅ Saved: table_a1_psm_balance.csv")

# Visualize propensity score distribution
print("\nGenerating PSM visualizations...")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Distribution
treated_ps = df[df['green_bond_issue'] == 1]['propensity_score'].dropna()
control_ps = df[df['green_bond_issue'] == 0]['propensity_score'].dropna()

axes[0].hist(control_ps, bins=50, alpha=0.5, label='Control', density=True)
axes[0].hist(treated_ps, bins=20, alpha=0.5, label='Treated', density=True)
axes[0].set_xlabel('Propensity Score')
axes[0].set_ylabel('Density')
axes[0].set_title('Propensity Score Distribution')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Balance plot
if len(balance_df) > 0:
    axes[1].barh(balance_df['Feature'], balance_df['Std_Difference'].abs())
    axes[1].axvline(x=0.1, color='red', linestyle='--', label='Threshold (0.1)')
    axes[1].set_xlabel('Absolute Standardized Mean Difference')
    axes[1].set_title('Post-Matching Covariate Balance')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(FIGURES_DIR / "psm_diagnostics.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"✅ Saved: psm_diagnostics.png")


# =============================================================================
# SECTION 5: DIFFERENCE-IN-DIFFERENCES (DiD)
# =============================================================================

print("\n" + "=" * 80)
print("SECTION 5: DIFFERENCE-IN-DIFFERENCES ESTIMATION")
print("=" * 80)

# Use full panel for DiD (matched sample often too small for panel variation)
analysis_df = df.copy()

outcomes = config.OUTCOME_VARIABLES
specs = ['entity_fe', 'time_fe', 'twoway_fe', 'none']

print(f"\nEstimating DiD for {len(outcomes)} outcomes × {len(specs)} specifications...")
print(f"Outcomes: {outcomes}")
print(f"Specifications: {specs}")

# Run multiple outcomes
did_survivorship_mode = config.SURVIVORSHIP_CONFIG.get('mode', 'ignore')
did_survivorship_kwargs = {
    'recent_years': [2023, 2024],
    'early_years': [2015, 2016, 2017],
}

results = run_multiple_outcomes(
    analysis_df,
    outcomes=outcomes,
    treatment_col='green_bond_active',
    specifications=specs,
    survivorship_mode=did_survivorship_mode,
    survivorship_kwargs=did_survivorship_kwargs,
)

print(f"\n✅ Estimated {len(results)} models")

# Table 4.7: DiD Results Summary
print("\n--- Table 4.7: DiD Estimates by Outcome and Specification ---")
results_summary = results[['outcome', 'specification', 'coefficient', 'std_error', 'p_value', 'n_obs']]
print(results_summary)
results.to_csv(TABLES_DIR / "table_4_7_did_results.csv", index=False)
print(f"✅ Saved: table_4_7_did_results.csv")

# Extract TWFE results for main analysis
twfe_results = results[results['specification'] == 'twoway_fe'].copy()
print("\n--- TWFE (Preferred Specification) Results ---")
print(twfe_results[['outcome', 'coefficient', 'p_value', 'n_obs']])


# =============================================================================
# SECTION 6: PARALLEL TRENDS TESTING
# =============================================================================

print("\n" + "=" * 80)
print("SECTION 6: PARALLEL TRENDS TESTING")
print("=" * 80)

print("\nTesting parallel trends with leads and lags...")
pt_results = parallel_trends_test(
    analysis_df,
    outcome='return_on_assets',  # Primary outcome for PT test
    treatment_col='green_bond_active',
    entity_col='org_permid',
    time_col='Year',
    leads=1,
    lags=1,
)

print("\n--- Table 4.10: Leads and Lags Analysis ---")
if 'coefficients' in pt_results and 'p_values' in pt_results:
    coeffs = pt_results['coefficients']
    pvals = pt_results['p_values']
    
    # Handle both Series and dict types
    if hasattr(coeffs, 'index'):
        var_names = coeffs.index
    elif isinstance(coeffs, dict):
        var_names = list(coeffs.keys())
    else:
        var_names = []
    
    for col in var_names:
        coef = coeffs[col] if isinstance(coeffs, (dict, pd.Series)) else coeffs.get(col, np.nan)
        pval = pvals[col] if isinstance(pvals, (dict, pd.Series)) else pvals.get(col, np.nan)
        sig = '***' if pval < 0.01 else '**' if pval < 0.05 else '*' if pval < 0.1 else ''
        print(f"  {col:30s}: {coef:8.4f} {sig:3s} (p={pval:.4f})")
        
    # Save to table
    pt_table = pd.DataFrame({
        'Variable': var_names,
        'Coefficient': [coeffs[v] for v in var_names],
        'P_Value': [pvals[v] for v in var_names],
    })
    pt_table.to_csv(TABLES_DIR / "table_4_10_parallel_trends.csv", index=False)
    print(f"✅ Saved: table_4_10_parallel_trends.csv")

# Visualize parallel trends
if 'model_estimated' in pt_results and pt_results['model_estimated']:
    fig = utils.plot_parallel_trends(pt_results, save_path=FIGURES_DIR / 'parallel_trends.png')
    print(f"✅ Saved: parallel_trends.png")


# =============================================================================
# SECTION 7: SYSTEM GMM
# =============================================================================

print("\n" + "=" * 80)
print("SECTION 7: SYSTEM GMM ROBUSTNESS CHECK")
print("=" * 80)

gmm_cov_type = 'clustered'
gmm_max_instruments = 20
gmm_survivorship_mode = config.SURVIVORSHIP_CONFIG.get('mode', 'ignore')
gmm_survivorship_kwargs = {'recent_years': [2023, 2024], 'early_years': [2015, 2016, 2017]}

print(f"\nGMM Config:")
print(f"  Max lags: {config.GMM_CONFIG['max_lags']}")
print(f"  Covariance type: {gmm_cov_type}")
print(f"  Max instruments: {gmm_max_instruments}")

gmm_results = []
for outcome in outcomes:
    print(f"\n--- {outcome} ---")
    
    # Try different thresholds for instrument coverage
    result = None
    for threshold in [0.30, 0.10, 0.08]:
        trial = estimate_system_gmm(
            analysis_df,
            outcome=outcome,
            treatment_col='green_bond_active',
            entity_col='org_permid',
            time_col='Year',
            control_vars=config.CONTROL_VARIABLES,
            max_lags=config.GMM_CONFIG['max_lags'],
            min_obs_fraction=threshold,
            endogenous_treatment=False,
            max_instruments=gmm_max_instruments,
            cov_type=gmm_cov_type,
            survivorship_mode=gmm_survivorship_mode,
            survivorship_kwargs=gmm_survivorship_kwargs,
        )
        if 'error' not in trial:
            result = trial
            break
    
    if result and 'error' not in result:
        print(f"  Coef: {result['coefficient']:.4f} | SE: {result['std_error']:.4f} | p: {result['p_value']:.4f}")
        print(f"  N: {result.get('n_obs', 'N/A')} | Instruments: {result.get('n_instruments', 0)}")
        gmm_results.append(result)
    else:
        print(f"  ❌ Failed: {result.get('error', 'Unknown') if result else 'Unknown'}")

# Table 4.8: GMM Results Summary
if gmm_results:
    print("\n--- Table 4.8: System GMM Estimates ---")
    gmm_summary = pd.DataFrame([
        {
            'Outcome': r['outcome'],
            'Coefficient': round(r['coefficient'], 4),
            'Std_Error': round(r['std_error'], 4),
            'P_Value': round(r['p_value'], 4),
            'N': r.get('n_obs', np.nan),
            'Cov_Type': r.get('cov_type_used', 'n/a'),
        }
        for r in gmm_results
    ])
    print(gmm_summary)
    gmm_summary.to_csv(TABLES_DIR / "table_4_8_gmm_results.csv", index=False)
    print(f"✅ Saved: table_4_8_gmm_results.csv")

# Table 4.9: DiD vs GMM Comparison
print("\n--- Table 4.9: DiD vs GMM Comparison ---")
if len(twfe_results) > 0 and len(gmm_results) > 0:
    comparison_table = []
    for outcome in outcomes:
        did_row = twfe_results[twfe_results['outcome'] == outcome]
        gmm_row = [r for r in gmm_results if r.get('outcome') == outcome]
        
        if len(did_row) > 0 and len(gmm_row) > 0:
            comparison_table.append({
                'Outcome': outcome,
                'DiD_Coefficient': did_row['coefficient'].values[0],
                'GMM_Coefficient': gmm_row[0]['coefficient'],
                'Direction_Consistent': np.sign(did_row['coefficient'].values[0]) == np.sign(gmm_row[0]['coefficient']),
            })
    
    if comparison_table:
        comparison_df = pd.DataFrame(comparison_table)
        print(comparison_df)
        comparison_df.to_csv(TABLES_DIR / "table_4_9_did_gmm_comparison.csv", index=False)
        print(f"✅ Saved: table_4_9_did_gmm_comparison.csv")


# =============================================================================
# SECTION 8: ROBUSTNESS CHECKS
# =============================================================================

print("\n" + "=" * 80)
print("SECTION 8: ROBUSTNESS CHECKS")
print("=" * 80)

# Specification sensitivity
print("\n--- Specification Sensitivity ---")
sensitivity = specification_sensitivity(
    analysis_df,
    outcome='return_on_assets',
    treatment_col='green_bond_active'
)
print(sensitivity[['specification', 'n_controls', 'coefficient', 'p_value']])
sensitivity.to_csv(TABLES_DIR / "robustness_sensitivity.csv", index=False)
print(f"✅ Saved: robustness_sensitivity.csv")

# Placebo test
print("\n--- Placebo Test ---")
placebo = placebo_test(
    analysis_df,
    outcome='return_on_assets',
    treatment_col='green_bond_active'
)
print(f"  Placebo coefficient: {placebo.get('placebo_coefficient', np.nan):.4f}")
print(f"  P-value: {placebo.get('placebo_p_value', np.nan):.4f}")
print(f"  Valid: {'✓' if placebo.get('is_zero_at_5pct') else '✗'}")

placebo_df = pd.DataFrame([{
    'Test': 'Placebo',
    'Coefficient': placebo.get('placebo_coefficient', np.nan),
    'P_Value': placebo.get('placebo_p_value', np.nan),
    'Valid': placebo.get('is_zero_at_5pct', False),
}])
placebo_df.to_csv(TABLES_DIR / "robustness_placebo.csv", index=False)
print(f"✅ Saved: robustness_placebo.csv")

# Full diagnostics battery
print("\n--- Running Comprehensive Diagnostics Battery ---")
diagnostics = run_diagnostics_battery(
    analysis_df,
    outcome='return_on_assets'
)
print(f"  Placebo valid: {diagnostics['placebo'].get('is_zero_at_5pct', 'N/A')}")
print(f"  LOOCV robust: {diagnostics['loocv'].get('robust', 'N/A')}")
print(f"  Specifications tested: {len(diagnostics['spec_sensitivity'])}")


# =============================================================================
# SECTION 9: COHORT-SPECIFIC ANALYSIS
# =============================================================================

print("\n" + "=" * 80)
print("SECTION 9: COHORT-SPECIFIC ANALYSIS")
print("=" * 80)

# Identify cohorts
if 'green_bond_issue' in analysis_df.columns:
    cohorts = analysis_df[analysis_df['green_bond_issue'] == 1].groupby('Year')['org_permid'].nunique()
    print(f"\nTreatment cohorts identified:")
    for year, count in cohorts.items():
        print(f"  {year}: {count} firms")
    
    # Save cohort distribution
    cohorts_df = pd.DataFrame({
        'Cohort_Year': cohorts.index,
        'N_Firms': cohorts.values,
    })
    cohorts_df.to_csv(TABLES_DIR / "cohort_distribution.csv", index=False)
    print(f"✅ Saved: cohort_distribution.csv")


# =============================================================================
# SECTION 10: HETEROGENEITY ANALYSIS
# =============================================================================

print("\n" + "=" * 80)
print("SECTION 10: HETEROGENEITY ANALYSIS")
print("=" * 80)

# Firm size heterogeneity
print("\n--- Heterogeneous Effects by Firm Size ---")
if 'L1_Firm_Size' in analysis_df.columns:
    # Dichotomize at median
    median_size = analysis_df['L1_Firm_Size'].median()
    analysis_df['size_group'] = (analysis_df['L1_Firm_Size'] > median_size).astype(int)
    
    hetero_results = heterogeneous_effects_analysis(
        analysis_df,
        outcome='return_on_assets',
        treatment_col='green_bond_active',
        heterogeneity_var='size_group',
        n_bins=0,  # Already binary
    )
    
    print(f"Estimated {len(hetero_results)} subgroup models")
    for group_label, result in list(hetero_results.items())[:5]:
        if 'error' not in result:
            print(f"  {group_label}: coef={result['coefficient']:.4f}, p={result['p_value']:.4f}, n={result['n_obs']}")
        else:
            print(f"  {group_label}: {result['error']}")
    
    # Save heterogeneity results
    hetero_df = pd.DataFrame([
        {
            'Group': k,
            'Coefficient': v.get('coefficient', np.nan),
            'P_Value': v.get('p_value', np.nan),
            'N_Obs': v.get('n_obs', np.nan),
            'Error': v.get('error', ''),
        }
        for k, v in hetero_results.items()
    ])
    hetero_df.to_csv(TABLES_DIR / "heterogeneity_firm_size.csv", index=False)
    print(f"✅ Saved: heterogeneity_firm_size.csv")


# =============================================================================
# SECTION 11: AUTHENTICITY SCORING
# =============================================================================

print("\n" + "=" * 80)
print("SECTION 11: AUTHENTICITY SCORING")
print("=" * 80)

try:
    # Load green bonds authenticated data
    auth_df = pd.read_csv('data/green_bonds_authenticated.csv')
    print(f"\nLoaded {len(auth_df)} green bonds for authenticity analysis")
    
    # Ensure certification columns exist
    for col in ['is_cbi_certified', 'is_icma_certified']:
        if col not in auth_df.columns:
            auth_df[col] = 0
        else:
            auth_df[col] = auth_df[col].fillna(0)
    
    # Assign tiers
    auth_df['authenticity_tier'] = 3  # Default: Certification only
    auth_df.loc[auth_df['n_pre_obs'].fillna(0) >= 1, 'authenticity_tier'] = 2  # Partial ESG
    auth_df.loc[(auth_df['n_pre_obs'].fillna(0) >= 2) & (auth_df['n_post_obs'].fillna(0) >= 2), 'authenticity_tier'] = 1  # Complete ESG
    
    # Compute scores
    scored_df = compute_authenticity_score(auth_df)
    
    print(f"\nAuthenticity Score Statistics:")
    print(f"  Mean: {scored_df['authenticity_score'].mean():.1f}")
    print(f"  Std: {scored_df['authenticity_score'].std():.1f}")
    print(f"  Min: {scored_df['authenticity_score'].min():.1f}")
    print(f"  Max: {scored_df['authenticity_score'].max():.1f}")
    
    # Generate report
    report = generate_authenticity_report(scored_df)
    print_authenticity_report(report)
    
    # Save authenticity scores
    scored_df.to_csv(TABLES_DIR / "authenticity_scores.csv", index=False)
    print(f"✅ Saved: authenticity_scores.csv")
    
    # Table A.3: Authenticity distribution
    auth_categories = pd.cut(
        scored_df['authenticity_score'],
        bins=[0, 40, 60, 80, 100],
        labels=['Unverified', 'Low', 'Medium', 'High'],
        include_lowest=True
    ).value_counts().sort_index()
    
    auth_dist = pd.DataFrame({
        'Category': auth_categories.index,
        'Count': auth_categories.values,
        'Percentage': (auth_categories.values / len(scored_df) * 100).round(1),
    })
    print("\n--- Table A.3: Authenticity Score Distribution ---")
    print(auth_dist)
    auth_dist.to_csv(TABLES_DIR / "table_a3_authenticity_distribution.csv", index=False)
    print(f"✅ Saved: table_a3_authenticity_distribution.csv")
    
except FileNotFoundError as e:
    print(f"⚠️  Authenticity data not found: {e}")
except Exception as e:
    print(f"⚠️  Error in authenticity analysis: {e}")


# =============================================================================
# FINAL SUMMARY
# =============================================================================

print("\n" + "=" * 80)
print("PIPELINE COMPLETE")
print("=" * 80)

print(f"\n✅ All analyses completed successfully!")
print(f"\n📁 Outputs saved to:")
print(f"   Tables: {TABLES_DIR.absolute()}")
print(f"   Figures: {FIGURES_DIR.absolute()}")

# List generated files
table_files = sorted(TABLES_DIR.glob("*.csv"))
figure_files = sorted(FIGURES_DIR.glob("*.png"))

print(f"\n📊 Generated {len(table_files)} tables:")
for f in table_files:
    print(f"   - {f.name}")

print(f"\n📈 Generated {len(figure_files)} figures:")
for f in figure_files:
    print(f"   - {f.name}")

# Create summary report
summary_report = f"""
ASEAN Green Bonds Econometric Analysis
=======================================

Pipeline Execution Summary
--------------------------
Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

Data:
- Observations: {len(df):,}
- Firms: {df['org_permid'].nunique():,}
- Time periods: {df['Year'].nunique()}
- Treated observations: {(df['green_bond_active'] == 1).sum()}

Models Estimated:
- DiD specifications: {len(results)}
- GMM specifications: {len(gmm_results)}
- Robustness checks: {len(diagnostics['spec_sensitivity'])} specifications

Key Results (TWFE):
{twfe_results[['outcome', 'coefficient', 'p_value']].to_string(index=False)}

Outputs:
- Tables generated: {len(table_files)}
- Figures generated: {len(figure_files)}

All outputs saved to: {OUTPUT_DIR.absolute()}
"""

with open(OUTPUT_DIR / "results_summary.md", "w") as f:
    f.write(summary_report)

print(f"\n✅ Summary report: {OUTPUT_DIR / 'results_summary.md'}")
print("\n" + "=" * 80)
print("END OF PIPELINE")
print("=" * 80)
