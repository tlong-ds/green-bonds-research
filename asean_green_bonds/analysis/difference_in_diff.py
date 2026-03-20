"""
Difference-in-Differences (DiD) estimation for causal effects.

Implements DiD regression with fixed effects and clustered standard errors.
"""

import pandas as pd
import numpy as np
from linearmodels.panel import PanelOLS, FirstDifferenceOLS
from linearmodels.panel.utility import AbsorbingEffectWarning
from typing import Tuple, Optional, List, Dict, Any
import warnings

# Suppress only specific expected warnings
warnings.filterwarnings('ignore', category=FutureWarning, module='linearmodels')
warnings.filterwarnings('ignore', category=AbsorbingEffectWarning, module='linearmodels')


def prepare_panel_for_regression(
    df: pd.DataFrame,
    entity_col: str = 'ric',
    time_col: str = 'Year',
    set_index: bool = True,
) -> pd.DataFrame:
    """
    Prepare panel data for regression analysis.
    
    Parameters
    ----------
    df : pd.DataFrame
        Unbalanced or irregular panel data.
    entity_col : str, optional
        Entity identifier column (default: 'ric').
    time_col : str, optional
        Time period column (default: 'Year').
    set_index : bool, optional
        If True, set MultiIndex (entity, time) (default: True).
        
    Returns
    -------
    pd.DataFrame
        Sorted, indexed panel ready for regression.
    """
    df = df.copy()
    
    # Ensure numeric time
    df[time_col] = pd.to_numeric(df[time_col], errors='coerce')
    
    # Sort by entity and time
    df = df.sort_values([entity_col, time_col])
    
    if set_index:
        df = df.set_index([entity_col, time_col])
    
    return df


