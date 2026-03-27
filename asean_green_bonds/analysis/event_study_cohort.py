"""
Cohort-specific event study for staggered Difference-in-Differences.

Implements a lightweight Callaway & Sant'Anna (2021)-style decomposition
by estimating separate DiD models for each treatment cohort against
never-treated firms, then aggregating to a cohort-weighted ATT.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from .difference_in_diff import estimate_did


def identify_cohorts(
    df: pd.DataFrame,
    treatment_col: str = 'green_bond_active',
    entity_col: str = 'org_permid',
    time_col: str = 'Year',
) -> pd.Series:
    """
    Identify the first treatment year (cohort) for each entity.

    Parameters
    ----------
    df : pd.DataFrame
        Panel data.
    treatment_col : str
        Binary treatment indicator.
    entity_col : str
        Entity identifier.
    time_col : str
        Time identifier.

    Returns
    -------
    pd.Series
        Index = entity, value = first treatment year (NaN for never-treated).
    """
    treated = df[df[treatment_col] == 1]
    if treated.empty:
        return pd.Series(dtype=float)
    first_treat = treated.groupby(entity_col)[time_col].min()
    return first_treat


def cohort_specific_did(
    df: pd.DataFrame,
    outcome: str,
    treatment_col: str = 'green_bond_active',
    entity_col: str = 'org_permid',
    time_col: str = 'Year',
    control_vars: Optional[List[str]] = None,
    specification: str = 'entity_fe',
) -> pd.DataFrame:
    """
    Estimate DiD separately for each treatment cohort vs never-treated.

    For each cohort g (first-treatment-year), restricts the sample to:
      - Firms first treated in year g
      - Firms never treated (green_bond_active == 0 in all years)

    Then estimates a standard DiD on this restricted sample.

    Parameters
    ----------
    df : pd.DataFrame
        Full panel data.
    outcome : str
        Outcome variable.
    treatment_col : str
        Binary treatment column.
    entity_col : str
        Entity identifier.
    time_col : str
        Time identifier.
    control_vars : list, optional
        Control variables.
    specification : str
        FE specification (default: 'entity_fe').

    Returns
    -------
    pd.DataFrame
        One row per cohort with columns: cohort, n_treated, n_control,
        coefficient, std_error, p_value, n_obs, pre_trend_coef, pre_trend_p.
    """
    if control_vars is None:
        control_vars = []

    # Identify cohorts
    cohorts = identify_cohorts(df, treatment_col, entity_col, time_col)
    if cohorts.empty:
        return pd.DataFrame()

    # Identify never-treated entities
    ever_treated = df[df[treatment_col] == 1][entity_col].unique()
    never_treated = df[~df[entity_col].isin(ever_treated)][entity_col].unique()

    results = []

    for cohort_year in sorted(cohorts.unique()):
        # Cohort-g entities
        cohort_entities = cohorts[cohorts == cohort_year].index.tolist()
        n_treated = len(cohort_entities)

        # Restrict sample: cohort-g treated + never-treated
        valid_entities = list(cohort_entities) + list(never_treated)
        df_cohort = df[df[entity_col].isin(valid_entities)].copy()
        n_control = df_cohort[df_cohort[entity_col].isin(never_treated)][entity_col].nunique()

        # Run DiD on restricted sample
        did_result = estimate_did(
            df_cohort,
            outcome=outcome,
            treatment_col=treatment_col,
            entity_col=entity_col,
            time_col=time_col,
            control_vars=control_vars,
            specification=specification,
            cluster_entity=True,
        )

        row = {
            'cohort': int(cohort_year),
            'n_treated_firms': n_treated,
            'n_control_firms': n_control,
            'n_obs': did_result.get('n_obs', len(df_cohort)),
            'coefficient': did_result.get('coefficient', np.nan),
            'std_error': did_result.get('std_error', np.nan),
            'p_value': did_result.get('p_value', np.nan),
            'error': did_result.get('error'),
        }

        # Pre-trend test for this cohort (if enough pre-treatment data)
        years_before = int(cohort_year) - df[time_col].min()
        if years_before >= 1:
            pre_df = df_cohort[df_cohort[time_col] < cohort_year].copy()
            # Create a pre-treatment trend indicator
            pre_df['pre_trend'] = pre_df[entity_col].isin(cohort_entities).astype(int)
            pre_df['relative_time'] = pre_df[time_col] - cohort_year
            pre_df['pre_trend_interaction'] = pre_df['pre_trend'] * pre_df['relative_time']

            try:
                from linearmodels.panel import PanelOLS
                pre_reg = pre_df.set_index([entity_col, time_col])
                y = pre_reg[outcome].dropna()
                X = pre_reg[['pre_trend_interaction']].reindex(y.index).dropna()
                y = y.reindex(X.index)

                if len(y) > 10 and X['pre_trend_interaction'].std() > 0:
                    model = PanelOLS(y, X, entity_effects=True, check_rank=False)
                    res = model.fit(cov_type='clustered', cluster_entity=True)
                    row['pre_trend_coef'] = float(res.params.iloc[0])
                    row['pre_trend_p'] = float(res.pvalues.iloc[0])
                else:
                    row['pre_trend_coef'] = np.nan
                    row['pre_trend_p'] = np.nan
            except Exception:
                row['pre_trend_coef'] = np.nan
                row['pre_trend_p'] = np.nan
        else:
            row['pre_trend_coef'] = np.nan
            row['pre_trend_p'] = np.nan

        results.append(row)

    return pd.DataFrame(results)


def aggregate_cohort_att(
    cohort_results: pd.DataFrame,
    weight_by: str = 'n_treated_firms',
) -> Dict[str, Any]:
    """
    Aggregate cohort-specific effects into an overall ATT.

    Uses cohort-size weighting following Callaway & Sant'Anna (2021).

    Parameters
    ----------
    cohort_results : pd.DataFrame
        Output from cohort_specific_did().
    weight_by : str
        Column to use as weights (default: 'n_treated_firms').

    Returns
    -------
    dict
        Aggregated ATT, standard error, and per-cohort breakdown.
    """
    valid = cohort_results.dropna(subset=['coefficient'])
    if valid.empty:
        return {'error': 'No valid cohort estimates'}

    weights = valid[weight_by].values.astype(float)
    total_weight = weights.sum()
    if total_weight == 0:
        return {'error': 'All weights are zero'}

    # Weighted ATT
    att = np.average(valid['coefficient'].values, weights=weights)

    # Weighted SE (assuming independence across cohorts)
    se = np.sqrt(np.average(valid['std_error'].values ** 2, weights=weights))

    # Check pre-trends
    pre_valid = valid.dropna(subset=['pre_trend_p'])
    n_violated = (pre_valid['pre_trend_p'] < 0.05).sum() if len(pre_valid) > 0 else 0

    return {
        'aggregated_att': att,
        'aggregated_se': se,
        'aggregated_p': float(2 * (1 - __import__('scipy').stats.norm.cdf(abs(att / se)))) if se > 0 else np.nan,
        'n_cohorts': len(valid),
        'total_treated_firms': int(total_weight),
        'pre_trend_violations': n_violated,
        'cohort_details': valid[['cohort', 'n_treated_firms', 'coefficient', 'std_error', 'p_value',
                                  'pre_trend_coef', 'pre_trend_p']].to_dict('records'),
    }
