"""
Propensity score matching (PSM) for ASEAN Green Bonds analysis.

Implements matching-based causal inference to create comparable treatment/control groups.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from typing import Tuple, Optional, Dict, List
import warnings

warnings.filterwarnings('ignore')


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


def check_common_support(
    df: pd.DataFrame,
    ps_col: str = 'propensity_score',
    treatment_col: str = 'green_bond_issue',
    plot: bool = False,
) -> Dict[str, any]:
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
    
    # Count violations (units outside common support)
    treated_violations = (treated < overlap_min).sum() + (treated > overlap_max).sum()
    control_violations = (control < overlap_min).sum() + (control > overlap_max).sum()
    
    # Overlap percentage
    treated_overlap = (treated_violations == 0).sum() / len(treated) * 100 if len(treated) > 0 else 0
    control_overlap = (control_violations == 0).sum() / len(control) * 100 if len(control) > 0 else 0
    
    report = {
        'treated_mean_ps': treated.mean(),
        'treated_sd_ps': treated.std(),
        'control_mean_ps': control.mean(),
        'control_sd_ps': control.std(),
        'overlap_region': (overlap_min, overlap_max),
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
    caliper: float = 0.1,
    ratio: int = 1,
    replacement: bool = False,
) -> Tuple[pd.DataFrame, Dict[str, any]]:
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
    caliper : float, optional
        Maximum PS distance for match (default: 0.1).
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
) -> Tuple[pd.DataFrame, Dict[str, any]]:
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
        
    Returns
    -------
    tuple
        (matched_dataset: pd.DataFrame, diagnostic_report: dict)
    """
    df = df.copy()
    
    # Create year-level treatment indicator
    df['ever_treated'] = df.groupby('ric')[treatment_col].transform('max')
    df['treatment_year'] = df.groupby('ric')[df[treatment_col] == 1].transform(
        lambda x: x.index[0] if len(x) > 0 else None
    )
    
    diagnostics = {}
    
    # Check common support
    if check_support:
        diagnostics['common_support'] = check_common_support(
            df, ps_col=ps_col, treatment_col=treatment_col
        )
    
    # Perform matching
    matched_df, match_stats = nearest_neighbor_matching(
        df, ps_col=ps_col, treatment_col=treatment_col,
        caliper=caliper, ratio=ratio
    )
    
    diagnostics['matching_stats'] = match_stats
    
    return matched_df, diagnostics
