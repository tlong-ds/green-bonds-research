"""
Feature selection utilities for ASEAN Green Bonds research.

Methods for identifying key variables for econometric analysis.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LassoCV
from sklearn.preprocessing import StandardScaler
from typing import Tuple, List, Optional, Dict
import warnings

warnings.filterwarnings('ignore')


def calculate_vif(df: pd.DataFrame, exclude_cols: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Calculate Variance Inflation Factors (VIF) for multicollinearity detection.
    
    Parameters
    ----------
    df : pd.DataFrame
        Data with numeric features.
    exclude_cols : list, optional
        Columns to exclude from VIF calculation.
        
    Returns
    -------
    pd.DataFrame
        VIF report with columns: 'Variable', 'VIF'.
    """
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    
    if exclude_cols is None:
        exclude_cols = []
    
    # Select numeric columns
    X = df.select_dtypes(include=[np.number]).copy()
    X = X.drop(columns=[col for col in exclude_cols if col in X.columns], errors='ignore')
    
    # Remove columns with NaN
    X = X.dropna(axis=1, how='any')
    
    vif_data = pd.DataFrame()
    vif_data["Variable"] = X.columns
    vif_data["VIF"] = [
        variance_inflation_factor(X.values, i) for i in range(X.shape[1])
    ]
    
    return vif_data.sort_values('VIF', ascending=False)


def correlation_filter(
    df: pd.DataFrame,
    outcome: str,
    threshold: float = 0.1,
) -> List[str]:
    """
    Filter features by correlation with outcome variable.
    
    Parameters
    ----------
    df : pd.DataFrame
        Data with features and outcome.
    outcome : str
        Name of outcome variable.
    threshold : float, optional
        Minimum absolute correlation with outcome (default: 0.1).
        
    Returns
    -------
    list
        Features with sufficient correlation to outcome.
    """
    # Calculate correlations
    corr = df.corr()[outcome].abs().sort_values(ascending=False)
    
    # Filter by threshold (exclude outcome itself)
    features = corr[(corr >= threshold) & (corr.index != outcome)].index.tolist()
    
    return features


def lasso_feature_selection(
    X: pd.DataFrame,
    y: pd.Series,
    cv: int = 5,
    max_iter: int = 10000,
) -> Tuple[List[str], LassoCV]:
    """
    Select features using LassoCV (elastic net with cross-validation).
    
    Parameters
    ----------
    X : pd.DataFrame
        Feature matrix (n_samples, n_features).
    y : pd.Series
        Target variable (n_samples,).
    cv : int, optional
        Cross-validation folds (default: 5).
    max_iter : int, optional
        Maximum iterations (default: 10000).
        
    Returns
    -------
    tuple
        (selected_features: list, lasso_model: LassoCV)
    """
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Fit LassoCV
    lasso = LassoCV(cv=cv, max_iter=max_iter, random_state=42)
    lasso.fit(X_scaled, y)
    
    # Extract non-zero coefficients
    selected = X.columns[lasso.coef_ != 0].tolist()
    
    return selected, lasso


def stepwise_selection(
    X: pd.DataFrame,
    y: pd.Series,
    forward: bool = True,
    criterion: str = 'aic',
) -> List[str]:
    """
    Stepwise feature selection using AIC/BIC criterion.
    
    Parameters
    ----------
    X : pd.DataFrame
        Feature matrix.
    y : pd.Series
        Target variable.
    forward : bool, optional
        If True, forward selection; if False, backward (default: True).
    criterion : str, optional
        Model selection criterion: 'aic' or 'bic' (default: 'aic').
        
    Returns
    -------
    list
        Selected features in order.
    """
    from statsmodels.regression.linear_model import OLS
    
    # Remove NaN
    mask = X.notna().all(axis=1) & y.notna()
    X_clean = X[mask]
    y_clean = y[mask]
    
    if X_clean.shape[0] < 10:
        return X.columns.tolist()
    
    if forward:
        # Forward selection
        selected = []
        remaining = set(X_clean.columns)
        
        while remaining:
            best_feature = None
            best_score = np.inf
            
            for feature in remaining:
                features = selected + [feature]
                X_temp = X_clean[features]
                model = OLS(y_clean, X_temp).fit()
                
                score = model.aic if criterion == 'aic' else model.bic
                
                if score < best_score:
                    best_score = score
                    best_feature = feature
            
            if best_feature is None:
                break
            
            selected.append(best_feature)
            remaining.remove(best_feature)
            
            # Stop if all variables selected
            if len(remaining) == 0:
                break
        
        return selected
    
    else:
        # Backward selection
        selected = X_clean.columns.tolist()
        
        while len(selected) > 1:
            best_feature_to_remove = None
            best_score = np.inf
            
            for feature in selected:
                features = [f for f in selected if f != feature]
                if not features:
                    break
                
                X_temp = X_clean[features]
                model = OLS(y_clean, X_temp).fit()
                
                score = model.aic if criterion == 'aic' else model.bic
                
                if score < best_score:
                    best_score = score
                    best_feature_to_remove = feature
            
            if best_feature_to_remove is None:
                break
            
            selected.remove(best_feature_to_remove)
        
        return selected


