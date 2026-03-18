"""
Difference-in-Differences (DiD) estimation for causal effects.

Implements DiD regression with fixed effects and clustered standard errors.
"""

import pandas as pd
import numpy as np
from linearmodels.panel import PanelOLS, FirstDifferenceOLS
from typing import Tuple, Optional, List, Dict
import warnings

warnings.filterwarnings('ignore')


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
) -> Dict[str, any]:
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
        
    Returns
    -------
    dict
        Regression results including coefficient, std error, t-stat, p-value.
    """
    if control_vars is None:
        control_vars = [
            'L1_Firm_Size', 'L1_Leverage', 'L1_Asset_Turnover',
            'L1_Capital_Intensity'
        ]
    
    # Prepare data
    df_reg = prepare_panel_for_regression(df, entity_col, time_col, set_index=True)
    
    # Build regressor list
    regressors = [treatment_col] + control_vars
    regressors = [r for r in regressors if r in df_reg.columns]
    
    X = df_reg[regressors].dropna()
    y = df_reg.loc[X.index, outcome]
    
    # Drop missing outcomes
    valid_idx = y.notna()
    X = X[valid_idx]
    y = y[valid_idx]
    
    # Fit model based on specification
    cov_type = 'clustered' if cluster_entity else 'robust'
    cov_kwargs = {'cluster_entity': True} if cluster_entity else {}
    
    if specification == 'entity_fe':
        model = PanelOLS(y, X, entity_effects=True, time_effects=False)
    elif specification == 'time_fe':
        model = PanelOLS(y, X, entity_effects=False, time_effects=True)
    elif specification == 'twoway_fe':
        model = PanelOLS(y, X, entity_effects=True, time_effects=True)
    else:  # 'none'
        # Add time dummies manually
        time_dummies = pd.get_dummies(df_reg.index.get_level_values(time_col), drop_first=True)
        time_dummies.index = df_reg.index
        X = X.join(time_dummies)
        model = PanelOLS(y, X, entity_effects=False, time_effects=False)
    
    # Estimate
    try:
        results = model.fit(cov_type=cov_type, **cov_kwargs)
    except Exception as e:
        return {
            'error': str(e),
            'outcome': outcome,
            'specification': specification,
            'n_obs': len(y),
        }
    
    # Extract treatment coefficient
    if treatment_col in results.params.index:
        coef = results.params[treatment_col]
        se = results.std_errors[treatment_col]
        t_stat = results.tstats[treatment_col]
        p_value = results.pvalues[treatment_col]
    else:
        # Treatment variable not in results, return error
        return {
            'error': f"Treatment variable '{treatment_col}' not found in model results",
            'outcome': outcome,
            'specification': specification,
            'n_obs': len(y),
        }
    
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
        'n_entities': len(df_reg.index.get_level_values(0).unique()),
        'n_periods': len(df_reg.index.get_level_values(1).unique()),
        'confidence_interval': (coef - 1.96*se, coef + 1.96*se),
        'significant_5pct': abs(t_stat) > 1.96,
        'significant_10pct': abs(t_stat) > 1.645,
    }


def run_multiple_outcomes(
    df: pd.DataFrame,
    outcomes: List[str],
    treatment_col: str = 'green_bond_active',
    entity_col: str = 'ric',
    time_col: str = 'Year',
    control_vars: Optional[List[str]] = None,
    specifications: Optional[List[str]] = None,
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
        
    Returns
    -------
    pd.DataFrame
        Results table with coefficients, SEs, t-stats, p-values.
    """
    if specifications is None:
        specifications = ['entity_fe', 'time_fe', 'twoway_fe', 'none']
    
    results = []
    
    for outcome in outcomes:
        for spec in specifications:
            result = estimate_did(
                df, outcome, treatment_col, entity_col, time_col,
                control_vars, spec
            )
            
            if 'error' not in result:
                results.append(result)
    
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
) -> Dict[str, any]:
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
    
    X = df_reg[lead_lag_cols].dropna()
    y = df_reg.loc[X.index, outcome].dropna()
    X = X[y.index]
    
    model = PanelOLS(y, X, entity_effects=True, time_effects=False)
    results = model.fit(cov_type='clustered', cluster_entity=True)
    
    # Organize results
    pt_results = {
        'specification': 'parallel_trends',
        'leads_tested': leads,
        'lags_tested': lags,
        'coefficients': {},
        'p_values': {},
    }
    
    for i, col in enumerate(lead_lag_cols):
        pt_results['coefficients'][col] = results.beta.iloc[i]
        pt_results['p_values'][col] = results.pvalues.iloc[i]
    
    return pt_results
