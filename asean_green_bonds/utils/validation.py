"""
Data validation utilities for ASEAN Green Bonds research.

Functions for checking data quality and assumption violations.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional, List, Dict
import warnings

warnings.filterwarnings('ignore')


def validate_panel_structure(
    df: pd.DataFrame,
    entity_col: str = 'ric',
    time_col: str = 'Year',
) -> Dict[str, any]:
    """
    Validate panel data structure and report irregularities.
    
    Parameters
    ----------
    df : pd.DataFrame
        Panel data.
    entity_col : str, optional
        Entity identifier (default: 'ric').
    time_col : str, optional
        Time identifier (default: 'Year').
        
    Returns
    -------
    dict
        Validation report.
    """
    report = {
        'n_entities': df[entity_col].nunique(),
        'n_periods': df[time_col].nunique(),
        'n_observations': len(df),
        'expected_obs_balanced': df[entity_col].nunique() * df[time_col].nunique(),
        'is_balanced': len(df) == df[entity_col].nunique() * df[time_col].nunique(),
        'observations_per_entity': df.groupby(entity_col).size().describe().to_dict(),
        'observations_per_period': df.groupby(time_col).size().describe().to_dict(),
        'duplicates': len(df) - len(df.drop_duplicates(subset=[entity_col, time_col])),
        'missing_combinations': df[entity_col].nunique() * df[time_col].nunique() - len(df),
    }
    
    return report


def check_missing_data(
    df: pd.DataFrame,
    threshold: float = 0.5,
) -> Dict[str, any]:
    """
    Check for missing data patterns.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input data.
    threshold : float, optional
        Threshold for flagging columns as problematic (default: 0.5).
        
    Returns
    -------
    dict
        Missing data report.
    """
    missing_pct = df.isnull().sum() / len(df) * 100
    
    report = {
        'total_missing_cells': df.isnull().sum().sum(),
        'total_cells': df.shape[0] * df.shape[1],
        'total_missing_pct': (df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100),
        'columns_above_threshold': missing_pct[missing_pct > threshold*100].to_dict(),
        'columns_with_missing': missing_pct[missing_pct > 0].to_dict(),
    }
    
    return report


def detect_outliers(
    df: pd.DataFrame,
    method: str = 'iqr',
    threshold: float = 3.0,
) -> Dict[str, List]:
    """
    Detect outliers in numeric columns.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input data.
    method : str, optional
        Detection method: 'iqr' (default) or 'zscore'
    threshold : float, optional
        IQR multiplier (method='iqr') or Z-score threshold (default: 3.0).
        
    Returns
    -------
    dict
        Outlier indices by column.
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    outliers = {}
    
    for col in numeric_cols:
        col_data = df[col].dropna()
        
        if method == 'iqr':
            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            
            outlier_mask = (col_data < lower_bound) | (col_data > upper_bound)
        
        else:  # zscore
            z_scores = np.abs((col_data - col_data.mean()) / col_data.std())
            outlier_mask = z_scores > threshold
        
        if outlier_mask.any():
            outliers[col] = col_data[outlier_mask].index.tolist()
    
    return outliers


def validate_treatment_variation(
    df: pd.DataFrame,
    treatment_col: str = 'green_bond_issue',
    entity_col: str = 'ric',
    time_col: str = 'Year',
) -> Dict[str, any]:
    """
    Validate treatment variation for DiD identification.
    
    Parameters
    ----------
    df : pd.DataFrame
        Panel data with treatment indicator.
    treatment_col : str, optional
        Treatment column (default: 'green_bond_issue').
    entity_col : str, optional
        Entity identifier (default: 'ric').
    time_col : str, optional
        Time identifier (default: 'Year').
        
    Returns
    -------
    dict
        Treatment variation report.
    """
    # Treatment status by entity and time
    treated_entities = df[df[treatment_col] == 1][entity_col].nunique()
    control_entities = df[df[treatment_col] == 0][entity_col].nunique()
    
    # Timing variation
    treatment_timing = df[df[treatment_col] == 1].groupby(entity_col)[time_col].min()
    
    report = {
        'total_entities': df[entity_col].nunique(),
        'treated_entities': treated_entities,
        'control_entities': control_entities,
        'treatment_obs': (df[treatment_col] == 1).sum(),
        'control_obs': (df[treatment_col] == 0).sum(),
        'treatment_pct': (df[treatment_col] == 1).sum() / len(df) * 100,
        'ever_treated': (df.groupby(entity_col)[treatment_col].max() == 1).sum(),
        'never_treated': (df.groupby(entity_col)[treatment_col].max() == 0).sum(),
        'timing_range': (treatment_timing.max() - treatment_timing.min()),
        'timing_variation': treatment_timing.std(),
    }
    
    return report


