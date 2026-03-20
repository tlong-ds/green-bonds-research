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

# Suppress only specific expected warnings, not all
warnings.filterwarnings('ignore', category=FutureWarning, module='sklearn')


def estimate_propensity_scores(
    df: pd.DataFrame,
    treatment_col: str = 'green_bond_issue',
    features: Optional[List[str]] = None,
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
        Features for propensity model. If None, auto-selects.
        
    Returns
    -------
    pd.Series
        Propensity scores [0, 1] indexed same as input.
        
    Notes
    -----
    Uses logistic regression: P(treatment=1 | X) to balance observable characteristics
    between treated and control firms before matching.
    """
    if features is None:
        # Default features for propensity score model
        features = [
            'L1_Firm_Size', 'L1_Leverage', 'L1_Asset_Turnover',
            'L1_Capital_Intensity', 'L1_Cash_Ratio'
        ]
    
    # Prepare data
    df_ps = df[[treatment_col] + features].dropna()
    X = df_ps[features]
    y = df_ps[treatment_col]
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Fit logistic model
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_scaled, y)
    
    # Get propensity scores
    ps = model.predict_proba(X_scaled)[:, 1]
    
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
    ratio: int = 1,
    replacement: bool = False,
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
        caliper = calculate_optimal_caliper(all_ps, method='austin')
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


def create_matched_dataset(
    df: pd.DataFrame,
    treatment_col: str = 'green_bond_issue',
    ps_col: str = 'propensity_score',
    caliper: float = 0.1,
    ratio: int = 4,
    check_support: bool = True,
    trim_to_common_support: bool = False,
    trimming_method: str = 'crump',
    trimming_alpha: float = 0.1,
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
    caliper : float, optional
        Maximum PS distance (default: 0.1).
    ratio : int, optional
        Controls per treated unit (default: 4).
    check_support : bool, optional
        If True, verify common support first (default: True).
    trim_to_common_support : bool, optional
        If True, trim extreme propensity scores before matching using
        trim_extreme_propensity_scores (default: False).
    trimming_method : str, optional
        Trimming method, one of {'crump', 'percentile'} (default: 'crump').
    trimming_alpha : float, optional
        Trimming threshold alpha passed to trim_extreme_propensity_scores
        (default: 0.1).
        
    Returns
    -------
    tuple
        (matched_dataset: pd.DataFrame, diagnostic_report: dict)
    """
    df = df.copy()
    
    # Create year-level treatment indicator
    df['ever_treated'] = df.groupby('ric')[treatment_col].transform('max')
    treatment_years = (
        df[df[treatment_col] == 1]
        .groupby('ric')['Year']
        .min()
    )
    df['treatment_year'] = df['ric'].map(treatment_years)
    
    diagnostics = {}
    
    # Check common support
    if check_support:
        diagnostics['common_support'] = check_common_support(
            df, ps_col=ps_col, treatment_col=treatment_col
        )
    
    if trim_to_common_support:
        before_trim_n = len(df)
        df = trim_extreme_propensity_scores(
            df,
            ps_col=ps_col,
            treatment_col=treatment_col,
            method=trimming_method,
            alpha=trimming_alpha,
        )
        diagnostics['trimming'] = {
            'enabled': True,
            'method': trimming_method,
            'alpha': trimming_alpha,
            'n_before': before_trim_n,
            'n_after': len(df),
            'n_dropped': before_trim_n - len(df),
        }
    else:
        diagnostics['trimming'] = {'enabled': False}
    
    # Perform matching
    matched_df, match_stats = nearest_neighbor_matching(
        df, ps_col=ps_col, treatment_col=treatment_col,
        caliper=caliper, ratio=ratio
    )
    
    diagnostics['matching_stats'] = match_stats
    
    return matched_df, diagnostics