def compile_selected_features(
    df: pd.DataFrame,
    outcome_cols: List[str],
    control_cols: List[str],
    lagged_cols: Optional[List[str]] = None,
    selection_method: str = 'union',
) -> Tuple[List[str], Dict[str, List[str]]]:
    """
    Compile final set of selected features across multiple methods.
    
    Parameters
    ----------
    df : pd.DataFrame
        Full panel data.
    outcome_cols : list
        Outcome variables to analyze.
    control_cols : list
        Core control variables.
    lagged_cols : list, optional
        Lagged variables for robustness.
    selection_method : str, optional
        How to combine selections: 'union', 'intersection', or 'consensus'
        (default: 'union').
        
    Returns
    -------
    tuple
        (final_features: list, selection_report: dict)
    """
    if lagged_cols is None:
        lagged_cols = []
    
    selection_report = {
        'control_variables': control_cols,
        'outcome_variables': outcome_cols,
        'lagged_variables': lagged_cols,
        'methods': {},
        'final_features': [],
    }
    
    # Prepare data
    X = df[control_cols + lagged_cols].dropna()
    
    # Method 1: Correlation filtering
    corr_features = set(control_cols)  # Always keep core controls
    for outcome in outcome_cols:
        y = df.loc[X.index, outcome].dropna()
        if len(y) > 10:
            corr_feats = correlation_filter(df.loc[X.index], outcome, threshold=0.05)
            corr_features.update(corr_feats)
    
    selection_report['methods']['correlation'] = list(corr_features)
    
    # Method 2: VIF check
    vif_report = calculate_vif(X, exclude_cols=['ric', 'Year', 'country'])
    high_vif = vif_report[vif_report['VIF'] > 10]['Variable'].tolist()
    vif_features = [f for f in control_cols + lagged_cols if f not in high_vif]
    
    selection_report['methods']['vif_filtering'] = vif_features
    
    # Combine based on method
    if selection_method == 'union':
        final = list(set(corr_features) | set(vif_features))
    elif selection_method == 'intersection':
        final = list(set(corr_features) & set(vif_features))
    else:  # consensus
        final = [f for f in control_cols if f in corr_features and f in vif_features]
        final += lagged_cols
    
    final = sorted(final)
    selection_report['final_features'] = final
    
    return final, selection_report


def create_feature_selection_report(
    df: pd.DataFrame,
    selected_features: List[str],
    outcome_cols: List[str],
) -> pd.DataFrame:
    """
    Create a summary report of feature selection.
    
    Parameters
    ----------
    df : pd.DataFrame
        Full panel data.
    selected_features : list
        Selected feature names.
    outcome_cols : list
        Outcome variable names.
        
    Returns
    -------
    pd.DataFrame
        Feature selection report with descriptive statistics.
    """
    report_data = []
    
    for feature in selected_features:
        if feature not in df.columns:
            continue
        
        row = {
            'Feature': feature,
            'Type': 'numeric' if df[feature].dtype in [np.float64, np.int64] else 'categorical',
            'Non_Missing_Count': df[feature].notna().sum(),
            'Missing_Pct': (df[feature].isna().sum() / len(df) * 100),
            'Mean': df[feature].mean() if df[feature].dtype in [np.float64, np.int64] else np.nan,
            'Std': df[feature].std() if df[feature].dtype in [np.float64, np.int64] else np.nan,
        }
        
        # Add correlations with outcomes
        for outcome in outcome_cols:
            if outcome in df.columns:
                corr = df[[feature, outcome]].corr().iloc[0, 1]
                row[f'Corr_with_{outcome}'] = corr
        
        report_data.append(row)
    
    return pd.DataFrame(report_data)