def check_parallel_trends_assumption(
    df: pd.DataFrame,
    outcome: str,
    treatment_col: str = 'green_bond_active',
    entity_col: str = 'ric',
    time_col: str = 'Year',
    pre_treatment_periods: int = 3,
) -> Dict[str, any]:
    """
    Preliminary check of parallel trends assumption.
    
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
    pre_treatment_periods : int, optional
        Number of pre-treatment periods to check (default: 3).
        
    Returns
    -------
    dict
        Parallel trends diagnostic.
    """
    # Get treatment timing
    treatment_timing = df[df[treatment_col] == 1].groupby(entity_col)[time_col].min()
    
    # Compare pre-treatment trends
    pre_trend_groups = []
    
    for entity in df[entity_col].unique():
        entity_data = df[df[entity_col] == entity].sort_values(time_col)
        
        if entity in treatment_timing.index:
            treatment_year = treatment_timing[entity]
            pre_data = entity_data[entity_data[time_col] < treatment_year]
            
            if len(pre_data) >= pre_treatment_periods:
                pre_outcome = pre_data.tail(pre_treatment_periods)[outcome].dropna()
                if len(pre_outcome) > 0:
                    pre_trend = pre_outcome.iloc[-1] - pre_outcome.iloc[0] if len(pre_outcome) > 1 else 0
                    pre_trend_groups.append({
                        'entity': entity,
                        'pre_treatment_trend': pre_trend,
                        'treated': 1
                    })
        else:
            # Control units
            control_data = entity_data.tail(pre_treatment_periods)
            control_outcome = control_data[outcome].dropna()
            if len(control_outcome) > 0:
                control_trend = control_outcome.iloc[-1] - control_outcome.iloc[0] if len(control_outcome) > 1 else 0
                pre_trend_groups.append({
                    'entity': entity,
                    'pre_treatment_trend': control_trend,
                    'treated': 0
                })
    
    if pre_trend_groups:
        pre_trends_df = pd.DataFrame(pre_trend_groups)
        
        treated_trends = pre_trends_df[pre_trends_df['treated'] == 1]['pre_treatment_trend']
        control_trends = pre_trends_df[pre_trends_df['treated'] == 0]['pre_treatment_trend']
        
        from scipy import stats as sp_stats
        if len(treated_trends) > 0 and len(control_trends) > 0:
            t_stat, p_value = sp_stats.ttest_ind(treated_trends, control_trends)
        else:
            t_stat, p_value = np.nan, np.nan
        
        report = {
            'test_name': 'preliminary_parallel_trends',
            'treated_mean_pre_trend': treated_trends.mean() if len(treated_trends) > 0 else np.nan,
            'control_mean_pre_trend': control_trends.mean() if len(control_trends) > 0 else np.nan,
            't_statistic': t_stat,
            'p_value': p_value,
            'parallel_plausible': p_value > 0.1 if not np.isnan(p_value) else np.nan,
        }
    else:
        report = {'error': 'Insufficient pre-treatment data'}
    
    return report


