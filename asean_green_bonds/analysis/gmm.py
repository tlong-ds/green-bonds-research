"""
System GMM estimation for dynamic panel models.

Implements Arellano-Bond and Blundell-Bond estimators for robustness checks
when lagged dependent variables are included in the model.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from scipy import stats
import warnings

warnings.filterwarnings('ignore', category=FutureWarning, module='linearmodels')


def select_gmm_instruments(
    df: pd.DataFrame,
    outcome: str,
    entity_col: str = 'ric',
    time_col: str = 'Year',
    max_lags: int = 3,
    min_obs_fraction: float = 0.3,
) -> List[str]:
    """
    Automatically select valid instruments based on data availability.
    
    Creates lagged variables L2_{outcome}, L3_{outcome}, etc.
    Only includes lags with sufficient non-missing observations.
    
    Parameters
    ----------
    df : pd.DataFrame
        Panel data with entity and time identifiers.
    outcome : str
        Outcome variable name to create lags for.
    entity_col : str, optional
        Entity identifier column (default: 'ric').
    time_col : str, optional
        Time period column (default: 'Year').
    max_lags : int, optional
        Maximum number of lags to consider (default: 3).
    min_obs_fraction : float, optional
        Minimum fraction of non-missing observations required (default: 0.3).
        
    Returns
    -------
    List[str]
        List of valid lagged instrument column names that have been added to df.
    """
    if outcome not in df.columns:
        return []
    
    valid_instruments = []
    n_total = len(df)
    
    # Sort data for proper lagging
    df_sorted = df.sort_values([entity_col, time_col])
    
    # Start from lag 2 (lag 1 is typically included as regressor in dynamic panel)
    for lag in range(2, max_lags + 1):
        col_name = f'L{lag}_{outcome}'
        
        # Create lagged variable within each entity
        lagged = df_sorted.groupby(entity_col)[outcome].shift(lag)
        
        # Check observation coverage
        n_valid = lagged.notna().sum()
        coverage = n_valid / n_total
        
        if coverage >= min_obs_fraction:
            df[col_name] = lagged.values
            valid_instruments.append(col_name)
    
    return valid_instruments


def _select_lagged_instruments_for_variable(
    df: pd.DataFrame,
    variable: str,
    entity_col: str = 'ric',
    time_col: str = 'Year',
    max_lags: int = 3,
    min_obs_fraction: float = 0.3,
) -> List[str]:
    """Create lagged instruments L2..Lk for a single variable when coverage is adequate."""
    if variable not in df.columns:
        return []
    
    valid_instruments = []
    n_total = len(df)
    df_sorted = df.sort_values([entity_col, time_col])
    
    for lag in range(2, max_lags + 1):
        col_name = f'L{lag}_{variable}'
        lagged = df_sorted.groupby(entity_col)[variable].shift(lag)
        coverage = lagged.notna().sum() / n_total
        if coverage >= min_obs_fraction:
            df[col_name] = lagged.values
            valid_instruments.append(col_name)
    
    return valid_instruments


def _prepare_gmm_data(
    df: pd.DataFrame,
    outcome: str,
    treatment_col: str,
    entity_col: str,
    time_col: str,
    control_vars: Optional[List[str]],
    instruments: Optional[List[str]],
    max_lags: int,
    min_obs_fraction: float = 0.3,
    endogenous_treatment: bool = False,
) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Prepare data for GMM estimation.
    
    Returns (prepared_df, error_message). If error_message is not None,
    prepared_df will be None.
    """
    df = df.copy()
    
    # Check required columns
    required = [outcome, treatment_col, entity_col, time_col]
    missing = [c for c in required if c not in df.columns]
    if missing:
        return None, f"Missing required columns: {missing}"
    
    # Sort by entity and time
    df = df.sort_values([entity_col, time_col])
    
    # Create lagged dependent variable (L1)
    df[f'L1_{outcome}'] = df.groupby(entity_col)[outcome].shift(1)
    
    # Select or generate instruments
    if instruments is None:
        instruments = _select_lagged_instruments_for_variable(
            df, outcome, entity_col, time_col, max_lags, min_obs_fraction
        )
        if endogenous_treatment:
            treatment_instruments = _select_lagged_instruments_for_variable(
                df, treatment_col, entity_col, time_col, max_lags, min_obs_fraction
            )
            instruments = instruments + treatment_instruments
    
    if len(instruments) == 0:
        return None, "No valid instruments available"
    
    # Build variable list
    if control_vars is None:
        control_vars = []
    
    # Filter to existing columns
    control_vars = [c for c in control_vars if c in df.columns]
    instruments = [i for i in instruments if i in df.columns]
    
    # Keep only needed columns
    keep_cols = [entity_col, time_col, outcome, f'L1_{outcome}', 
                 treatment_col] + control_vars + instruments
    keep_cols = list(dict.fromkeys(keep_cols))  # Remove duplicates
    
    df_clean = df[[c for c in keep_cols if c in df.columns]].dropna()
    
    if len(df_clean) < 20:
        return None, f"Insufficient observations after removing NaNs: {len(df_clean)}"
    
    # Store metadata
    df_clean.attrs['instruments'] = instruments
    df_clean.attrs['control_vars'] = control_vars
    df_clean.attrs['lagged_dep'] = f'L1_{outcome}'
    
    return df_clean, None


