"""
Visualization utilities for ASEAN Green Bonds research.

Functions for creating publication-quality plots and figures.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, Tuple, List, Dict
import warnings

warnings.filterwarnings('ignore')

# Set default style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


def plot_propensity_score_overlap(
    df: pd.DataFrame,
    ps_col: str = 'propensity_score',
    treatment_col: str = 'green_bond_issue',
    figsize: Tuple[int, int] = (10, 6),
    save_path: Optional[str] = None,
) -> plt.Figure:
    """
    Plot propensity score distribution by treatment group.
    
    Parameters
    ----------
    df : pd.DataFrame
        Data with propensity scores.
    ps_col : str, optional
        Propensity score column (default: 'propensity_score').
    treatment_col : str, optional
        Treatment column (default: 'green_bond_issue').
    figsize : tuple, optional
        Figure size (default: (10, 6)).
    save_path : str, optional
        Path to save figure. If None, not saved.
        
    Returns
    -------
    matplotlib.figure.Figure
        Figure object.
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    treated = df[df[treatment_col] == 1][ps_col].dropna()
    control = df[df[treatment_col] == 0][ps_col].dropna()
    
    # Plot histograms
    ax.hist(control, bins=30, alpha=0.6, label=f'Control (n={len(control)})', color='blue')
    ax.hist(treated, bins=30, alpha=0.6, label=f'Treated (n={len(treated)})', color='red')
    
    ax.set_xlabel('Propensity Score', fontsize=11)
    ax.set_ylabel('Frequency', fontsize=11)
    ax.set_title('Propensity Score Distribution: Common Support Check', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_covariate_balance(
    balance_df: pd.DataFrame,
    figsize: Tuple[int, int] = (12, 8),
    save_path: Optional[str] = None,
    threshold: float = 0.1,
) -> plt.Figure:
    """
    Create love plot for covariate balance assessment.
    
    Parameters
    ----------
    balance_df : pd.DataFrame
        Output from assess_balance().
    figsize : tuple, optional
        Figure size (default: (12, 8)).
    save_path : str, optional
        Path to save figure.
    threshold : float, optional
        Balance threshold (default: 0.1).
        
    Returns
    -------
    matplotlib.figure.Figure
        Figure object.
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Sort by absolute standardized difference
    balance_df_sorted = balance_df.sort_values('Std_Difference', key=abs)
    
    # Create plot
    colors = ['green' if abs(x) < threshold else 'red' 
              for x in balance_df_sorted['Std_Difference']]
    
    y_pos = np.arange(len(balance_df_sorted))
    ax.barh(y_pos, balance_df_sorted['Std_Difference'], color=colors, alpha=0.7)
    
    # Add threshold lines
    ax.axvline(-threshold, color='black', linestyle='--', linewidth=1, label=f'Threshold (±{threshold})')
    ax.axvline(threshold, color='black', linestyle='--', linewidth=1)
    ax.axvline(0, color='black', linestyle='-', linewidth=1)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(balance_df_sorted['Feature'])
    ax.set_xlabel('Standardized Mean Difference', fontsize=11)
    ax.set_title('Covariate Balance After Matching', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='x')
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_did_results(
    results_df: pd.DataFrame,
    figsize: Tuple[int, int] = (12, 8),
    save_path: Optional[str] = None,
) -> plt.Figure:
    """
    Plot DiD coefficients across outcomes and specifications.
    
    Parameters
    ----------
    results_df : pd.DataFrame
        Output from run_multiple_outcomes().
    figsize : tuple, optional
        Figure size (default: (12, 8)).
    save_path : str, optional
        Path to save figure.
        
    Returns
    -------
    matplotlib.figure.Figure
        Figure object.
    """
    fig, axes = plt.subplots(figsize=figsize)
    
    # Prepare data for plotting
    results_df['label'] = results_df['outcome'] + '\n' + results_df['specification']
    
    # Create plot
    x_pos = np.arange(len(results_df))
    colors = ['green' if p < 0.05 else 'blue' for p in results_df['p_value']]
    
    axes.bar(x_pos, results_df['coefficient'], color=colors, alpha=0.7, capsize=5)
    
    # Add error bars
    axes.errorbar(x_pos, results_df['coefficient'], 
                  yerr=1.96*results_df['std_error'], 
                  fmt='none', color='black', capsize=5)
    
    axes.set_xticks(x_pos)
    axes.set_xticklabels(results_df['label'], rotation=45, ha='right')
    axes.set_ylabel('Treatment Coefficient', fontsize=11)
    axes.set_title('DiD Treatment Effects Across Specifications', fontsize=12, fontweight='bold')
    axes.axhline(0, color='black', linestyle='-', linewidth=1)
    axes.grid(True, alpha=0.3, axis='y')
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_event_study(
    car_df: pd.DataFrame,
    figsize: Tuple[int, int] = (10, 6),
    save_path: Optional[str] = None,
) -> plt.Figure:
    """
    Plot cumulative abnormal returns around event.
    
    Parameters
    ----------
    car_df : pd.DataFrame
        CAR results from calculate_cumulative_abnormal_returns().
    figsize : tuple, optional
        Figure size (default: (10, 6)).
    save_path : str, optional
        Path to save figure.
        
    Returns
    -------
    matplotlib.figure.Figure
        Figure object.
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot CAR
    ax.plot(car_df['days_from_event'], car_df['mean_ar'], 
            marker='o', color='blue', linewidth=2, label='CAR')
    
    # Add confidence band (±1 SE)
    se = car_df['std_ar'] / np.sqrt(car_df['n_observations'])
    ax.fill_between(car_df['days_from_event'], 
                    car_df['mean_ar'] - 1.96*se,
                    car_df['mean_ar'] + 1.96*se,
                    alpha=0.2, color='blue', label='95% CI')
    
    # Highlight event day
    ax.axvline(0, color='red', linestyle='--', linewidth=2, label='Event Day')
    ax.axhline(0, color='black', linestyle='-', linewidth=1)
    
    ax.set_xlabel('Days from Event', fontsize=11)
    ax.set_ylabel('Cumulative Abnormal Return', fontsize=11)
    ax.set_title('Event Study: Market Reaction to Green Bond Announcement', 
                 fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_specification_sensitivity(
    spec_df: pd.DataFrame,
    figsize: Tuple[int, int] = (10, 6),
    save_path: Optional[str] = None,
) -> plt.Figure:
    """
    Plot treatment coefficient across specifications.
    
    Parameters
    ----------
    spec_df : pd.DataFrame
        Specification sensitivity results.
    figsize : tuple, optional
        Figure size (default: (10, 6)).
    save_path : str, optional
        Path to save figure.
        
    Returns
    -------
    matplotlib.figure.Figure
        Figure object.
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Filter error rows
    spec_df_clean = spec_df.dropna(subset=['coefficient'])
    
    x_pos = np.arange(len(spec_df_clean))
    
    # Plot coefficients with error bars
    ax.bar(x_pos, spec_df_clean['coefficient'], alpha=0.7, color='steelblue', capsize=5)
    ax.errorbar(x_pos, spec_df_clean['coefficient'],
                yerr=1.96*spec_df_clean['std_error'],
                fmt='none', color='black', capsize=5)
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(spec_df_clean['specification'])
    ax.set_ylabel('Treatment Coefficient', fontsize=11)
    ax.set_title('Specification Sensitivity: Control Variable Choices', 
                 fontsize=12, fontweight='bold')
    ax.axhline(0, color='black', linestyle='-', linewidth=1)
    ax.grid(True, alpha=0.3, axis='y')
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_parallel_trends(
    pt_results: Dict,
    figsize: Tuple[int, int] = (10, 6),
    save_path: Optional[str] = None,
) -> plt.Figure:
    """
    Plot parallel trends test (leads/lags).
    
    Parameters
    ----------
    pt_results : dict
        Parallel trends test results.
    figsize : tuple, optional
        Figure size (default: (10, 6)).
    save_path : str, optional
        Path to save figure.
        
    Returns
    -------
    matplotlib.figure.Figure
        Figure object.
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Extract coefficients and labels
    coefs = pt_results['coefficients']
    
    # Sort by period
    periods = []
    values = []
    
    def sort_key(item):
        key = item[0]
        if 'lead' in key:
            # treatment_lead_X format
            try:
                lead_num = int(key.split('_')[2])
                return (0, -lead_num)  # Leads first, in reverse order
            except (IndexError, ValueError):
                return (2, 0)  # Fallback for non-standard format
        elif 'lag' in key:
            # treatment_lag_X format
            try:
                lag_num = int(key.split('_')[2])
                return (2, lag_num)  # Lags last, in order
            except (IndexError, ValueError):
                return (2, 0)  # Fallback
        else:
            # Current treatment (green_bond_active)
            return (1, 0)  # Middle position
    
    for key, val in sorted(coefs.items(), key=sort_key):
        periods.append(key.replace('treatment_', ''))
        values.append(val)
    
    x_pos = np.arange(len(periods))
    colors = ['red' if 'lead' in p else 'green' for p in periods]
    
    ax.bar(x_pos, values, color=colors, alpha=0.7)
    ax.axhline(0, color='black', linestyle='-', linewidth=2)
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(periods, rotation=45, ha='right')
    ax.set_ylabel('Coefficient', fontsize=11)
    ax.set_title('Parallel Trends Test: Leads and Lags of Treatment', 
                 fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_summary_statistics(
    summary_df: pd.DataFrame,
    figsize: Tuple[int, int] = (12, 8),
    save_path: Optional[str] = None,
) -> plt.Figure:
    """
    Create summary statistics visualization.
    
    Parameters
    ----------
    summary_df : pd.DataFrame
        Summary statistics table.
    figsize : tuple, optional
        Figure size (default: (12, 8)).
    save_path : str, optional
        Path to save figure.
        
    Returns
    -------
    matplotlib.figure.Figure
        Figure object.
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Create table
    table_data = summary_df[['Variable', 'N', 'Mean', 'Std_Dev', 'Min', 'Max']].values
    columns = ['Variable', 'N', 'Mean', 'Std Dev', 'Min', 'Max']
    
    table = ax.table(cellText=np.round(table_data, 3), 
                    colLabels=columns,
                    cellLoc='center',
                    loc='center')
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    ax.axis('off')
    ax.set_title('Summary Statistics', fontsize=12, fontweight='bold', pad=20)
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig
