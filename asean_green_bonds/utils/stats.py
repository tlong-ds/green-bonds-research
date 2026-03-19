"""
Statistical utility functions for ASEAN Green Bonds research.

Helper functions for statistical analysis and hypothesis testing.
"""

import pandas as pd
import numpy as np
from scipy import stats as sp_stats
from typing import Tuple, Optional, Dict, List, Any
import warnings

# Suppress only specific expected warnings
warnings.filterwarnings('ignore', category=FutureWarning)


def calculate_effect_size(
    group1: pd.Series,
    group2: pd.Series,
    method: str = 'cohens_d',
) -> float:
    """
    Calculate effect size between two groups.
    
    Parameters
    ----------
    group1 : pd.Series
        First group values.
    group2 : pd.Series
        Second group values.
    method : str, optional
        Effect size measure: 'cohens_d' (default), 'hedges_g', 'correlation'
        
    Returns
    -------
    float
        Effect size measure.
    """
    group1_clean = group1.dropna()
    group2_clean = group2.dropna()
    
    if len(group1_clean) < 2 or len(group2_clean) < 2:
        return np.nan
    
    mean1, mean2 = group1_clean.mean(), group2_clean.mean()
    sd1, sd2 = group1_clean.std(), group2_clean.std()
    n1, n2 = len(group1_clean), len(group2_clean)
    
    if method == 'cohens_d':
        # Cohen's d (biased)
        pooled_sd = np.sqrt(((n1-1)*sd1**2 + (n2-1)*sd2**2) / (n1 + n2 - 2))
        return (mean1 - mean2) / pooled_sd if pooled_sd > 0 else 0
    
    elif method == 'hedges_g':
        # Hedges' g (unbiased)
        pooled_sd = np.sqrt(((n1-1)*sd1**2 + (n2-1)*sd2**2) / (n1 + n2 - 2))
        correction = 1 - (3 / (4*(n1 + n2 - 2) - 1))
        return ((mean1 - mean2) / pooled_sd * correction) if pooled_sd > 0 else 0
    
    elif method == 'correlation':
        # Correlation coefficient
        combined = pd.concat([group1_clean, group2_clean])
        group_indicator = pd.Series([0]*len(group1_clean) + [1]*len(group2_clean))
        return combined.corr(group_indicator)
    
    else:
        raise ValueError(f"Unknown method: {method}")


def calculate_confidence_interval(
    data: pd.Series,
    confidence: float = 0.95,
    method: str = 't',
) -> Tuple[float, float]:
    """
    Calculate confidence interval for mean.
    
    Parameters
    ----------
    data : pd.Series
        Data values.
    confidence : float, optional
        Confidence level (default: 0.95).
    method : str, optional
        Method: 't' (default) or 'z'
        
    Returns
    -------
    tuple
        (lower_bound, upper_bound)
    """
    data_clean = data.dropna()
    n = len(data_clean)
    
    if n < 2:
        return (np.nan, np.nan)
    
    mean = data_clean.mean()
    se = data_clean.sem()
    
    if method == 't':
        alpha = 1 - confidence
        t_crit = sp_stats.t.ppf(1 - alpha/2, n - 1)
        margin = t_crit * se
    else:  # z
        z_crit = sp_stats.norm.ppf(1 - (1-confidence)/2)
        margin = z_crit * se
    
    return (mean - margin, mean + margin)


def proportion_test(
    count1: int,
    n1: int,
    count2: int,
    n2: int,
    alternative: str = 'two-sided',
) -> Dict[str, float]:
    """
    Two-sample proportion test (z-test).
    
    Parameters
    ----------
    count1 : int
        Number of successes in group 1.
    n1 : int
        Sample size of group 1.
    count2 : int
        Number of successes in group 2.
    n2 : int
        Sample size of group 2.
    alternative : str, optional
        Hypothesis: 'two-sided' (default), 'greater', 'less'
        
    Returns
    -------
    dict
        Test results: statistic, p_value, effect_size
    """
    p1 = count1 / n1 if n1 > 0 else 0
    p2 = count2 / n2 if n2 > 0 else 0
    
    # Pooled proportion
    p_pooled = (count1 + count2) / (n1 + n2)
    
    # Standard error
    se = np.sqrt(p_pooled * (1 - p_pooled) * (1/n1 + 1/n2))
    
    # Test statistic
    z_stat = (p1 - p2) / se if se > 0 else 0
    
    # P-value
    if alternative == 'two-sided':
        p_value = 2 * (1 - sp_stats.norm.cdf(abs(z_stat)))
    elif alternative == 'greater':
        p_value = 1 - sp_stats.norm.cdf(z_stat)
    else:  # 'less'
        p_value = sp_stats.norm.cdf(z_stat)
    
    # Effect size (difference in proportions)
    effect_size = p1 - p2
    
    return {
        'z_statistic': z_stat,
        'p_value': p_value,
        'proportion_1': p1,
        'proportion_2': p2,
        'difference': effect_size,
    }


def multiple_comparisons_correction(
    p_values: pd.Series,
    method: str = 'bonferroni',
) -> pd.Series:
    """
    Correct p-values for multiple comparisons.
    
    Parameters
    ----------
    p_values : pd.Series
        Original p-values.
    method : str, optional
        Correction method: 'bonferroni', 'holm', 'benjamini_hochberg'
        (default: 'bonferroni')
        
    Returns
    -------
    pd.Series
        Corrected p-values.
    """
    from statsmodels.stats.multitest import multipletests
    
    # Remove NaN
    valid_mask = p_values.notna()
    p_valid = p_values[valid_mask]
    
    # Apply correction
    reject, corrected, _, _ = multipletests(p_valid, method=method)
    
    # Reconstruct full series
    result = pd.Series(np.nan, index=p_values.index)
    result[valid_mask] = corrected
    
    return result


def calculate_variance_inflation_factors(
    X: pd.DataFrame,
    columns: Optional[List[str]] = None,
) -> Dict[str, float]:
    """
    Calculate VIF for all numeric columns.
    
    Parameters
    ----------
    X : pd.DataFrame
        Feature matrix.
    columns : list, optional
        Specific columns to check. If None, uses all numeric.
        
    Returns
    -------
    dict
        VIF values by column.
    """
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    
    if columns is None:
        columns = X.select_dtypes(include=[np.number]).columns
    
    vif_dict = {}
    X_clean = X[columns].dropna()
    
    for i, col in enumerate(X_clean.columns):
        vif = variance_inflation_factor(X_clean.values, i)
        vif_dict[col] = vif
    
    return vif_dict


def calculate_icc(
    data: pd.DataFrame,
    entity_col: str,
    outcome_col: str,
    icc_type: str = '1,k',
) -> float:
    """
    Calculate Intra-Class Correlation (ICC) for clustered data.
    
    Used to assess within-cluster similarity and compute Moulton factors.
    
    Parameters
    ----------
    data : pd.DataFrame
        Panel data with entity and outcome.
    entity_col : str
        Entity/cluster identifier.
    outcome_col : str
        Outcome variable.
    icc_type : str, optional
        ICC type: '1,1', '1,k', '2,1', '2,k' (default: '1,k')
        
    Returns
    -------
    float
        ICC value [0, 1].
    """
    grouped = data.groupby(entity_col)[outcome_col].apply(list)
    
    # Remove empty groups
    grouped = grouped[grouped.apply(len) > 0]
    
    # Calculate between and within variance
    grand_mean = data[outcome_col].mean()
    
    between_var = sum(
        len(group) * (np.mean(group) - grand_mean)**2
        for group in grouped
    ) / (len(grouped) - 1) if len(grouped) > 1 else 0
    
    within_var = sum(
        sum((x - np.mean(group))**2 for x in group)
        for group in grouped
    ) / (len(data) - len(grouped)) if len(data) > len(grouped) else 0
    
    # ICC formula
    if '1,' in icc_type:
        k = grouped.apply(len).mean()
        icc = (between_var - within_var) / (between_var + (k - 1) * within_var + 1e-10)
    else:
        icc = (between_var - within_var) / (between_var + within_var + 1e-10)
    
    return np.clip(icc, 0, 1)


def create_summary_statistics(
    data: pd.DataFrame,
    variables: Optional[List[str]] = None,
    by: Optional[str] = None,
) -> pd.DataFrame:
    """
    Create summary statistics table for variables.
    
    Parameters
    ----------
    data : pd.DataFrame
        Input data.
    variables : list, optional
        Variables to summarize. If None, uses all numeric.
    by : str, optional
        Group by variable for stratified summaries.
        
    Returns
    -------
    pd.DataFrame
        Summary statistics: n, mean, sd, min, max.
    """
    if variables is None:
        variables = data.select_dtypes(include=[np.number]).columns.tolist()
    
    if by is None:
        # Overall summary
        summary_data = []
        for var in variables:
            if var not in data.columns:
                continue
            
            col = data[var].dropna()
            summary_data.append({
                'Variable': var,
                'N': len(col),
                'Mean': col.mean(),
                'Std_Dev': col.std(),
                'Min': col.min(),
                'Median': col.median(),
                'Max': col.max(),
                'Pct_Missing': (data[var].isna().sum() / len(data) * 100),
            })
    else:
        # Stratified summary
        summary_data = []
        groups = data[by].unique()
        
        for var in variables:
            if var not in data.columns:
                continue
            
            for group in groups:
                col = data[data[by] == group][var].dropna()
                summary_data.append({
                    by: group,
                    'Variable': var,
                    'N': len(col),
                    'Mean': col.mean(),
                    'Std_Dev': col.std(),
                    'Min': col.min(),
                    'Max': col.max(),
                })
    
    return pd.DataFrame(summary_data)