def arellano_bond_test(
    residuals: pd.Series,
    entity_col: str,
    time_col: str,
    order: int = 2,
) -> Dict[str, float]:
    """
    Arellano-Bond test for serial correlation in first-differenced residuals.
    
    H0: No serial correlation of order `order`
    For valid GMM, AR(1) should be significant, AR(2) should NOT be significant.
    
    Parameters
    ----------
    residuals : pd.Series
        Residuals from GMM estimation with MultiIndex (entity, time).
    entity_col : str
        Entity identifier column name.
    time_col : str
        Time identifier column name.
    order : int, optional
        Order of serial correlation to test (default: 2).
        
    Returns
    -------
    dict
        Dictionary with 'statistic' and 'p_value'.
    """
    if not isinstance(residuals.index, pd.MultiIndex):
        return {
            'statistic': np.nan,
            'p_value': np.nan,
            'error': 'Residuals must have MultiIndex (entity, time)'
        }
    
    try:
        # Get entity and time from index
        entities = residuals.index.get_level_values(0)
        times = residuals.index.get_level_values(1)
        
        resid_df = pd.DataFrame({
            'entity': entities,
            'time': times,
            'resid': residuals.values
        })
        
        # First difference residuals within entity
        resid_df = resid_df.sort_values(['entity', 'time'])
        resid_df['d_resid'] = resid_df.groupby('entity')['resid'].diff()
        
        # Lag the differenced residuals
        resid_df[f'd_resid_lag{order}'] = resid_df.groupby('entity')['d_resid'].shift(order)
        
        # Drop missing
        df_test = resid_df[['d_resid', f'd_resid_lag{order}']].dropna()
        
        if len(df_test) < 10:
            return {
                'statistic': np.nan,
                'p_value': np.nan,
                'error': f'Insufficient observations for AR({order}) test'
            }
        
        # Calculate correlation
        numerator = (df_test['d_resid'] * df_test[f'd_resid_lag{order}']).sum()
        denominator_sq = (df_test['d_resid'] ** 2).sum() * (df_test[f'd_resid_lag{order}'] ** 2).sum()
        
        if denominator_sq <= 0:
            return {
                'statistic': np.nan,
                'p_value': np.nan,
                'error': 'Zero variance in residuals'
            }
        
        # Test statistic (asymptotically N(0,1))
        z_stat = numerator / np.sqrt(denominator_sq)
        p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
        
        return {
            'statistic': float(z_stat),
            'p_value': float(p_value)
        }
    
    except Exception as e:
        return {
            'statistic': np.nan,
            'p_value': np.nan,
            'error': str(e)
        }


