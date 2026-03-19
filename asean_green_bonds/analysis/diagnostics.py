"""
Diagnostic and robustness check functions for ASEAN Green Bonds analysis.

Tests for assumption violations and robustness of econometric results.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional, List, Dict, Any
import warnings

# Suppress only specific expected warnings
warnings.filterwarnings('ignore', category=FutureWarning, module='linearmodels')


def placebo_test(
    df: pd.DataFrame,
    outcome: str,
    treatment_col: str = 'green_bond_active',
    entity_col: str = 'ric',
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
        Entity identifier (default: 'ric').
    time_col : str, optional
        Time identifier (default: 'Year').
    placebo_shift : int, optional
        Years to shift treatment timing (default: 1).
        
    Returns
    -------
    dict
        Placebo effect (should be near zero if DiD identifies true treatment effect).
    """
    from linearmodels.panel import PanelOLS
    
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
    
    try:
        model = PanelOLS(y, X, entity_effects=True, time_effects=False)
        results = model.fit(cov_type='clustered', cluster_entity=True)
        
        placebo_effect = results.params.iloc[0]
        placebo_se = results.std_errors.iloc[0]
        placebo_tstat = results.tstats.iloc[0]
        placebo_pval = results.pvalues.iloc[0]
        
        return {
            'test_name': 'placebo_test',
            'shift_years': placebo_shift,
            'placebo_coefficient': placebo_effect,
            'placebo_std_error': placebo_se,
            'placebo_t_statistic': placebo_tstat,
            'placebo_p_value': placebo_pval,
            'is_zero_at_5pct': abs(placebo_tstat) < 1.96,
            'n_observations': len(y),
        }
    except Exception as e:
        return {
            'test_name': 'placebo_test',
            'error': str(e),
        }


def leave_one_out_cv(
    df: pd.DataFrame,
    outcome: str,
    treatment_col: str = 'green_bond_active',
    entity_col: str = 'ric',
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
        Entity identifier (default: 'ric').
    time_col : str, optional
        Time identifier (default: 'Year').
        
    Returns
    -------
    dict
        LOOCV results: mean coefficient, SD across folds, range.
    """
    from linearmodels.panel import PanelOLS
    
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
        
        df_fold = df_fold.set_index([entity_col, time_col])
        
        X = df_fold[[treatment_col]]
        y = df_fold[outcome]
        
        # Align data properly
        df_aligned = pd.concat([X, y], axis=1).dropna()
        X = df_aligned[[treatment_col]]
        y = df_aligned[outcome]
        
        try:
            model = PanelOLS(y, X, entity_effects=True, time_effects=False)
            results = model.fit(cov_type='clustered', cluster_entity=True)
            coefficients.append(results.params.iloc[0])
        except (ValueError, np.linalg.LinAlgError) as e:
            # Skip this fold if estimation fails (singular matrix, insufficient data, etc.)
            warnings.warn(f"LOOCV fold estimation failed: {e}")
            continue
    
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
    entity_col: str = 'ric',
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
        Entity identifier (default: 'ric').
    time_col : str, optional
        Time identifier (default: 'Year').
    control_sets : list, optional
        List of control variable lists. If None, tests incremental specifications.
        
    Returns
    -------
    pd.DataFrame
        Coefficients and SEs across specifications.
    """
    from linearmodels.panel import PanelOLS
    
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
        df_reg = df_reg.set_index([entity_col, time_col])
        
        X = df_reg[regressors]
        y = df_reg[outcome]
        
        result_row = {
            'specification': f'Spec_{spec_num+1}',
            'n_controls': len(controls),
            'controls': ', '.join(controls) if controls else 'None',
            'coefficient': None,
            'std_error': None,
            't_statistic': None,
            'p_value': None,
            'r2_within': None,
            'n_obs': len(y),
            'error': None,
        }
        
        try:
            model = PanelOLS(y, X, entity_effects=True, time_effects=False)
            est = model.fit(cov_type='clustered', cluster_entity=True)
            
            result_row.update({
                'coefficient': est.params.iloc[0],
                'std_error': est.std_errors.iloc[0],
                't_statistic': est.tstats.iloc[0],
                'p_value': est.pvalues.iloc[0],
                'r2_within': est.rsquared_within,
            })
        except Exception as e:
            result_row['error'] = str(e)
        
        results.append(result_row)
    
    return pd.DataFrame(results)


def heterogeneous_effects_analysis(
    df: pd.DataFrame,
    outcome: str,
    treatment_col: str = 'green_bond_active',
    entity_col: str = 'ric',
    time_col: str = 'Year',
    heterogeneity_var: str = 'is_certified',
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
        Entity identifier (default: 'ric').
    time_col : str, optional
        Time identifier (default: 'Year').
    heterogeneity_var : str, optional
        Variable defining subgroups (default: 'is_certified').
        
    Returns
    -------
    dict
        Treatment effects by subgroup.
    """
    from linearmodels.panel import PanelOLS
    
    effects = {}
    
    if heterogeneity_var not in df.columns:
        return {'error': f'Variable {heterogeneity_var} not found'}
    
    for group_val in df[heterogeneity_var].unique():
        if pd.isna(group_val):
            continue
        
        df_group = df[df[heterogeneity_var] == group_val]
        df_group = df_group.set_index([entity_col, time_col])
        
        X = df_group[[treatment_col]]
        y = df_group[outcome]
        
        # Align data properly
        df_aligned = pd.concat([X, y], axis=1).dropna()
        X = df_aligned[[treatment_col]]
        y = df_aligned[outcome]
        
        try:
            model = PanelOLS(y, X, entity_effects=True, time_effects=False)
            results = model.fit(cov_type='clustered', cluster_entity=True)
            
            effects[f'{heterogeneity_var}_{group_val}'] = {
                'coefficient': results.params.iloc[0],
                'std_error': results.std_errors.iloc[0],
                't_statistic': results.tstats.iloc[0],
                'p_value': results.pvalues.iloc[0],
                'n_obs': len(y),
            }
        except Exception as e:
            effects[f'{heterogeneity_var}_{group_val}'] = {'error': str(e)}
    
    return effects


def run_diagnostics_battery(
    df: pd.DataFrame,
    outcome: str,
    treatment_col: str = 'green_bond_active',
    entity_col: str = 'ric',
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
        Entity identifier (default: 'ric').
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
