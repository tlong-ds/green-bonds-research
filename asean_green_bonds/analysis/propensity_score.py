"""
Propensity score matching (PSM) for ASEAN Green Bonds analysis.

Implements matching-based causal inference to create comparable treatment/control groups.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from typing import Tuple, Optional, Dict, List, Any, Union
import warnings
from ..config import (
    PSM_CALIPER,
    PSM_CALIPER_METHOD,
    PSM_QUALITY_CONFIG,
    PSM_FEATURES,
    PSM_RELAXED_CALIPER_FACTOR,
    PSM_RELAXED_CALIPER_MIN,
)

# Suppress only specific expected warnings, not all
warnings.filterwarnings('ignore', category=FutureWarning, module='sklearn')


def estimate_propensity_scores(
    df: pd.DataFrame,
    treatment_col: str = 'green_bond_issue',
    features: Optional[List[str]] = None,
    add_industry_fe: bool = True,
    add_country_fe: bool = True,
    exclude_separation_vars: bool = True,
) -> pd.Series:
    """
    Estimate propensity scores (probability of treatment) via logistic regression.
    
    Parameters
    ----------
    df : pd.DataFrame
        Panel data with treatment and control variables.
    treatment_col : str, optional
        Name of treatment variable (default: 'green_bond_issue').
    features : list, optional
        Features for propensity model. If None, uses enhanced default set.
    add_industry_fe : bool, optional
        Whether to include industry (TRBC sector) fixed effects (default: True).
    add_country_fe : bool, optional
        Whether to include country fixed effects (default: True).
    exclude_separation_vars : bool, optional
        Whether to exclude variables that cause perfect/quasi-separation (default: True).
        
    Returns
    -------
    pd.Series
        Propensity scores [0, 1] indexed same as input.
        
    Notes
    -----
    Uses enhanced logistic regression with theory-driven variables:
    P(treatment=1 | X, Industry, Country) to balance observable characteristics
    between treated and control firms before matching.
    
    Handles perfect separation by excluding problematic variables (has_green_framework)
    and uses regularized logistic regression for stability.
    """
    if features is None:
        # Enhanced default features for propensity score model
        # Theory-driven specification capturing multi-dimensional selection process
        features = list(PSM_FEATURES)
    
    # Check for problematic variables that cause perfect separation
    if exclude_separation_vars:
        # Remove variables known to cause quasi-separation
        separation_vars = ['has_green_framework']  # All treated=1, most control=0
        # Detect additional binary variables with extreme separation ratios (>10:1)
        for feature in list(features):
            if feature not in df.columns:
                continue
            series = df[feature].dropna()
            unique_vals = set(series.unique())
            # Only evaluate binary variables to avoid false positives
            if unique_vals.issubset({0, 1, True, False}):
                treated = df[df[treatment_col] == 1][feature].dropna()
                control = df[df[treatment_col] == 0][feature].dropna()
                treated_rate = treated.mean() if len(treated) > 0 else 0.0
                control_rate = control.mean() if len(control) > 0 else 0.0
                # Avoid division by zero; treat zero as extreme separation
                if treated_rate == 0 or control_rate == 0:
                    separation_vars.append(feature)
                    continue
                ratio = max(treated_rate / control_rate, control_rate / treated_rate)
                if ratio > 10.0:
                    separation_vars.append(feature)
        separation_vars = list(dict.fromkeys(separation_vars))
        available_features = [f for f in features if f in df.columns and f not in separation_vars]
        if len(available_features) < len(features):
            print(f"Excluded {len(features) - len(available_features)} separation variables from propensity model")
        features = available_features
    
    # Prepare feature list for data extraction
    required_cols = [treatment_col] + features
    
    # Add fixed effects variables if requested
    if add_industry_fe and 'trbc_business_sector' in df.columns:
        required_cols.append('trbc_business_sector')
    if add_country_fe and 'country' in df.columns:
        required_cols.append('country')
    
    # Prepare data (keep observations with all required variables)
    df_ps = df[required_cols].dropna()
    
    if len(df_ps) == 0:
        raise ValueError("No observations remain after dropping missing values. Check feature availability.")
    
    # Separate continuous features and categorical fixed effects
    X_continuous = df_ps[features]
    y = df_ps[treatment_col]
    
    # Create dummy variables for fixed effects
    X_dummies = pd.DataFrame(index=df_ps.index)
    
    if add_industry_fe and 'trbc_business_sector' in df_ps.columns:
        industry_dummies = pd.get_dummies(df_ps['trbc_business_sector'], prefix='industry', drop_first=True)
        X_dummies = pd.concat([X_dummies, industry_dummies], axis=1)
    
    if add_country_fe and 'country' in df_ps.columns:
        country_dummies = pd.get_dummies(df_ps['country'], prefix='country', drop_first=True)  
        X_dummies = pd.concat([X_dummies, country_dummies], axis=1)
    
    # Combine continuous features with dummy variables
    X_combined = pd.concat([X_continuous, X_dummies], axis=1)
    
    # Standardize only the continuous features (not dummy variables)
    scaler = StandardScaler()
    X_continuous_scaled = pd.DataFrame(
        scaler.fit_transform(X_continuous), 
        columns=X_continuous.columns, 
        index=X_continuous.index
    )
    
    # Combine scaled continuous and dummy variables
    X_final = pd.concat([X_continuous_scaled, X_dummies], axis=1)
    
    # Fit logistic model with L1 regularization for stability
    model = LogisticRegression(
        penalty='l1',  # L1 regularization helps with separation issues
        C=1.0,         # Regularization strength (lower = more regularization)
        max_iter=2000, # Increased iterations for convergence
        solver='liblinear',  # Required for L1 penalty
        random_state=42
    )
    model.fit(X_final, y)
    
    # Get propensity scores
    ps = model.predict_proba(X_final)[:, 1]
    
    # Return as Series with original index
    result = pd.Series(np.nan, index=df.index)
    result.loc[df_ps.index] = ps
    
    return result


def calculate_optimal_caliper(
    propensity_scores: pd.Series,
    method: str = 'austin',
) -> float:
    """
    Calculate optimal caliper based on propensity score distribution.
    
    Parameters
    ----------
    propensity_scores : pd.Series
        Series of propensity scores.
    method : str
        'austin' - 0.25 * SD(propensity_score) [Austin 2011]
        'logit' - 0.2 * SD(logit(PS)) 
        'rosenbaum' - 0.25 * SD(PS) pooled across groups
    
    Returns
    -------
    float
        Optimal caliper value (minimum 0.01).
        
    Notes
    -----
    Austin (2011) "Optimal caliper widths for propensity-score matching"
    recommends 0.2 * SD(logit(PS)), but 0.25 * SD(PS) is simpler and works well.
    """
    MIN_CALIPER = 0.01
    
    ps = propensity_scores.dropna()
    
    if len(ps) < 2:
        return MIN_CALIPER
    
    # Handle edge case: all same PS values
    if ps.std() == 0 or np.isnan(ps.std()):
        return MIN_CALIPER
    
    if method == 'austin':
        # Austin (2011) simplified: 0.25 * SD(PS)
        caliper = 0.25 * ps.std()
        
    elif method == 'logit':
        # Austin (2011) recommended: 0.2 * SD(logit(PS))
        # Clip to avoid log(0) and log(1)
        ps_clipped = ps.clip(lower=1e-6, upper=1 - 1e-6)
        logit_ps = np.log(ps_clipped / (1 - ps_clipped))
        caliper = 0.2 * logit_ps.std()
        
    elif method == 'rosenbaum':
        # Rosenbaum & Rubin: 0.25 * pooled SD(PS)
        caliper = 0.25 * ps.std()
        
    else:
        raise ValueError(f"Unknown method: {method}. Use 'austin', 'logit', or 'rosenbaum'.")
    
    # Enforce minimum caliper to prevent over-restriction
    return max(caliper, MIN_CALIPER)


def trim_extreme_propensity_scores(
    df: pd.DataFrame,
    ps_col: str = 'propensity_score',
    treatment_col: str = 'green_bond_issue',
    method: str = 'crump',
    alpha: float = 0.1,
) -> pd.DataFrame:
    """
    Trim observations with extreme propensity scores to improve common support.
    
    Parameters
    ----------
    df : pd.DataFrame
        Data with propensity scores.
    ps_col : str
        Propensity score column name (default: 'propensity_score').
    treatment_col : str
        Treatment column name (default: 'green_bond_issue').
    method : str
        'crump' - Crump et al. (2009) optimal trimming rule
        'percentile' - Trim below alpha and above 1-alpha percentiles
    alpha : float
        For 'percentile' method, trim below alpha and above 1-alpha.
        For 'crump', this is the threshold for optimal trimming.
    
    Returns
    -------
    pd.DataFrame
        Trimmed dataset with extreme propensity scores removed.
        
    Notes
    -----
    Crump et al. (2009) "Dealing with limited overlap in estimation of
    average treatment effects" recommends trimming observations where
    PS < alpha or PS > (1 - alpha), with alpha typically ~0.1.
    """
    df = df.copy()
    ps = df[ps_col]
    
    if method == 'crump':
        # Crump et al. (2009): trim where PS < alpha or PS > 1-alpha
        # Default alpha=0.1 gives common support [0.1, 0.9]
        lower_bound = alpha
        upper_bound = 1 - alpha
        
    elif method == 'percentile':
        # Percentile-based trimming
        lower_bound = ps.quantile(alpha)
        upper_bound = ps.quantile(1 - alpha)
        
    else:
        raise ValueError(f"Unknown method: {method}. Use 'crump' or 'percentile'.")
    
    # Apply trimming
    mask = (ps >= lower_bound) & (ps <= upper_bound)
    trimmed_df = df[mask].copy()
    
    return trimmed_df


def check_common_support(
    df: pd.DataFrame,
    ps_col: str = 'propensity_score',
    treatment_col: str = 'green_bond_issue',
    plot: bool = False,
) -> Dict[str, Any]:
    """
    Verify common support assumption (overlap of propensity score distributions).
    
    Parameters
    ----------
    df : pd.DataFrame
        Data with propensity scores.
    ps_col : str, optional
        Propensity score column name (default: 'propensity_score').
    treatment_col : str, optional
        Treatment column name (default: 'green_bond_issue').
    plot : bool, optional
        If True, create visualization (default: False).
        
    Returns
    -------
    dict
        Diagnostic report: min/max PS by group, violations, overlap percentage.
    """
    treated = df[df[treatment_col] == 1][ps_col].dropna()
    control = df[df[treatment_col] == 0][ps_col].dropna()
    
    # Calculate support regions
    treated_min, treated_max = treated.min(), treated.max()
    control_min, control_max = control.min(), control.max()
    
    # Calculate overlap region
    overlap_min = max(treated_min, control_min)
    overlap_max = min(treated_max, control_max)
    has_overlap = overlap_min <= overlap_max
    
    # Count violations (units outside common support)
    if has_overlap:
        treated_in_support = (treated >= overlap_min) & (treated <= overlap_max)
        control_in_support = (control >= overlap_min) & (control <= overlap_max)
    else:
        treated_in_support = pd.Series(False, index=treated.index)
        control_in_support = pd.Series(False, index=control.index)
    
    treated_violations = (~treated_in_support).sum()
    control_violations = (~control_in_support).sum()
    
    # Overlap percentage
    treated_overlap = treated_in_support.mean() * 100 if len(treated) > 0 else 0
    control_overlap = control_in_support.mean() * 100 if len(control) > 0 else 0
    
    report = {
        'treated_mean_ps': treated.mean(),
        'treated_sd_ps': treated.std(),
        'control_mean_ps': control.mean(),
        'control_sd_ps': control.std(),
        'overlap_region': (overlap_min, overlap_max),
        'has_overlap': has_overlap,
        'treated_violations': treated_violations,
        'control_violations': control_violations,
        'treated_overlap_pct': treated_overlap,
        'control_overlap_pct': control_overlap,
        'total_observations': len(df),
        'treated_count': len(treated),
        'control_count': len(control),
    }
    
    return report


def nearest_neighbor_matching(
    df: pd.DataFrame,
    ps_col: str = 'propensity_score',
    treatment_col: str = 'green_bond_issue',
    caliper: Union[float, str] = 0.1,
    caliper_method: str = 'austin',
    ratio: int = 1,
    replacement: bool = True,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Perform 1-to-k nearest neighbor matching with caliper.
    
    Parameters
    ----------
    df : pd.DataFrame
        Data with propensity scores.
    ps_col : str, optional
        Propensity score column name (default: 'propensity_score').
    treatment_col : str, optional
        Treatment column name (default: 'green_bond_issue').
    caliper : float or 'auto', optional
        Maximum PS distance for match (default: 0.1).
        If 'auto', uses calculate_optimal_caliper() with 'austin' method.
        If float, uses fixed caliper value.
    caliper_method : str, optional
        Method used when caliper='auto' (default: 'austin').
    ratio : int, optional
        Number of controls per treated unit (default: 1).
    replacement : bool, optional
        If True, allow reuse of control units (default: False).
        
    Returns
    -------
    tuple
        (matched_data: pd.DataFrame, matching_stats: dict)
    """
    df = df.copy()
    df['_matched'] = False
    df['_match_id'] = None
    
    treated_idx = df[df[treatment_col] == 1].index
    control_idx = df[df[treatment_col] == 0].index
    
    treated_ps = df.loc[treated_idx, ps_col]
    control_ps = df.loc[control_idx, ps_col]
    
    # Handle 'auto' caliper
    if caliper == 'auto':
        all_ps = df[ps_col].dropna()
        caliper = calculate_optimal_caliper(all_ps, method=caliper_method)
    else:
        caliper = float(caliper)
    
    matched_rows = []
    unmatched_treated = 0
    matches_made = 0
    
    for t_idx, t_ps in treated_ps.items():
        # Calculate distances
        distances = np.abs(control_ps - t_ps)
        
        # Apply caliper
        valid_matches = distances[distances <= caliper].sort_values()
        
        if len(valid_matches) == 0:
            unmatched_treated += 1
            continue
        
        # Select top k matches
        selected_idx = valid_matches.index[:ratio]
        
        if not replacement:
            # Remove already matched units
            control_ps = control_ps.drop(selected_idx, errors='ignore')
        
        for m_idx in selected_idx:
            matched_rows.append(t_idx)
            matched_rows.append(m_idx)
            matches_made += 1
    
    # Create matched dataset
    matched_df = df.loc[df.index.isin(matched_rows)].copy()
    
    stats = {
        'treated_units': len(treated_idx),
        'control_units': len(control_idx),
        'matched_treated': len(treated_idx) - unmatched_treated,
        'unmatched_treated': unmatched_treated,
        'matched_controls': len(matched_df[matched_df[treatment_col] == 0]),
        'caliper': caliper,
        'ratio': ratio,
        'total_matched_obs': len(matched_df),
    }
    
    return matched_df, stats