def sargan_hansen_test(
    residuals: pd.Series,
    instruments: pd.DataFrame,
    n_params: int,
) -> Dict[str, float]:
    """
    Sargan/Hansen J-test for overidentifying restrictions.
    
    H0: All instruments are valid (orthogonal to error term)
    
    Parameters
    ----------
    residuals : pd.Series
        Residuals from GMM estimation.
    instruments : pd.DataFrame
        Instrument matrix used in estimation.
    n_params : int
        Number of estimated parameters.
        
    Returns
    -------
    dict
        Dictionary with 'statistic', 'df', 'p_value'.
    """
    try:
        # Align residuals and instruments
        common_idx = residuals.index.intersection(instruments.index)
        if len(common_idx) < 10:
            return {
                'statistic': np.nan,
                'df': np.nan,
                'p_value': np.nan,
                'error': 'Insufficient common observations'
            }
        
        resid = residuals.loc[common_idx].values
        Z = instruments.loc[common_idx].values
        
        n = len(resid)
        k = Z.shape[1]  # Number of instruments
        
        # Degrees of freedom = overidentification
        df = k - n_params
        
        if df <= 0:
            return {
                'statistic': np.nan,
                'df': 0,
                'p_value': np.nan,
                'error': 'Model is not overidentified'
            }
        
        # J = n * (e'Z(Z'Z)^{-1}Z'e) / (e'e)
        ZtZ = Z.T @ Z
        
        # Add small regularization for numerical stability
        ZtZ_reg = ZtZ + 1e-8 * np.eye(k)
        
        try:
            ZtZ_inv = np.linalg.inv(ZtZ_reg)
        except np.linalg.LinAlgError:
            return {
                'statistic': np.nan,
                'df': df,
                'p_value': np.nan,
                'error': 'Singular instrument matrix'
            }
        
        Zte = Z.T @ resid
        j_stat = n * (Zte.T @ ZtZ_inv @ Zte) / (resid.T @ resid)
        p_value = 1 - stats.chi2.cdf(j_stat, df)
        
        return {
            'statistic': float(j_stat),
            'df': int(df),
            'p_value': float(p_value)
        }
    
    except Exception as e:
        return {
            'statistic': np.nan,
            'df': np.nan,
            'p_value': np.nan,
            'error': str(e)
        }