def estimate_did(
    df: pd.DataFrame,
    outcome: str,
    treatment_col: str = 'green_bond_active',
    entity_col: str = 'ric',
    time_col: str = 'Year',
    control_vars: Optional[List[str]] = None,
    specification: str = 'entity_fe',
    cluster_entity: bool = True,
    survivorship_mode: str = 'ignore',
    survivorship_kwargs: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Estimate difference-in-differences treatment effect.
    
    Parameters
    ----------
    df : pd.DataFrame
        Panel data with outcome, treatment, and controls.
    outcome : str
        Outcome variable name.
    treatment_col : str, optional
        Treatment indicator column (default: 'green_bond_active').
    entity_col : str, optional
        Entity identifier (default: 'ric').
    time_col : str, optional
        Time period identifier (default: 'Year').
    control_vars : list, optional
        List of control variables. If None, uses defaults.
    specification : str, optional
        Model specification:
        - 'entity_fe': Entity fixed effects only
        - 'time_fe': Time fixed effects only
        - 'twoway_fe': Both entity and time fixed effects
        - 'none': No fixed effects, just time dummies
        (default: 'entity_fe')
    cluster_entity : bool, optional
        If True, cluster standard errors at entity level (default: True).
    survivorship_mode : str, optional
        Survivorship handling mode ('ignore', 'exclude', 'weight').
    survivorship_kwargs : dict, optional
        Additional arguments passed to data.prepare_analysis_sample.
        
    Returns
    -------
    dict
        Regression results including coefficient, std error, t-stat, p-value.
    """
    if survivorship_kwargs is None:
        survivorship_kwargs = {}
    
    if survivorship_mode != 'ignore':
        from ..data.processing import prepare_analysis_sample
        df = prepare_analysis_sample(
            df,
            survivorship_mode=survivorship_mode,
            firm_col=entity_col,
            time_col=time_col,
            **survivorship_kwargs,
        )
    
    if control_vars is None:
        control_vars = [
            'L1_Firm_Size', 'L1_Leverage', 'L1_Asset_Turnover',
            'L1_Capital_Intensity'
        ]
    
    # Prepare data
    df_reg = prepare_panel_for_regression(df, entity_col, time_col, set_index=True)
    
    # Build regressor list, filtering out variables not in data
    regressors = [treatment_col] + control_vars
    regressors = [r for r in regressors if r in df_reg.columns]
    
    # Remove control variables with zero variance
    regressors_with_variance = [treatment_col]  # Always keep treatment
    for var in regressors:
        if var == treatment_col:
            continue
        if var in df_reg.columns:
            var_std = df_reg[var].std()
            if var_std > 1e-10:  # Has some variance
                regressors_with_variance.append(var)
    
    regressors = regressors_with_variance
    
    # Check if treatment variable exists in regressors
    if treatment_col not in regressors:
        return {
            'error': f"Treatment variable '{treatment_col}' not found in data columns",
            'outcome': outcome,
            'specification': specification,
            'n_obs': 0,
        }
    
    # Check if outcome variable exists
    if outcome not in df_reg.columns:
        return {
            'error': f"Outcome variable '{outcome}' not found in data columns",
            'outcome': outcome,
            'specification': specification,
            'n_obs': 0,
            'available_columns': list(df_reg.columns[:20]),  # Show first 20 columns for debugging
        }
    
    required_cols = [*regressors, outcome]
    if survivorship_mode == 'weight' and 'survivorship_weight' in df_reg.columns:
        required_cols.append('survivorship_weight')
    
    # Drop missing values in regressors and outcome simultaneously
    df_clean = df_reg[required_cols].dropna()
    
    # Check minimum sample size
    if len(df_clean) < 10:
        return {
            'error': f"Insufficient observations after removing NaNs: {len(df_clean)}",
            'outcome': outcome,
            'specification': specification,
            'n_obs': len(df_clean),
        }
    
    X = df_clean[regressors]
    y = df_clean[outcome]
    weights = None
    if survivorship_mode == 'weight' and 'survivorship_weight' in df_clean.columns:
        weights = df_clean['survivorship_weight']
    
    # Check for and remove collinear variables using VIF and correlation
    def remove_collinear_features(X, threshold=0.90, keep_col=None):
        """
        Remove highly correlated features, preserving keep_col.
        Uses pairwise correlation to detect and remove collinear features.
        """
        X_numeric = X.select_dtypes(include=[np.number])
        
        if len(X_numeric.columns) <= 1:
            return X, []
        
        corr_matrix = X_numeric.corr().abs()
        
        # Find pairs of highly correlated features
        to_drop = set()
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                col_i = corr_matrix.columns[i]
                col_j = corr_matrix.columns[j]
                
                if corr_matrix.iloc[i, j] > threshold:
                    # Drop the second one unless it's the keep_col
                    if keep_col and col_i == keep_col:
                        to_drop.add(col_j)
                    elif keep_col and col_j == keep_col:
                        to_drop.add(col_i)
                    else:
                        # Drop the one with higher average correlation
                        avg_corr_i = corr_matrix[col_i].mean()
                        avg_corr_j = corr_matrix[col_j].mean()
                        if avg_corr_i > avg_corr_j:
                            to_drop.add(col_i)
                        else:
                            to_drop.add(col_j)
        
        to_drop = list(to_drop)
        return X.drop(columns=to_drop), to_drop
    
    # Remove collinear features but keep treatment variable  
    X_clean, dropped_cols = remove_collinear_features(X, threshold=0.90, keep_col=treatment_col)
    
    if dropped_cols:
        regressors = [r for r in regressors if r not in dropped_cols]
        X = X_clean
    
    # Additional check: ensure treatment variable has variation
    if treatment_col in X.columns:
        treatment_var = X[treatment_col].var()
        if treatment_var == 0 or np.isnan(treatment_var):
            return {
                'error': f"Treatment variable '{treatment_col}' has no variation",
                'outcome': outcome,
                'specification': specification,
                'n_obs': len(y),
            }
    
    n_entities = len(df_reg.index.get_level_values(0).unique())
    n_periods = len(df_reg.index.get_level_values(1).unique())

    def _build_absorbed_result(absorbed_vars: Optional[List[str]] = None, note: Optional[str] = None) -> Dict[str, Any]:
        absorbed_list = list(dict.fromkeys(absorbed_vars or regressors))
        return {
            'outcome': outcome,
            'treatment': treatment_col,
            'specification': specification,
            'coefficient': np.nan,
            'std_error': np.nan,
            't_statistic': np.nan,
            'p_value': np.nan,
            'r_squared': np.nan,
            'adj_r_squared': np.nan,
            'n_obs': len(y),
            'n_entities': n_entities,
            'n_periods': n_periods,
            'confidence_interval': (np.nan, np.nan),
            'significant_5pct': False,
            'significant_10pct': False,
            'dropped_collinear_vars': dropped_cols if dropped_cols else [],
            'absorbed_vars': absorbed_list,
            'treatment_absorbed': treatment_col in absorbed_list,
            'model_estimated': False,
            'estimation_note': note or 'all_exogenous_variables_absorbed',
            'survivorship_mode': survivorship_mode,
        }

    # Fit model based on specification
    cov_type = 'clustered' if cluster_entity else 'robust'
    cov_kwargs = {'cluster_entity': True} if cluster_entity else {}
    
    try:
        if specification == 'entity_fe':
            model = PanelOLS(
                y, X, entity_effects=True, time_effects=False,
                check_rank=False, drop_absorbed=True, weights=weights
            )
        elif specification == 'time_fe':
            model = PanelOLS(
                y, X, entity_effects=False, time_effects=True,
                check_rank=False, drop_absorbed=True, weights=weights
            )
        elif specification == 'twoway_fe':
            model = PanelOLS(
                y, X, entity_effects=True, time_effects=True,
                check_rank=False, drop_absorbed=True, weights=weights
            )
        else:  # 'none'
            # Add time dummies manually - using indices from cleaned data
            time_dummies = pd.get_dummies(y.index.get_level_values(time_col), drop_first=True)
            time_dummies.index = y.index
            # Use concat instead of join to avoid cartesian product with non-unique indices
            X = pd.concat([X, time_dummies], axis=1)
            model = PanelOLS(
                y, X, entity_effects=False, time_effects=False,
                check_rank=False, drop_absorbed=True, weights=weights
            )
    except Exception as e:
        err_msg = str(e).lower()
        if 'fully absorbed' in err_msg or 'all columns in exog' in err_msg:
            return _build_absorbed_result(note=str(e))
        return {
            'error': f"Model creation failed: {str(e)}",
            'outcome': outcome,
            'specification': specification,
            'n_obs': len(y),
        }
    
    # Estimate
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', AbsorbingEffectWarning)
            results = model.fit(cov_type=cov_type, **cov_kwargs)
    except Exception as e:
        err_msg = str(e).lower()
        if 'fully absorbed' in err_msg or 'all columns in exog' in err_msg:
            return _build_absorbed_result(note=str(e))
        if cluster_entity and ('float division by zero' in err_msg or 'division by zero' in err_msg):
            # Fallback when clustered covariance fails due degenerate clusters.
            try:
                results = model.fit(cov_type='robust')
            except Exception as e2:
                err2 = str(e2).lower()
                if 'float division by zero' in err2 or 'division by zero' in err2:
                    return _build_absorbed_result(note=f"{str(e)}; robust_fallback_failed: {str(e2)}")
                if 'fully absorbed' in err2 or 'all columns in exog' in err2:
                    return _build_absorbed_result(note=str(e2))
                return {
                    'error': str(e2),
                    'outcome': outcome,
                    'specification': specification,
                    'n_obs': len(y),
                }
        else:
            return {
                'error': str(e),
                'outcome': outcome,
                'specification': specification,
                'n_obs': len(y),
            }
    
    model_exog = getattr(results.model, "exog", None)
    retained_vars = list(getattr(model_exog, "vars", [])) if model_exog is not None else []
    absorbed_vars = [v for v in regressors if v not in retained_vars]
    if not retained_vars:
        return _build_absorbed_result(absorbed_vars=absorbed_vars, note='all_exogenous_variables_absorbed')

    treatment_absorbed = treatment_col in absorbed_vars or treatment_col not in results.params.index

    # Extract treatment coefficient
    if treatment_col in results.params.index:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', RuntimeWarning)
            coef = results.params[treatment_col]
            se = results.std_errors[treatment_col]
            t_stat = results.tstats[treatment_col]
            p_value = results.pvalues[treatment_col]
    else:
        coef = np.nan
        se = np.nan
        t_stat = np.nan
        p_value = np.nan

    return {
        'outcome': outcome,
        'treatment': treatment_col,
        'specification': specification,
        'coefficient': coef,
        'std_error': se,
        't_statistic': t_stat,
        'p_value': p_value,
        'r_squared': results.rsquared,  # Use rsquared instead of r2
        'adj_r_squared': results.rsquared_within,  # Use rsquared_within instead of r2_within
        'n_obs': len(y),
        'n_entities': n_entities,
        'n_periods': n_periods,
        'confidence_interval': (
            np.nan if pd.isna(coef) or pd.isna(se) else coef - 1.96 * se,
            np.nan if pd.isna(coef) or pd.isna(se) else coef + 1.96 * se,
        ),
        'significant_5pct': bool(abs(t_stat) > 1.96) if not pd.isna(t_stat) else False,
        'significant_10pct': bool(abs(t_stat) > 1.645) if not pd.isna(t_stat) else False,
        'dropped_collinear_vars': dropped_cols if dropped_cols else [],
        'absorbed_vars': absorbed_vars,
        'treatment_absorbed': treatment_absorbed,
        'model_estimated': True,
        'estimation_note': None,
        'survivorship_mode': survivorship_mode,
    }


def run_multiple_outcomes(
    df: pd.DataFrame,
    outcomes: List[str],
    treatment_col: str = 'green_bond_active',
    entity_col: str = 'ric',
    time_col: str = 'Year',
    control_vars: Optional[List[str]] = None,
    specifications: Optional[List[str]] = None,
    survivorship_mode: str = 'ignore',
    survivorship_kwargs: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """
    Estimate DiD for multiple outcomes and specifications.
    
    Parameters
    ----------
    df : pd.DataFrame
        Panel data.
    outcomes : list
        List of outcome variables.
    treatment_col : str, optional
        Treatment indicator (default: 'green_bond_active').
    entity_col : str, optional
        Entity identifier (default: 'ric').
    time_col : str, optional
        Time identifier (default: 'Year').
    control_vars : list, optional
        Control variables.
    specifications : list, optional
        Specifications to test. If None, tests all 4.
    survivorship_mode : str, optional
        Survivorship handling mode ('ignore', 'exclude', 'weight').
    survivorship_kwargs : dict, optional
        Additional arguments passed to data.prepare_analysis_sample.
        
    Returns
    -------
    pd.DataFrame
        Results table with coefficients, SEs, t-stats, p-values.
    """
    if specifications is None:
        specifications = ['entity_fe', 'time_fe', 'twoway_fe', 'none']
    
    results = []
    errors = []
    
    for outcome in outcomes:
        for spec in specifications:
            result = estimate_did(
                df=df,
                outcome=outcome,
                treatment_col=treatment_col,
                entity_col=entity_col,
                time_col=time_col,
                control_vars=control_vars,
                specification=spec,
                cluster_entity=True,
                survivorship_mode=survivorship_mode,
                survivorship_kwargs=survivorship_kwargs,
            )
            
            if 'error' not in result:
                results.append(result)
            else:
                # Collect errors for reporting
                errors.append({
                    'outcome': outcome,
                    'specification': spec,
                    'error': result['error']
                })
    
    # Print errors if any
    if errors:
        print(f"\n⚠️  Warning: {len(errors)} model(s) failed to estimate:")
        for err in errors[:5]:  # Show first 5 errors
            print(f"  - {err['outcome']} ({err['specification']}): {err['error']}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors")
    
    return pd.DataFrame(results)


def calculate_moulton_factor(
    df: pd.DataFrame,
    outcome: str,
    entity_col: str = 'ric',
    time_col: str = 'Year',
    treatment_col: str = 'green_bond_active',
) -> float:
    """
    Calculate Moulton factor for clustered standard errors.
    
    Moulton factor = sqrt(1 + (average cluster size - 1) * ICC)
    where ICC = intra-cluster correlation of treatment residuals.
    
    Parameters
    ----------
    df : pd.DataFrame
        Panel data.
    outcome : str
        Outcome variable.
    entity_col : str, optional
        Entity/cluster identifier (default: 'ric').
    time_col : str, optional
        Time identifier (default: 'Year').
    treatment_col : str, optional
        Treatment column (default: 'green_bond_active').
        
    Returns
    -------
    float
        Moulton factor for SE inflation due to clustering.
    """
    df_clean = df[[entity_col, time_col, outcome, treatment_col]].dropna()
    
    # Get residuals from simple model
    from sklearn.linear_model import LinearRegression
    X = df_clean[[treatment_col]].values
    y = df_clean[outcome].values
    model = LinearRegression()
    model.fit(X, y)
    residuals = y - model.predict(X)
    
    # Group by entity
    df_clean['residuals'] = residuals
    grouped = df_clean.groupby(entity_col)
    
    # Calculate ICC
    total_var = np.var(residuals)
    between_var = grouped['residuals'].mean().var() * len(df_clean) / len(grouped)
    within_var = grouped['residuals'].apply(np.var).mean()
    
    icc = between_var / (between_var + within_var) if (between_var + within_var) > 0 else 0
    
    # Average cluster size
    avg_cluster_size = len(df_clean) / len(grouped)
    
    # Moulton factor
    moulton = np.sqrt(1 + (avg_cluster_size - 1) * icc)
    
    return moulton


def parallel_trends_test(
    df: pd.DataFrame,
    outcome: str,
    treatment_col: str = 'green_bond_active',
    entity_col: str = 'ric',
    time_col: str = 'Year',
    leads: int = 3,
    lags: int = 3,
) -> Dict[str, Any]:
    """
    Test parallel trends assumption via leads/lags analysis.
    
    Parameters
    ----------
    df : pd.DataFrame
        Panel data with treatment and outcome.
    outcome : str
        Outcome variable.
    treatment_col : str, optional
        Treatment column (default: 'green_bond_active').
    entity_col : str, optional
        Entity identifier (default: 'ric').
    time_col : str, optional
        Time identifier (default: 'Year').
    leads : int, optional
        Number of leads to test (default: 3).
    lags : int, optional
        Number of lags to test (default: 3).
        
    Returns
    -------
    dict
        Coefficients and p-values for each lead/lag period.
    """
    from linearmodels.panel import PanelOLS
    
    df_reg = prepare_panel_for_regression(df, entity_col, time_col, set_index=True)
    
    # Create lead/lag indicators
    for lead in range(1, leads + 1):
        col_name = f'treatment_lead_{lead}'
        df_reg[col_name] = df_reg.groupby(level=0)[treatment_col].shift(lead)
    
    for lag in range(1, lags + 1):
        col_name = f'treatment_lag_{lag}'
        df_reg[col_name] = df_reg.groupby(level=0)[treatment_col].shift(-lag)
    
    # Regress outcome on leads/lags
    lead_lag_cols = [f'treatment_lead_{i}' for i in range(1, leads+1)] + \
                    [treatment_col] + \
                    [f'treatment_lag_{i}' for i in range(1, lags+1)]
    
    # Prepare data with proper alignment
    X = df_reg[lead_lag_cols]
    y = df_reg[outcome]
    
    # Drop rows with missing values in either X or y
    df_aligned = pd.concat([X, y], axis=1).dropna()
    X = df_aligned[lead_lag_cols]
    y = df_aligned[outcome]
    
    # Initialize with full requested design so downstream consumers always see all keys.
    pt_results = {
        'specification': 'parallel_trends',
        'leads_tested': leads,
        'lags_tested': lags,
        'coefficients': {col: np.nan for col in lead_lag_cols},
        'p_values': {col: np.nan for col in lead_lag_cols},
        'absorbed_vars': [],
        'model_estimated': False,
        'estimation_note': None,
    }
    
    if df_aligned.empty:
        pt_results['estimation_note'] = 'no_observations_after_alignment'
        return pt_results
    
    try:
        model = PanelOLS(
            y, X, entity_effects=True, time_effects=False,
            check_rank=False, drop_absorbed=True
        )
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', AbsorbingEffectWarning)
            results = model.fit(cov_type='clustered', cluster_entity=True)
    except Exception as e:
        err_msg = str(e).lower()
        if 'float division by zero' in err_msg or 'division by zero' in err_msg:
            # Degenerate clustered covariance can happen in small/irregular panels.
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore', AbsorbingEffectWarning)
                    results = model.fit(cov_type='robust')
            except Exception as e2:
                pt_results['estimation_note'] = str(e2)
                return pt_results
        else:
            pt_results['estimation_note'] = str(e)
            return pt_results
    
    retained_vars = list(results.params.index)
    pt_results['absorbed_vars'] = [col for col in lead_lag_cols if col not in retained_vars]
    
    try:
        pvalues = results.pvalues
    except Exception:
        pvalues = pd.Series(dtype=float)
    
    for col in retained_vars:
        if col in pt_results['coefficients']:
            pt_results['coefficients'][col] = results.params.get(col, np.nan)
            pt_results['p_values'][col] = pvalues.get(col, np.nan)
    
    pt_results['model_estimated'] = True
    return pt_results