def assess_balance(
    df: pd.DataFrame,
    features: List[str],
    treatment_col: str = 'green_bond_issue',
    standardized: bool = True,
) -> pd.DataFrame:
    """
    Assess covariate balance after matching.
    
    Parameters
    ----------
    df : pd.DataFrame
        Matched data.
    features : list
        Covariates to check for balance.
    treatment_col : str, optional
        Treatment column name (default: 'green_bond_issue').
    standardized : bool, optional
        If True, report standardized differences (default: True).
        
    Returns
    -------
    pd.DataFrame
        Balance report: mean difference, std diff, p-value for each feature.
    """
    balance_data = []
    
    for feature in features:
        if feature not in df.columns:
            continue
        
        treated = df[df[treatment_col] == 1][feature].dropna()
        control = df[df[treatment_col] == 0][feature].dropna()
        
        if len(treated) == 0 or len(control) == 0:
            continue
        
        # Calculate statistics
        mean_diff = treated.mean() - control.mean()
        
        if standardized:
            # Standardized difference (Cohen's d)
            pooled_sd = np.sqrt(
                ((len(treated)-1)*treated.std()**2 + (len(control)-1)*control.std()**2) /
                (len(treated) + len(control) - 2)
            )
            std_diff = mean_diff / pooled_sd if pooled_sd > 0 else 0
        else:
            std_diff = mean_diff
        
        # T-test
        from scipy import stats as sp_stats
        if len(treated) > 1 and len(control) > 1:
            t_stat, p_value = sp_stats.ttest_ind(treated, control)
        else:
            t_stat, p_value = np.nan, np.nan
        
        balance_data.append({
            'Feature': feature,
            'Treated_Mean': treated.mean(),
            'Control_Mean': control.mean(),
            'Mean_Difference': mean_diff,
            'Std_Difference': std_diff,
            'T_Statistic': t_stat,
            'P_Value': p_value,
            'Balanced': abs(std_diff) < 0.1 if standardized else abs(mean_diff) < mean_diff.std()*0.2,
        })
    
    return pd.DataFrame(balance_data)


