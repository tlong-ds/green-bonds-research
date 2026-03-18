"""
Event study analysis for ASEAN Green Bonds research.

Analyzes stock market reactions to green bond announcements and issuances.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional, List, Dict
from datetime import timedelta
import warnings

warnings.filterwarnings('ignore')


def calculate_abnormal_returns(
    df: pd.DataFrame,
    event_date_col: str,
    return_col: str = 'stock_return',
    window_start: int = -5,
    window_end: int = 5,
    estimation_window: int = 120,
) -> Tuple[pd.DataFrame, Dict[str, any]]:
    """
    Calculate abnormal returns around event date using mean-adjusted model.
    
    Parameters
    ----------
    df : pd.DataFrame
        Time series data with dates, returns, and event indicators.
    event_date_col : str
        Column name with event dates.
    return_col : str, optional
        Column name with stock returns (default: 'stock_return').
    window_start : int, optional
        Start of event window relative to event (default: -5).
    window_end : int, optional
        End of event window relative to event (default: 5).
    estimation_window : int, optional
        Days for estimating expected returns (default: 120).
        
    Returns
    -------
    tuple
        (abnormal_returns: pd.DataFrame, statistics: dict)
    """
    df = df.copy()
    df[event_date_col] = pd.to_datetime(df[event_date_col])
    
    abnormal_returns_list = []
    
    for event_date in df[event_date_col].dropna().unique():
        # Define windows
        est_start = event_date - timedelta(days=estimation_window)
        window_start_date = event_date + timedelta(days=window_start)
        window_end_date = event_date + timedelta(days=window_end)
        
        # Estimation period returns
        est_data = df[(df.index >= est_start) & (df.index < event_date)]
        if len(est_data) > 10:
            expected_return = est_data[return_col].mean()
        else:
            expected_return = 0
        
        # Event window returns
        event_data = df[(df.index >= window_start_date) & (df.index <= window_end_date)]
        
        for date, ret in event_data[return_col].items():
            days_from_event = (date - event_date).days
            abnormal_return = ret - expected_return
            
            abnormal_returns_list.append({
                'event_date': event_date,
                'date': date,
                'days_from_event': days_from_event,
                'actual_return': ret,
                'expected_return': expected_return,
                'abnormal_return': abnormal_return,
            })
    
    ar_df = pd.DataFrame(abnormal_returns_list)
    
    # Statistics
    stats = {
        'n_events': len(df[event_date_col].dropna().unique()),
        'mean_ar': ar_df['abnormal_return'].mean(),
        'std_ar': ar_df['abnormal_return'].std(),
        'cumulative_ar': ar_df['abnormal_return'].sum(),
    }
    
    return ar_df, stats


def calculate_cumulative_abnormal_returns(
    abnormal_returns_df: pd.DataFrame,
    groupby_col: str = 'days_from_event',
) -> pd.DataFrame:
    """
    Calculate cumulative abnormal returns by event window period.
    
    Parameters
    ----------
    abnormal_returns_df : pd.DataFrame
        Output from calculate_abnormal_returns().
    groupby_col : str, optional
        Column to group by for aggregation (default: 'days_from_event').
        
    Returns
    -------
    pd.DataFrame
        Cumulative AR by period with mean, SD, t-stat, p-value.
    """
    from scipy import stats as sp_stats
    
    grouped = abnormal_returns_df.groupby(groupby_col)['abnormal_return']
    
    car_results = []
    
    for period, returns in grouped:
        n = len(returns)
        mean_ar = returns.mean()
        std_ar = returns.std()
        
        # T-statistic
        t_stat = (mean_ar / (std_ar / np.sqrt(n))) if std_ar > 0 and n > 1 else 0
        p_value = 2 * (1 - sp_stats.t.cdf(abs(t_stat), n - 1)) if not np.isnan(t_stat) else 1
        
        car_results.append({
            groupby_col: period,
            'n_observations': n,
            'mean_ar': mean_ar,
            'std_ar': std_ar,
            't_statistic': t_stat,
            'p_value': p_value,
            'significant_5pct': abs(t_stat) > 1.96,
        })
    
    return pd.DataFrame(car_results).sort_values(groupby_col)


def analyze_market_reaction_by_firm(
    df: pd.DataFrame,
    firm_col: str,
    event_date_col: str,
    return_col: str = 'stock_return',
    event_type: str = 'issuance',
) -> pd.DataFrame:
    """
    Analyze market reactions separately for each firm.
    
    Parameters
    ----------
    df : pd.DataFrame
        Time series data with firms, events, and returns.
    firm_col : str
        Firm identifier column.
    event_date_col : str
        Event date column.
    return_col : str, optional
        Returns column (default: 'stock_return').
    event_type : str, optional
        Type of event for reporting (default: 'issuance').
        
    Returns
    -------
    pd.DataFrame
        Firm-level market reaction statistics.
    """
    df = df.copy()
    df[event_date_col] = pd.to_datetime(df[event_date_col])
    
    firm_reactions = []
    
    for firm in df[firm_col].unique():
        firm_data = df[df[firm_col] == firm]
        event_dates = firm_data[event_date_col].dropna().unique()
        
        if len(event_dates) == 0:
            continue
        
        for event_date in event_dates:
            # Event window: -1 to +1
            window_start = event_date - timedelta(days=1)
            window_end = event_date + timedelta(days=1)
            
            event_window = firm_data[
                (firm_data.index >= window_start) & (firm_data.index <= window_end)
            ][return_col]
            
            if len(event_window) > 0:
                firm_reactions.append({
                    'firm': firm,
                    'event_date': event_date,
                    'event_type': event_type,
                    'mean_return_event_window': event_window.mean(),
                    'n_trading_days': len(event_window),
                })
    
    return pd.DataFrame(firm_reactions)


def test_event_significance(
    abnormal_returns_df: pd.DataFrame,
    window_start: int = -5,
    window_end: int = 5,
) -> Dict[str, any]:
    """
    Test statistical significance of abnormal returns in event window.
    
    Parameters
    ----------
    abnormal_returns_df : pd.DataFrame
        Abnormal returns from calculate_abnormal_returns().
    window_start : int, optional
        Window start (default: -5).
    window_end : int, optional
        Window end (default: 5).
        
    Returns
    -------
    dict
        Significance test results (t-stat, p-value, effect size).
    """
    from scipy import stats as sp_stats
    
    window_data = abnormal_returns_df[
        (abnormal_returns_df['days_from_event'] >= window_start) &
        (abnormal_returns_df['days_from_event'] <= window_end)
    ]['abnormal_return']
    
    if len(window_data) < 2:
        return {
            'error': 'Insufficient observations',
            'n_obs': len(window_data),
        }
    
    # One-sample t-test: H0: mean AR = 0
    t_stat, p_value = sp_stats.ttest_1samp(window_data, 0)
    
    # Effect size (Cohen's d)
    cohens_d = window_data.mean() / window_data.std() if window_data.std() > 0 else 0
    
    return {
        'window': (window_start, window_end),
        'n_observations': len(window_data),
        'mean_ar': window_data.mean(),
        'std_ar': window_data.std(),
        't_statistic': t_stat,
        'p_value': p_value,
        'cohens_d': cohens_d,
        'significant_5pct': abs(t_stat) > 1.96,
        'significant_10pct': abs(t_stat) > 1.645,
    }


def run_event_study_analysis(
    df: pd.DataFrame,
    event_indicator_col: str,
    outcome_col: str,
    entity_col: str,
    time_col: str,
    window_days: Tuple[int, int] = (-5, 5),
    estimation_days: int = 120,
) -> Dict[str, any]:
    """
    Comprehensive event study analysis.
    
    Parameters
    ----------
    df : pd.DataFrame
        Panel data with events and outcomes.
    event_indicator_col : str
        Column indicating event occurrence (binary).
    outcome_col : str
        Outcome variable to analyze.
    entity_col : str
        Entity identifier.
    time_col : str
        Time identifier.
    window_days : tuple, optional
        Event window (start, end) in days (default: (-5, 5)).
    estimation_days : int, optional
        Days for estimation period (default: 120).
        
    Returns
    -------
    dict
        Complete event study results including AR, CAR, tests, visualization data.
    """
    df = df.copy()
    df[time_col] = pd.to_datetime(df[time_col])
    
    # Get event dates
    event_data = df[df[event_indicator_col] == 1]
    events_by_entity = event_data.groupby(entity_col)[time_col].apply(list)
    
    # Run for each entity
    all_results = {
        'by_entity': {},
        'overall': {},
    }
    
    for entity, dates in events_by_entity.items():
        entity_data = df[df[entity_col] == entity].set_index(time_col)
        
        for event_date in dates:
            try:
                ar, stats = calculate_abnormal_returns(
                    entity_data,
                    event_indicator_col,
                    outcome_col,
                    window_days[0],
                    window_days[1],
                    estimation_days
                )
                
                if entity not in all_results['by_entity']:
                    all_results['by_entity'][entity] = []
                
                all_results['by_entity'][entity].append({
                    'event_date': event_date,
                    'stats': stats,
                })
            except Exception as e:
                warnings.warn(f"Error for {entity} on {event_date}: {e}")
    
    # Aggregate overall results
    all_ar = pd.concat(
        [ar for entity_results in all_results['by_entity'].values()
         for ar in entity_results],
        ignore_index=True
    ) if all_results['by_entity'] else pd.DataFrame()
    
    if len(all_ar) > 0:
        all_results['overall'] = {
            'car_by_day': calculate_cumulative_abnormal_returns(all_ar),
            'significance_test': test_event_significance(all_ar, window_days[0], window_days[1]),
            'n_events': len(events_by_entity.values()),
            'total_observations': len(all_ar),
        }
    
    return all_results