def estimate_system_gmm(
    df: pd.DataFrame,
    outcome: str,
    treatment_col: str = 'green_bond_active',
    entity_col: str = 'ric',
    time_col: str = 'Year',
    control_vars: Optional[List[str]] = None,
    instruments: Optional[List[str]] = None,
    max_lags: int = 2,
    min_obs_fraction: float = 0.3,
    endogenous_treatment: bool = False,
    max_instruments: Optional[int] = 20,
    cov_type: str = 'clustered',
    survivorship_mode: str = 'ignore',
    survivorship_kwargs: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Estimate System GMM model for dynamic panel.
    
    Uses lagged levels as instruments for differences equation and
    lagged differences as instruments for levels equation.
    
    Parameters
    ----------
    df : pd.DataFrame
        Panel data with outcome, treatment, and controls.
    outcome : str
        Dependent variable name.
    treatment_col : str, optional
        Treatment indicator column (default: 'green_bond_active').
    entity_col : str, optional
        Entity identifier column (default: 'ric').
    time_col : str, optional
        Time period column (default: 'Year').
    control_vars : list, optional
        List of control variables. If None, uses defaults.
    instruments : list, optional
        Custom instruments (if None, uses automatic lag selection).
    max_lags : int, optional
        Maximum lags for automatic instrument generation (default: 2).
    min_obs_fraction : float, optional
        Minimum non-missing fraction for lag instrument retention when
        instruments are auto-generated (default: 0.3).
    endogenous_treatment : bool, optional
        If True, treat treatment as endogenous and instrument it with lagged
        treatment values (default: False).
    max_instruments : int, optional
        Optional hard cap on number of instruments retained (default: 20).
    cov_type : str, optional
        Covariance type for inference. Supports 'clustered' and 'robust'.
        Defaults to 'clustered' with robust fallback when unavailable.
    survivorship_mode : str, optional
        Survivorship handling mode passed to data.prepare_analysis_sample:
        'ignore' (default), 'exclude', or 'weight'.
    survivorship_kwargs : dict, optional
        Additional arguments passed to data.prepare_analysis_sample.
        
    Returns
    -------
    dict
        Results dictionary with keys:
        - coefficient, std_error, t_statistic, p_value (for treatment)
        - sargan_pvalue : p-value for Sargan/Hansen J-test
        - ar1_pvalue, ar2_pvalue : Arellano-Bond serial correlation tests
        - n_obs, n_instruments
        - error (if estimation fails)
    """
    # Import here to handle import errors gracefully
    try:
        from linearmodels.iv import IVGMM
    except ImportError:
        return {
            'error': 'linearmodels not installed. Run: pip install linearmodels',
            'outcome': outcome,
            'n_obs': 0,
        }
    
    # Default control variables
    if control_vars is None:
        control_vars = [
            'L1_Firm_Size', 'L1_Leverage', 'L1_Asset_Turnover',
            'L1_Capital_Intensity'
        ]
    
    if survivorship_kwargs is None:
        survivorship_kwargs = {}
    
    # Optional survivorship handling before model prep
    if survivorship_mode != 'ignore':
        from ..data.processing import prepare_analysis_sample
        df = prepare_analysis_sample(
            df,
            survivorship_mode=survivorship_mode,
            firm_col=entity_col,
            time_col=time_col,
            **survivorship_kwargs,
        )
    
    # Prepare data
    df_prep, error = _prepare_gmm_data(
        df, outcome, treatment_col, entity_col, time_col,
        control_vars, instruments, max_lags, min_obs_fraction, endogenous_treatment
    )
    
    if error is not None:
        return {
            'error': error,
            'outcome': outcome,
            'n_obs': 0,
        }
    
    # Get metadata
    instr_cols = df_prep.attrs.get('instruments', [])
    ctrl_vars = df_prep.attrs.get('control_vars', [])
    lagged_dep = df_prep.attrs.get('lagged_dep')
    
    # Set index for panel structure
    df_reg = df_prep.set_index([entity_col, time_col])
    
    # Check treatment variation
    if treatment_col in df_reg.columns:
        if df_reg[treatment_col].var() < 1e-10:
            return {
                'error': f"Treatment variable '{treatment_col}' has no variation",
                'outcome': outcome,
                'n_obs': len(df_reg),
            }
    
    # Build regression components
    # Dependent variable
    y = df_reg[outcome]
    
    # Endogenous variables
    endog_cols = [lagged_dep] if lagged_dep in df_reg.columns else []
    if endogenous_treatment and treatment_col in df_reg.columns:
        endog_cols.append(treatment_col)
    endog = df_reg[endog_cols] if len(endog_cols) > 0 else None
    
    # Exogenous: treatment + controls
    exog_cols = [c for c in [treatment_col] + ctrl_vars if c in df_reg.columns]
    if endogenous_treatment:
        exog_cols = [c for c in exog_cols if c != treatment_col]
    exog_cols = list(dict.fromkeys(exog_cols))  # Remove duplicates
    
    # Filter out columns not in df_reg
    exog_cols = [c for c in exog_cols if c in df_reg.columns]
    
    if len(exog_cols) == 0:
        return {
            'error': 'No exogenous variables available',
            'outcome': outcome,
            'n_obs': len(df_reg),
        }
    
    exog = df_reg[exog_cols]
    
    # Add constant
    exog = exog.copy()
    exog['const'] = 1.0
    
    # Instruments
    instr_cols_valid = [c for c in instr_cols if c in df_reg.columns]
    if max_instruments is not None and max_instruments > 0:
        instr_cols_valid = instr_cols_valid[:max_instruments]
    if len(instr_cols_valid) == 0:
        return {
            'error': 'No valid instruments in data',
            'outcome': outcome,
            'n_obs': len(df_reg),
        }
    
    instruments_df = df_reg[instr_cols_valid]
    
    # Remove rows with any NaN
    all_cols = list(set([outcome] + endog_cols + exog_cols + instr_cols_valid))
    all_cols = [c for c in all_cols if c in df_reg.columns]
    mask = df_reg[all_cols].notna().all(axis=1)
    
    y_clean = y[mask]
    exog_clean = exog[mask]
    instruments_clean = instruments_df[mask]
    
    if endog is not None:
        endog_clean = endog[mask]
    else:
        endog_clean = None
    
    if len(y_clean) < 20:
        return {
            'error': f"Insufficient observations after cleaning: {len(y_clean)}",
            'outcome': outcome,
            'n_obs': len(y_clean),
        }
    
    # Estimate GMM model
    try:
        if endog_clean is not None and len(endog_clean.columns) > 0:
            model = IVGMM(
                dependent=y_clean,
                exog=exog_clean,
                endog=endog_clean,
                instruments=instruments_clean,
            )
        else:
            # No endogenous variables - use OLS with GMM
            # Combine all regressors
            full_exog = exog_clean.copy()
            model = IVGMM(
                dependent=y_clean,
                exog=full_exog,
                endog=None,
                instruments=instruments_clean,
            )
        
        cov_requested = cov_type
        cov_used = cov_requested
        cov_warning = None
        if cov_requested == 'clustered':
            try:
                clusters = y_clean.index.get_level_values(0)
                results = model.fit(cov_type='clustered', clusters=clusters)
            except Exception:
                cov_used = 'robust'
                cov_warning = "Clustered covariance unavailable for IVGMM; used robust instead."
                results = model.fit(cov_type='robust')
        else:
            results = model.fit(cov_type='robust')
        
    except Exception as e:
        error_msg = str(e)
        # Common error handling
        if 'singular' in error_msg.lower() or 'rank' in error_msg.lower():
            return {
                'error': f"Matrix singularity issue: {error_msg}",
                'outcome': outcome,
                'n_obs': len(y_clean),
                'n_instruments': len(instr_cols_valid),
            }
        return {
            'error': f"GMM estimation failed: {error_msg}",
            'outcome': outcome,
            'n_obs': len(y_clean),
        }
    
    # Extract treatment coefficient
    if treatment_col in results.params.index:
        coef = results.params[treatment_col]
        se = results.std_errors[treatment_col]
        t_stat = results.tstats[treatment_col]
        p_value = results.pvalues[treatment_col]
    else:
        return {
            'error': f"Treatment variable '{treatment_col}' not found in results",
            'outcome': outcome,
            'n_obs': len(y_clean),
        }
    
    # Get residuals for diagnostic tests
    residuals = results.resids
    
    # Arellano-Bond AR tests
    ar1_test = arellano_bond_test(residuals, entity_col, time_col, order=1)
    ar2_test = arellano_bond_test(residuals, entity_col, time_col, order=2)
    
    # Sargan-Hansen test
    n_params = len(results.params)
    sargan_test = sargan_hansen_test(residuals, instruments_clean, n_params)
    
    # Build results dictionary
    n_entities = len(y_clean.index.get_level_values(0).unique())
    instr_entity_ratio = len(instr_cols_valid) / max(n_entities, 1)
    result = {
        'outcome': outcome,
        'treatment': treatment_col,
        'coefficient': float(coef),
        'std_error': float(se),
        't_statistic': float(t_stat),
        'p_value': float(p_value),
        'n_obs': int(len(y_clean)),
        'n_entities': n_entities,
        'n_periods': len(y_clean.index.get_level_values(1).unique()),
        'n_instruments': len(instr_cols_valid),
        'instrument_entity_ratio': float(instr_entity_ratio),
        'instruments_used': instr_cols_valid,
        'endogenous_treatment': endogenous_treatment,
        'cov_type_requested': cov_requested,
        'cov_type_used': cov_used,
        'survivorship_mode': survivorship_mode,
        # Diagnostic tests
        'ar1_statistic': ar1_test.get('statistic', np.nan),
        'ar1_pvalue': ar1_test.get('p_value', np.nan),
        'ar2_statistic': ar2_test.get('statistic', np.nan),
        'ar2_pvalue': ar2_test.get('p_value', np.nan),
        'sargan_statistic': sargan_test.get('statistic', np.nan),
        'sargan_df': sargan_test.get('df', np.nan),
        'sargan_pvalue': sargan_test.get('p_value', np.nan),
        # Inference
        'confidence_interval': (float(coef - 1.96*se), float(coef + 1.96*se)),
        'significant_5pct': abs(t_stat) > 1.96,
        'significant_10pct': abs(t_stat) > 1.645,
    }
    
    # Add lagged dependent variable coefficient if available
    if lagged_dep in results.params.index:
        result['lagged_dep_coefficient'] = float(results.params[lagged_dep])
        result['lagged_dep_pvalue'] = float(results.pvalues[lagged_dep])
    
    if cov_warning is not None:
        result['covariance_warning'] = cov_warning
    if instr_entity_ratio > 1.0:
        result['instrument_warning'] = (
            f"Instrument count ({len(instr_cols_valid)}) exceeds entity count ({n_entities})."
        )
    
    return result


def run_gmm_robustness(
    df: pd.DataFrame,
    outcomes: List[str],
    treatment_col: str = 'green_bond_active',
    entity_col: str = 'ric',
    time_col: str = 'Year',
    control_vars: Optional[List[str]] = None,
    max_lags: int = 2,
    endogenous_treatment: bool = False,
    max_instruments: Optional[int] = 20,
    cov_type: str = 'clustered',
    survivorship_mode: str = 'ignore',
    survivorship_kwargs: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """
    Run System GMM for multiple outcomes and compile results.
    
    Parameters
    ----------
    df : pd.DataFrame
        Panel data.
    outcomes : list
        List of outcome variables to analyze.
    treatment_col : str, optional
        Treatment indicator (default: 'green_bond_active').
    entity_col : str, optional
        Entity identifier (default: 'ric').
    time_col : str, optional
        Time identifier (default: 'Year').
    control_vars : list, optional
        Control variables.
    max_lags : int, optional
        Maximum lags for instruments (default: 2).
    endogenous_treatment : bool, optional
        If True, treat treatment as endogenous (default: False).
    max_instruments : int, optional
        Optional hard cap on instruments retained (default: 20).
    cov_type : str, optional
        Covariance type for inference (default: 'clustered').
    survivorship_mode : str, optional
        Survivorship handling mode ('ignore', 'exclude', 'weight').
    survivorship_kwargs : dict, optional
        Additional arguments for survivorship sample preparation.
        
    Returns
    -------
    pd.DataFrame
        Summary results for all outcomes.
    """
    results = []
    errors = []
    
    for outcome in outcomes:
        result = estimate_system_gmm(
            df=df,
            outcome=outcome,
            treatment_col=treatment_col,
            entity_col=entity_col,
            time_col=time_col,
            control_vars=control_vars,
            max_lags=max_lags,
            endogenous_treatment=endogenous_treatment,
            max_instruments=max_instruments,
            cov_type=cov_type,
            survivorship_mode=survivorship_mode,
            survivorship_kwargs=survivorship_kwargs,
        )
        
        if 'error' not in result:
            results.append(result)
        else:
            errors.append({
                'outcome': outcome,
                'error': result['error']
            })
    
    if errors:
        print(f"\n⚠️  Warning: {len(errors)} GMM model(s) failed:")
        for err in errors[:5]:
            print(f"  - {err['outcome']}: {err['error']}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors")
    
    if results:
        return pd.DataFrame(results)
    else:
        return pd.DataFrame()


__all__ = [
    "select_gmm_instruments",
    "arellano_bond_test",
    "sargan_hansen_test",
    "estimate_system_gmm",
    "run_gmm_robustness",
]