def estimate_entropy_weights(
    df: pd.DataFrame,
    treatment_col: str = 'green_bond_issue',
    features: Optional[List[str]] = None,
    moments: int = 1,
) -> pd.Series:
    """
    Estimate entropy balancing weights (Hainmueller 2012).
    
    Finds weights for control units such that their covariate moments 
    match those of the treatment group, while staying as close as 
    possible to uniform weights (base weights).
    
    Parameters
    ----------
    df : pd.DataFrame
        Data with treatment and covariates.
    treatment_col : str
        Treatment indicator.
    features : list
        Covariates to balance.
    moments : int
        Number of moments to balance (1=mean, 2=variance).
        
    Returns
    -------
    pd.Series
        Weights indexed same as input. Treated units get weight 1.0.
    """
    from scipy.optimize import minimize
    
    if features is None:
        features = [
            'L1_Firm_Size', 'L1_Leverage', 'L1_Asset_Turnover',
            'L1_Capital_Intensity', 'L1_Cash_Ratio'
        ]
        
    df_eb = df[[treatment_col] + features].dropna()
    X = df_eb[features].values
    y = df_eb[treatment_col].values
    
    X_treat = X[y == 1]
    X_control = X[y == 0]
    
    if len(X_treat) == 0 or len(X_control) == 0:
        return pd.Series(1.0, index=df.index)
        
    # Target moments (means of treatment group)
    targets = np.mean(X_treat, axis=0)
    
    # Initial Lagrange multipliers
    params = np.zeros(len(features))
    
    # Loss function for entropy balancing (Lagrangian)
    def loss(params):
        # Weight for each control unit: w_i = exp(X_i * params)
        weights = np.exp(np.dot(X_control, params))
        # Moment conditions: sum(w_i * X_ij) = target_j * sum(w_i)
        # We want to minimize the log partition function
        return np.log(np.sum(weights)) - np.dot(targets, params)
        
    # Optimize
    res = minimize(loss, params, method='L-BFGS-B')
    
    if not res.success:
        warnings.warn(f"Entropy balancing optimization failed: {res.message}")
        return pd.Series(1.0, index=df.index)
        
    # Calculate final weights for controls
    control_weights = np.exp(np.dot(X_control, res.x))
    # Normalize so they sum to number of control units (or 1, but we'll use n_control)
    control_weights = control_weights * (len(X_control) / np.sum(control_weights))
    
    weights = pd.Series(1.0, index=df.index)
    weights.loc[df_eb[y == 0].index] = control_weights
    
    return weights


