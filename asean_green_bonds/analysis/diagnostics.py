"""
Diagnostic and robustness check functions for ASEAN Green Bonds analysis.

Tests for assumption violations and robustness of econometric results.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional, List, Dict, Any
import warnings
from .difference_in_diff import estimate_did

# Suppress only specific expected warnings
warnings.filterwarnings('ignore', category=FutureWarning, module='linearmodels')


def placebo_test(
    df: pd.DataFrame,
    outcome: str,
    treatment_col: str = 'green_bond_active',
    entity_col: str = 'org_permid',
    time_col: str = 'Year',
    placebo_shift: int = 1,
) -> Dict[str, Any]:
    """
    Placebo test: Shift treatment timing and re-estimate (should have zero effect).
    
    Parameters
    ----------
    df : pd.DataFrame
        Panel data.
    outcome : str
        Outcome variable.
    treatment_col : str, optional
        Treatment column (default: 'green_bond_active').
    entity_col : str, optional
        Entity identifier (default: 'org_permid').
    time_col : str, optional
        Time identifier (default: 'Year').
    placebo_shift : int, optional
        Years to shift treatment timing (default: 1).
        
    Returns
    -------
    dict
        Placebo effect (should be near zero if DiD identifies true treatment effect).
    """
    df_placebo = df.copy()
    
    # Shift treatment forward in time
    df_placebo = df_placebo.sort_values([entity_col, time_col])
    df_placebo[f'{treatment_col}_placebo'] = df_placebo.groupby(entity_col)[
        treatment_col
    ].shift(-placebo_shift)
    
    # Set index for regression
    df_placebo = df_placebo.set_index([entity_col, time_col])
    
    # Regress outcome on placebo treatment
    X = df_placebo[[f'{treatment_col}_placebo']]
    y = df_placebo[outcome]
    
    # Align data properly
    df_aligned = pd.concat([X, y], axis=1).dropna()
    X = df_aligned[[f'{treatment_col}_placebo']]
    y = df_aligned[outcome]
    
    did_result = estimate_did(
        df_aligned.reset_index(),
        outcome=outcome,
        treatment_col=f'{treatment_col}_placebo',
        entity_col=entity_col,
        time_col=time_col,
        control_vars=[],
        specification='entity_fe',
        cluster_entity=True,
    )
    if 'error' in did_result:
        return {
            'test_name': 'placebo_test',
            'error': did_result['error'],
        }
    placebo_tstat = did_result.get('t_statistic', np.nan)
    return {
        'test_name': 'placebo_test',
        'shift_years': placebo_shift,
        'placebo_coefficient': did_result.get('coefficient', np.nan),
        'placebo_std_error': did_result.get('std_error', np.nan),
        'placebo_t_statistic': placebo_tstat,
        'placebo_p_value': did_result.get('p_value', np.nan),
        'is_zero_at_5pct': bool(abs(placebo_tstat) < 1.96) if not pd.isna(placebo_tstat) else False,
        'n_observations': int(did_result.get('n_obs', len(df_aligned))),
        'model_estimated': did_result.get('model_estimated', True),
        'absorbed_vars': did_result.get('absorbed_vars', []),
        'estimation_note': did_result.get('estimation_note'),
    }


def leave_one_out_cv(
    df: pd.DataFrame,
    outcome: str,
    treatment_col: str = 'green_bond_active',
    entity_col: str = 'org_permid',
    time_col: str = 'Year',
) -> Dict[str, Any]:
    """
    Leave-one-out cross-validation for DiD robustness.
    
    Tests whether results are driven by individual observations.
    
    Parameters
    ----------
    df : pd.DataFrame
        Panel data.
    outcome : str
        Outcome variable.
    treatment_col : str, optional
        Treatment column (default: 'green_bond_active').
    entity_col : str, optional
        Entity identifier (default: 'org_permid').
    time_col : str, optional
        Time identifier (default: 'Year').
        
    Returns
    -------
    dict
        LOOCV results: mean coefficient, SD across folds, range.
    """
    df_clean = df[[entity_col, time_col, outcome, treatment_col]].dropna()
    
    if len(df_clean) < 50:
        return {'error': 'Insufficient observations for LOOCV'}
    
    coefficients = []
    
    # Leave-one-out loop (sample version, not full LOOCV due to computational cost)
    n_folds = min(100, len(df_clean) // 10)
    
    for fold in range(n_folds):
        # Drop random subset (10% of data)
        drop_indices = np.random.choice(len(df_clean), size=max(1, len(df_clean)//10), replace=False)
        df_fold = df_clean.drop(df_clean.index[drop_indices])
        
        did_result = estimate_did(
            df_fold,
            outcome=outcome,
            treatment_col=treatment_col,
            entity_col=entity_col,
            time_col=time_col,
            control_vars=[],
            specification='entity_fe',
            cluster_entity=True,
        )
        if 'error' in did_result:
            warnings.warn(f"LOOCV fold estimation failed: {did_result['error']}")
            continue
        coef = did_result.get('coefficient', np.nan)
        if pd.isna(coef):
            continue
        coefficients.append(coef)
    
    if len(coefficients) > 1:
        mean_coef = np.mean(coefficients)
        std_coef = np.std(coefficients)
        # Robust if coefficient variation is low relative to mean (handle negative coefficients)
        robust = std_coef < abs(mean_coef) * 0.5 if mean_coef != 0 else std_coef < 0.1
        return {
            'test_name': 'leave_one_out_cv',
            'n_folds': len(coefficients),
            'mean_coefficient': mean_coef,
            'std_coefficient': std_coef,
            'min_coefficient': np.min(coefficients),
            'max_coefficient': np.max(coefficients),
            'robust': robust,
        }
    else:
        return {'test_name': 'leave_one_out_cv', 'error': 'Failed to complete folds'}


def specification_sensitivity(
    df: pd.DataFrame,
    outcome: str,
    treatment_col: str = 'green_bond_active',
    entity_col: str = 'org_permid',
    time_col: str = 'Year',
    control_sets: Optional[List[List[str]]] = None,
) -> pd.DataFrame:
    """
    Test sensitivity to different control variable specifications.
    
    Parameters
    ----------
    df : pd.DataFrame
        Panel data.
    outcome : str
        Outcome variable.
    treatment_col : str, optional
        Treatment column (default: 'green_bond_active').
    entity_col : str, optional
        Entity identifier (default: 'org_permid').
    time_col : str, optional
        Time identifier (default: 'Year').
    control_sets : list, optional
        List of control variable lists. If None, tests incremental specifications.
        
    Returns
    -------
    pd.DataFrame
        Coefficients and SEs across specifications.
    """
    if control_sets is None:
        control_sets = [
            [],  # No controls
            ['L1_Firm_Size'],  # Size only
            ['L1_Firm_Size', 'L1_Leverage'],  # Size + leverage
            ['L1_Firm_Size', 'L1_Leverage', 'L1_Asset_Turnover'],  # Three controls
            ['L1_Firm_Size', 'L1_Leverage', 'L1_Asset_Turnover', 'L1_Capital_Intensity'],  # Full
        ]
    
    results = []
    
    for spec_num, controls in enumerate(control_sets):
        regressors = [treatment_col] + controls
        regressors = [r for r in regressors if r in df.columns]
        
        df_reg = df[regressors + [entity_col, time_col, outcome]].dropna()
        
        result_row = {
            'specification': f'Spec_{spec_num+1}',
            'n_controls': len(controls),
            'controls': ', '.join(controls) if controls else 'None',
            'coefficient': None,
            'std_error': None,
            't_statistic': None,
            'p_value': None,
            'r2_within': None,
            'n_obs': len(df_reg),
            'error': None,
            'model_estimated': None,
            'absorbed_vars': [],
            'estimation_note': None,
        }
        did_result = estimate_did(
            df_reg,
            outcome=outcome,
            treatment_col=treatment_col,
            entity_col=entity_col,
            time_col=time_col,
            control_vars=controls,
            specification='entity_fe',
            cluster_entity=True,
        )
        if 'error' in did_result:
            result_row['error'] = did_result['error']
        else:
            result_row.update({
                'coefficient': did_result.get('coefficient'),
                'std_error': did_result.get('std_error'),
                't_statistic': did_result.get('t_statistic'),
                'p_value': did_result.get('p_value'),
                'r2_within': did_result.get('adj_r_squared'),
                'model_estimated': did_result.get('model_estimated', True),
                'absorbed_vars': did_result.get('absorbed_vars', []),
                'estimation_note': did_result.get('estimation_note'),
            })
        
        results.append(result_row)
    
    return pd.DataFrame(results)


def heterogeneous_effects_analysis(
    df: pd.DataFrame,
    outcome: str,
    treatment_col: str = 'green_bond_active',
    entity_col: str = 'org_permid',
    time_col: str = 'Year',
    heterogeneity_var: str = 'is_certified_majority',
    n_bins: int = 0,
) -> Dict[str, Any]:
    """
    Analyze treatment effect heterogeneity by subgroup.
    
    Parameters
    ----------
    df : pd.DataFrame
        Panel data.
    outcome : str
        Outcome variable.
    treatment_col : str, optional
        Treatment column (default: 'green_bond_active').
    entity_col : str, optional
        Entity identifier (default: 'org_permid').
    time_col : str, optional
        Time identifier (default: 'Year').
    heterogeneity_var : str, optional
        Variable defining subgroups (default: 'is_certified_majority').
    n_bins : int, optional
        If heterogeneity_var is continuous and n_bins > 1, split into quantile
        bins and estimate effects by bin (default: 0, disabled).
        
    Returns
    -------
    dict
        Treatment effects by subgroup.
    """
    effects = {}
    
    if heterogeneity_var not in df.columns:
        return {'error': f'Variable {heterogeneity_var} not found'}
    
    working_df = df.copy()
    group_var = heterogeneity_var
    if n_bins and n_bins > 1:
        non_na = working_df[heterogeneity_var].dropna()
        if non_na.nunique() >= n_bins:
            group_var = f'{heterogeneity_var}_bin'
            working_df[group_var] = pd.qcut(
                working_df[heterogeneity_var],
                q=n_bins,
                labels=False,
                duplicates='drop',
            )
    
    for group_val in working_df[group_var].unique():
        if pd.isna(group_val):
            continue
        
        df_group = working_df[working_df[group_var] == group_val]
        
        # Check for variation in treatment within the group
        if df_group[treatment_col].nunique() < 2:
            effects[f'{group_var}_{group_val}'] = {
                'error': f'Treatment variable {treatment_col} has no variation in this subgroup'
            }
            continue
            
        did_result = estimate_did(
            df_group,
            outcome=outcome,
            treatment_col=treatment_col,
            entity_col=entity_col,
            time_col=time_col,
            control_vars=[],
            specification='entity_fe',
            cluster_entity=True,
        )
        if 'error' in did_result:
            effects[f'{group_var}_{group_val}'] = {'error': did_result['error']}
        else:
            effects[f'{group_var}_{group_val}'] = {
                'coefficient': did_result.get('coefficient', np.nan),
                'std_error': did_result.get('std_error', np.nan),
                't_statistic': did_result.get('t_statistic', np.nan),
                'p_value': did_result.get('p_value', np.nan),
                'n_obs': did_result.get('n_obs', len(df_group)),
                'model_estimated': did_result.get('model_estimated', True),
                'absorbed_vars': did_result.get('absorbed_vars', []),
                'estimation_note': did_result.get('estimation_note'),
            }
    
    return effects


def detect_survivorship_bias(
    df: pd.DataFrame,
    entity_col: str = 'org_permid',
    time_col: str = 'Year',
    recent_years: Optional[List[int]] = None,
    early_years: Optional[List[int]] = None,
    existence_col: str = 'total_assets',
) -> pd.DataFrame:
    """
    Identifies potential survivorship bias by finding firms that disappear 
    before the end of the sample period.
    
    Parameters
    ----------
    df : pd.DataFrame
        Panel data.
    entity_col : str, optional
        Entity identifier (default: 'org_permid').
    time_col : str, optional
        Time identifier (default: 'Year').
    recent_years : list, optional
        Years to check for firm existence (default: [2023, 2024, 2025]).
    early_years : list, optional
        Years to check for initial firm existence (default: [2015, 2016, 2017]).
    existence_col : str, optional
        Column to check for non-null as existence proxy (default: 'total_assets').
        
    Returns
    -------
    pd.DataFrame
        Potential delisted/inactive firms with their last year of data.
    """
    if recent_years is None:
        recent_years = [2023, 2024, 2025]
    if early_years is None:
        early_years = [2015, 2016, 2017]
        
    def check_existence(group):
        has_early = group[group[time_col].isin(early_years)][existence_col].notna().any()
        has_recent = group[group[time_col].isin(recent_years)][existence_col].notna().any()
        last_year = group[group[existence_col].notna()][time_col].max()
        return pd.Series({
            'has_early_data': has_early,
            'has_recent_data': has_recent,
            'last_year_with_data': last_year
        })
        
    existence = df.groupby(entity_col).apply(check_existence)
    
    # Potential dead firms: had data in early years but none in recent years
    potential_dead_firms = existence[(existence['has_early_data']) & (~existence['has_recent_data'])]
    
    return potential_dead_firms


def run_diagnostics_battery(
    df: pd.DataFrame,
    outcome: str,
    treatment_col: str = 'green_bond_active',
    entity_col: str = 'org_permid',
    time_col: str = 'Year',
) -> Dict[str, Any]:
    """
    Run comprehensive diagnostics on DiD model.
    
    Parameters
    ----------
    df : pd.DataFrame
        Panel data.
    outcome : str
        Outcome variable.
    treatment_col : str, optional
        Treatment column (default: 'green_bond_active').
    entity_col : str, optional
        Entity identifier (default: 'org_permid').
    time_col : str, optional
        Time identifier (default: 'Year').
        
    Returns
    -------
    dict
        Comprehensive diagnostics report.
    """
    diagnostics = {}
    
    print("Running placebo test...")
    diagnostics['placebo'] = placebo_test(df, outcome, treatment_col, entity_col, time_col)
    
    print("Running specification sensitivity...")
    diagnostics['spec_sensitivity'] = specification_sensitivity(
        df, outcome, treatment_col, entity_col, time_col
    ).to_dict('records')
    
    print("Running leave-one-out CV...")
    diagnostics['loocv'] = leave_one_out_cv(df, outcome, treatment_col, entity_col, time_col)
    
    print("Analyzing heterogeneous effects...")
    diagnostics['heterogeneous_effects'] = heterogeneous_effects_analysis(
        df, outcome, treatment_col, entity_col, time_col
    )
    
    return diagnostics