def validate_regression_assumptions(
    residuals: pd.Series,
    x_variable: pd.Series,
) -> Dict[str, any]:
    """
    Test classical linear regression assumptions on residuals.
    
    Parameters
    ----------
    residuals : pd.Series
        Model residuals.
    x_variable : pd.Series
        Independent variable (for heteroscedasticity test).
        
    Returns
    -------
    dict
        Assumption test results.
    """
    from scipy import stats as sp_stats
    
    # Clean data
    residuals_clean = residuals.dropna()
    
    if len(residuals_clean) < 3:
        return {'error': 'Insufficient observations'}
    
    # 1. Normality: Shapiro-Wilk test
    if len(residuals_clean) <= 5000:
        sw_stat, sw_pval = sp_stats.shapiro(residuals_clean)
    else:
        sw_stat, sw_pval = np.nan, np.nan  # Shapiro-Wilk not recommended for large samples
    
    # 2. Heteroscedasticity: Breusch-Pagan test approximation
    if len(x_variable) > 0 and len(residuals_clean) > 0:
        x_clean = x_variable[residuals_clean.index].dropna()
        
        if len(x_clean) > 2:
            # Simple correlation of squared residuals with X
            corr = np.corrcoef(x_clean, residuals_clean**2)[0, 1]
            bp_stat = corr * len(residuals_clean)
            bp_pval = 1 - sp_stats.chi2.cdf(bp_stat, 1)
        else:
            bp_stat, bp_pval = np.nan, np.nan
    else:
        bp_stat, bp_pval = np.nan, np.nan
    
    # 3. Mean of residuals (should be ~0)
    residual_mean = residuals_clean.mean()
    residual_se = residuals_clean.sem()
    
    return {
        'n_residuals': len(residuals_clean),
        'normality_sw_statistic': sw_stat,
        'normality_p_value': sw_pval,
        'normal_at_5pct': sw_pval > 0.05 if not np.isnan(sw_pval) else np.nan,
        'heteroscedasticity_bp_statistic': bp_stat,
        'heteroscedasticity_p_value': bp_pval,
        'homoscedastic_at_5pct': bp_pval > 0.05 if not np.isnan(bp_pval) else np.nan,
        'residual_mean': residual_mean,
        'residual_se': residual_se,
        'mean_significantly_nonzero': abs(residual_mean / residual_se) > 1.96,
    }


def generate_data_quality_report(
    df: pd.DataFrame,
    entity_col: str = 'ric',
    time_col: str = 'Year',
    treatment_col: str = 'green_bond_issue',
) -> str:
    """
    Generate comprehensive data quality report.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input data.
    entity_col : str, optional
        Entity identifier (default: 'ric').
    time_col : str, optional
        Time identifier (default: 'Year').
    treatment_col : str, optional
        Treatment column (default: 'green_bond_issue').
        
    Returns
    -------
    str
        Formatted report text.
    """
    report_lines = ["=" * 70, "DATA QUALITY REPORT", "=" * 70]
    
    # Panel structure
    panel_report = validate_panel_structure(df, entity_col, time_col)
    report_lines.append("\n📊 PANEL STRUCTURE")
    report_lines.append(f"   Entities: {panel_report['n_entities']}")
    report_lines.append(f"   Periods: {panel_report['n_periods']}")
    report_lines.append(f"   Total observations: {panel_report['n_observations']}")
    report_lines.append(f"   Balanced: {'Yes' if panel_report['is_balanced'] else 'No (unbalanced panel)'}")
    report_lines.append(f"   Missing combinations: {panel_report['missing_combinations']}")
    
    # Missing data
    missing_report = check_missing_data(df)
    report_lines.append("\n📋 MISSING DATA")
    report_lines.append(f"   Total missing: {missing_report['total_missing_cells']} cells ({missing_report['total_missing_pct']:.1f}%)")
    
    # Outliers
    outliers = detect_outliers(df)
    report_lines.append(f"\n⚠️  OUTLIERS DETECTED")
    report_lines.append(f"   Columns with outliers: {len(outliers)}")
    for col in list(outliers.keys())[:5]:
        report_lines.append(f"   - {col}: {len(outliers[col])} outliers")
    
    # Treatment variation
    treatment_report = validate_treatment_variation(df, treatment_col, entity_col, time_col)
    report_lines.append(f"\n🎯 TREATMENT VARIATION")
    report_lines.append(f"   Treated entities: {treatment_report['treated_entities']} / {treatment_report['total_entities']}")
    report_lines.append(f"   Treatment prevalence: {treatment_report['treatment_pct']:.1f}%")
    report_lines.append(f"   Timing range: {treatment_report['timing_range']} years")
    
    report_lines.append("\n" + "=" * 70)
    
    return "\n".join(report_lines)