def create_matched_dataset(
    df: pd.DataFrame,
    treatment_col: str = 'green_bond_issue',
    ps_col: str = 'propensity_score',
    caliper: Optional[Union[float, str]] = None,
    ratio: int = 4,
    replacement: Optional[bool] = None,
    check_support: bool = True,
    trim_to_common_support: Optional[bool] = None,
    trimming_method: Optional[str] = None,
    trimming_alpha: Optional[float] = None,
    enforce_quality: Optional[bool] = None,
    min_matched_treated_ratio: Optional[float] = None,
    max_abs_std_diff: Optional[float] = None,
    balance_features: Optional[List[str]] = None,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Create propensity-score matched dataset for DiD analysis.
    
    Parameters
    ----------
    df : pd.DataFrame
        Full panel data.
    treatment_col : str, optional
        Treatment column name (default: 'green_bond_issue').
    ps_col : str, optional
        Propensity score column name (default: 'propensity_score').
    caliper : float or 'auto', optional
        Maximum PS distance. If None, resolves from config policy.
    ratio : int, optional
        Controls per treated unit (default: 4).
    replacement : bool, optional
        If True, allow reuse of control units (default: True).
    check_support : bool, optional
        If True, verify common support first (default: True).
    trim_to_common_support : bool, optional
        If True, trim extreme propensity scores before matching using
        trim_extreme_propensity_scores. If None, uses config default.
    trimming_method : str, optional
        Trimming method, one of {'crump', 'percentile'}. If None, uses config.
    trimming_alpha : float, optional
        Trimming threshold alpha passed to trim_extreme_propensity_scores
        (if None, uses config).
        
    Returns
    -------
    tuple
        (matched_dataset: pd.DataFrame, diagnostic_report: dict)
    """
    df = df.copy()

    if caliper == 'auto':
        caliper_value: Union[float, str] = 'auto'
        caliper_method = PSM_CALIPER_METHOD
    elif caliper is None:
        if PSM_CALIPER_METHOD == 'fixed':
            caliper_value = float(PSM_CALIPER)
            caliper_method = 'fixed'
        else:
            caliper_value = 'auto'
            caliper_method = PSM_CALIPER_METHOD
    else:
        caliper_value = float(caliper)
        caliper_method = 'fixed'

    if trim_to_common_support is None:
        trim_to_common_support = bool(PSM_QUALITY_CONFIG.get('trim_to_common_support', False))
    if trimming_method is None:
        trimming_method = str(PSM_QUALITY_CONFIG.get('trimming_method', 'crump'))
    if trimming_alpha is None:
        trimming_alpha = float(PSM_QUALITY_CONFIG.get('trimming_alpha', 0.1))
    if enforce_quality is None:
        enforce_quality = bool(PSM_QUALITY_CONFIG.get('enforce_quality', False))
    if min_matched_treated_ratio is None:
        min_matched_treated_ratio = float(PSM_QUALITY_CONFIG.get('min_matched_treated_ratio', 0.7))
    if max_abs_std_diff is None:
        max_abs_std_diff = float(PSM_QUALITY_CONFIG.get('max_abs_std_diff', 0.1))
    if replacement is None:
        replacement = True
    
    # Create year-level treatment indicator
    df['ever_treated'] = df.groupby('org_permid')[treatment_col].transform('max')
    treatment_years = (
        df[df[treatment_col] == 1]
        .groupby('org_permid')['Year']
        .min()
    )
    df['treatment_year'] = df['org_permid'].map(treatment_years)
    
    diagnostics = {}
    
    # Check common support
    if check_support:
        diagnostics['common_support'] = check_common_support(
            df, ps_col=ps_col, treatment_col=treatment_col
        )
    
    if trim_to_common_support:
        before_trim_n = len(df)
        trimmed_df = trim_extreme_propensity_scores(
            df,
            ps_col=ps_col,
            treatment_col=treatment_col,
            method=trimming_method,
            alpha=trimming_alpha,
        )
        # Guard against pathological trimming that removes all treated or controls.
        treated_after = int((trimmed_df[treatment_col] == 1).sum()) if treatment_col in trimmed_df.columns else 0
        control_after = int((trimmed_df[treatment_col] == 0).sum()) if treatment_col in trimmed_df.columns else 0
        trim_applied = treated_after > 0 and control_after > 0 and len(trimmed_df) > 0
        if trim_applied:
            df = trimmed_df
        diagnostics['trimming'] = {
            'enabled': True,
            'method': trimming_method,
            'alpha': trimming_alpha,
            'n_before': before_trim_n,
            'n_after': len(trimmed_df) if trim_applied else before_trim_n,
            'n_dropped': before_trim_n - (len(trimmed_df) if trim_applied else before_trim_n),
            'applied': trim_applied,
            'skipped_reason': None if trim_applied else 'trim_removed_treated_or_control_group',
        }
    else:
        diagnostics['trimming'] = {'enabled': False, 'applied': False}
    
    # Resolve relaxed caliper policy for sparse treatment settings
    if caliper_value == 'auto' and caliper_method in {'austin', 'logit', 'rosenbaum'}:
        all_ps = df[ps_col].dropna()
        base_caliper = calculate_optimal_caliper(all_ps, method=caliper_method)
        relaxed_caliper = max(base_caliper * PSM_RELAXED_CALIPER_FACTOR, PSM_RELAXED_CALIPER_MIN)
        caliper_value = float(relaxed_caliper)
        caliper_method = f"relaxed_{caliper_method}"

    # Perform matching
    matched_df, match_stats = nearest_neighbor_matching(
        df, ps_col=ps_col, treatment_col=treatment_col,
        caliper=caliper_value, caliper_method=caliper_method, ratio=ratio,
        replacement=replacement
    )
    
    diagnostics['matching_stats'] = match_stats
    diagnostics['caliper_policy'] = {
        'requested_caliper': caliper,
        'resolved_method': caliper_method,
        'resolved_caliper': float(match_stats.get('caliper', np.nan)),
        'relax_factor': PSM_RELAXED_CALIPER_FACTOR,
        'relax_min': PSM_RELAXED_CALIPER_MIN,
    }

    features_for_balance = balance_features or [c for c in PSM_FEATURES if c in matched_df.columns]
    balance_df = assess_balance(matched_df, features_for_balance, treatment_col=treatment_col)
    if not balance_df.empty and 'Std_Difference' in balance_df.columns:
        max_smd = float(balance_df['Std_Difference'].abs().max())
        pct_balanced = float(balance_df['Balanced'].mean()) if 'Balanced' in balance_df.columns else np.nan
    else:
        max_smd = np.nan
        pct_balanced = np.nan

    treated_units = float(match_stats.get('treated_units', 0) or 0)
    matched_treated = float(match_stats.get('matched_treated', 0) or 0)
    matched_ratio = (matched_treated / treated_units) if treated_units > 0 else 0.0
    quality_report = {
        'enforce_quality': enforce_quality,
        'min_matched_treated_ratio': min_matched_treated_ratio,
        'max_abs_std_diff_threshold': max_abs_std_diff,
        'matched_treated_ratio': matched_ratio,
        'max_abs_std_diff_observed': max_smd,
        'balanced_feature_share': pct_balanced,
    }
    diagnostics['balance_summary'] = quality_report

    quality_failures = []
    if matched_ratio < min_matched_treated_ratio:
        quality_failures.append(
            f"Matched treated ratio {matched_ratio:.3f} below threshold {min_matched_treated_ratio:.3f}"
        )
    if not np.isnan(max_smd) and max_smd > max_abs_std_diff:
        quality_failures.append(
            f"Max absolute standardized difference {max_smd:.3f} above threshold {max_abs_std_diff:.3f}"
        )
    diagnostics['quality_failures'] = quality_failures
    if quality_failures:
        diagnostics['quality_warning'] = " | ".join(quality_failures)
        if enforce_quality:
            raise ValueError(diagnostics['quality_warning'])
    
    return matched_df, diagnostics
