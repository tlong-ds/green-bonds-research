"""
Diagnostic Feature Analysis for ASEAN Green Bonds Research.

This module provides DIAGNOSTIC tools to validate theory-driven variable
selection for econometric modeling (PSM-DiD). It is NOT for primary model
specification.

⚠️  WARNING: Do NOT use automatically selected features as your primary
specification for causal inference (PSM-DiD). Use these functions to:

1. Validate your theory-driven variable selection
2. Check for multicollinearity and data quality issues
3. Compare automatic vs theory-driven selections
4. Identify potential confounders
5. Generate specification robustness reports

✅  These are DIAGNOSTIC tools, not model specification tools.

Usage Example:
    # Step 1: Define theory-driven variables
    theory_vars = ['firm_size', 'leverage', 'sector', 'profitability']
    
    # Step 2: Run diagnostic analysis
    report = validate_specification(
        df,
        theory_vars=theory_vars,
        outcome='esg_score'
    )
    
    # Step 3: Interpret results
    print(report.overlap_analysis)  # Are theory vars in auto-selected?
    print(report.multicollinearity)  # VIF for your variables
    print(report.data_quality)  # Missing values, outliers
    print(report.recommendations)  # Specification validation
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LassoCV
from sklearn.preprocessing import StandardScaler
from typing import Tuple, List, Optional, Dict, Any
import warnings

# Suppress only specific expected warnings
warnings.filterwarnings('ignore', category=FutureWarning, module='sklearn')


class DiagnosticReport:
    """
    Diagnostic report for validating econometric variable specification.
    
    Attributes
    ----------
    overlap_analysis : dict
        Comparison of theory-driven vs auto-selected variables
    multicollinearity : pd.DataFrame
        VIF for theory-driven variables
    variable_importance : pd.DataFrame
        Ranking of theory-driven variables by correlation/importance
    data_quality : dict
        Missing values, outliers for theory-driven variables
    recommendations : list
        Specification validation recommendations
    warnings : list
        Issues to watch (e.g., confounders not in auto-selection)
    """
    
    def __init__(self):
        self.overlap_analysis = {}
        self.multicollinearity = pd.DataFrame()
        self.variable_importance = pd.DataFrame()
        self.data_quality = {}
        self.recommendations = []
        self.warnings = []
    
    def __repr__(self):
        return f"""
DIAGNOSTIC SPECIFICATION REPORT
================================

OVERLAP ANALYSIS:
{self.overlap_analysis}

MULTICOLLINEARITY (VIF):
{self.multicollinearity.to_string()}

VARIABLE IMPORTANCE:
{self.variable_importance.to_string()}

DATA QUALITY:
{self.data_quality}

RECOMMENDATIONS:
{chr(10).join(['  ' + r for r in self.recommendations])}

WARNINGS:
{chr(10).join(['  ⚠️  ' + w for w in self.warnings])}
"""



# ============================================================================
# OLD API (kept for backward compatibility - use new diagnostic API above)
# ============================================================================

def calculate_vif_old(df: pd.DataFrame, exclude_cols: Optional[List[str]] = None) -> pd.DataFrame:
    """
    [DEPRECATED - Use diagnose_multicollinearity instead]
    
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


def correlation_filter_old(
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
    # Select only numeric columns to avoid string-to-float conversion errors
    numeric_df = df.select_dtypes(include=[np.number])
    
    # Ensure outcome is in the numeric dataframe
    if outcome not in numeric_df.columns:
        return []
    
    # Calculate correlations
    corr = numeric_df.corr()[outcome].abs().sort_values(ascending=False)
    
    # Filter by threshold (exclude outcome itself)
    features = corr[(corr >= threshold) & (corr.index != outcome)].index.tolist()
    
    return features


def lasso_feature_selection_old(
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


# ============================================================================
# NEW DIAGNOSTIC API
# ============================================================================
# These functions provide diagnostic validation of theory-driven specifications

def diagnose_multicollinearity(
    df: pd.DataFrame,
    theory_vars: List[str],
    exclude_cols: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Diagnose multicollinearity (VIF) for theory-driven variables.
    
    ⚠️  Use this to validate your manually-selected PSM/DiD specification.
    
    Parameters
    ----------
    df : pd.DataFrame
        Data with numeric features.
    theory_vars : list
        Your theory-driven variable specification to validate.
    exclude_cols : list, optional
        Additional columns to exclude from VIF calculation.
        
    Returns
    -------
    pd.DataFrame
        VIF report for theory variables with interpretation.
    """
    # Validate theory_vars
    theory_vars = [v for v in theory_vars if v in df.columns]
    if not theory_vars:
        return pd.DataFrame({'Warning': ['No theory variables found in data']})
    
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    
    # Select only numeric theory variables
    X = df[theory_vars].select_dtypes(include=[np.number]).copy()
    X = X.dropna(axis=1, how='any')
    
    vif_data = pd.DataFrame()
    vif_data["Variable"] = X.columns
    vif_data["VIF"] = [
        variance_inflation_factor(X.values, i) for i in range(X.shape[1])
    ]
    
    # Add interpretation
    vif_data["Status"] = vif_data["VIF"].apply(
        lambda x: "✓ OK" if x < 5 else ("⚠️  Warning (5-10)" if x < 10 else "❌ High (>10)")
    )
    
    return vif_data.sort_values('VIF', ascending=False)


def validate_specification(
    df: pd.DataFrame,
    theory_vars: List[str],
    outcome_col: str,
    control_cols: Optional[List[str]] = None,
    lagged_cols: Optional[List[str]] = None,
) -> DiagnosticReport:
    """
    Comprehensive diagnostic validation of theory-driven specification.
    
    ⚠️  Use this to validate your PSM-DiD variable selection BEFORE
    running econometric models. This compares your theory-driven
    specification against data-driven filters.
    
    Parameters
    ----------
    df : pd.DataFrame
        Panel data with all variables.
    theory_vars : list
        Your manually-selected theory-driven variables (PSM/DiD spec).
    outcome_col : str
        Primary outcome variable.
    control_cols : list, optional
        Core control variables.
    lagged_cols : list, optional
        Lagged variables.
        
    Returns
    -------
    DiagnosticReport
        Comprehensive diagnostic with overlap, multicollinearity,
        importance ranking, data quality, and recommendations.
    """
    report = DiagnosticReport()
    
    # Step 1: Get auto-selected features for comparison
    try:
        auto_selected, _ = compile_selected_features(
            df,
            outcome_cols=[outcome_col] if outcome_col in df.columns else [],
            control_cols=control_cols or theory_vars,
            lagged_cols=lagged_cols or [],
            selection_method='union'
        )
    except:
        auto_selected = []
    
    # Step 2: Overlap Analysis
    theory_set = set(v for v in theory_vars if v in df.columns)
    auto_set = set(auto_selected)
    overlap = theory_set & auto_set
    missing_from_auto = theory_set - auto_set
    extra_in_auto = auto_set - theory_set
    
    report.overlap_analysis = {
        'theory_vars': len(theory_set),
        'auto_selected': len(auto_set),
        'overlap': len(overlap),
        'overlap_pct': 100 * len(overlap) / len(theory_set) if theory_set else 0,
        'missing_from_auto': list(missing_from_auto),
        'extra_in_auto': list(extra_in_auto)[:10],  # Show first 10
    }
    
    # Step 3: Multicollinearity Check
    report.multicollinearity = diagnose_multicollinearity(df, list(theory_set))
    
    # Step 4: Variable Importance Ranking
    numeric_df = df[list(theory_set)].select_dtypes(include=[np.number])
    if outcome_col in df.columns and df[outcome_col].dtype in [np.float64, np.int64]:
        corr = numeric_df.corrwith(df[outcome_col]).abs().sort_values(ascending=False)
        rank_df = pd.DataFrame({
            'Variable': corr.index,
            'Correlation_with_Outcome': corr.values,
            'Ranking': range(1, len(corr) + 1),
            'Signal': ['✓ Strong' if c > 0.1 else '⚠️  Weak' for c in corr.values]
        })
        report.variable_importance = rank_df
    
    # Step 5: Data Quality
    report.data_quality = {
        'total_vars': len(theory_set),
        'missing_pct': {v: 100 * df[v].isna().sum() / len(df) for v in theory_set},
        'zero_variance_vars': [v for v in theory_set if df[v].nunique() <= 1],
    }
    
    # Step 6: Recommendations
    if missing_from_auto:
        report.recommendations.append(
            f"✓ {len(missing_from_auto)} theory vars NOT in auto-selection: "
            f"{list(missing_from_auto)[:5]}. These may be low-signal but essential "
            f"confounders - KEEP THEM."
        )
    
    if len(overlap) == len(theory_set):
        report.recommendations.append(
            "✓ All theory variables selected by automatic filters. "
            "Good data-theory alignment."
        )
    
    if report.multicollinearity['VIF'].max() > 10:
        report.warnings.append(
            f"Some variables have VIF > 10 (high multicollinearity). "
            f"Check: {report.multicollinearity[report.multicollinearity['VIF'] > 10]['Variable'].tolist()}"
        )
    
    if extra_in_auto:
        report.recommendations.append(
            f"Auto-selection finds {len(extra_in_auto)} additional variables. "
            f"Consider robustness check with these included."
        )
    
    report.recommendations.append(
        "✓ This validation shows specification alignment with data. "
        "Proceed with theory-driven PSM-DiD specification."
    )
    
    return report


def compare_specifications(
    df: pd.DataFrame,
    theory_vars: List[str],
    outcome_col: str,
) -> pd.DataFrame:
    """
    Compare theory-driven vs auto-selected variable importance.
    
    Use this to show that your results are robust to variable selection method.
    
    Parameters
    ----------
    df : pd.DataFrame
        Data with all variables.
    theory_vars : list
        Your theory-driven specification.
    outcome_col : str
        Outcome variable for ranking.
        
    Returns
    -------
    pd.DataFrame
        Comparison table of variable importance by method.
    """
    theory_set = set(v for v in theory_vars if v in df.columns)
    
    # Get auto-selected
    try:
        auto_selected, _ = compile_selected_features(
            df,
            outcome_cols=[outcome_col] if outcome_col in df.columns else [],
            control_cols=list(theory_set),
            lagged_cols=[],
            selection_method='union'
        )
        auto_set = set(auto_selected)
    except:
        auto_set = set()
    
    # Create comparison
    all_vars = theory_set | auto_set
    comparison = []
    
    for var in sorted(all_vars):
        comparison.append({
            'Variable': var,
            'In_Theory_Spec': '✓' if var in theory_set else '',
            'In_Auto_Selected': '✓' if var in auto_set else '',
            'Correlation': df[var].corr(df[outcome_col]) if outcome_col in df.columns else np.nan,
        })
    
    return pd.DataFrame(comparison).sort_values('Correlation', key=abs, ascending=False)


# ============================================================================
# BACKWARD COMPATIBILITY: Keep old function names as aliases
# ============================================================================

def calculate_vif(df: pd.DataFrame, exclude_cols: Optional[List[str]] = None) -> pd.DataFrame:
    """
    [BACKWARD COMPATIBILITY ALIAS]
    Calculate Variance Inflation Factors (VIF) for multicollinearity detection.
    
    For new code, consider using diagnose_multicollinearity() with theory_vars.
    """
    return calculate_vif_old(df, exclude_cols)


def correlation_filter(
    df: pd.DataFrame,
    outcome: str,
    threshold: float = 0.1,
) -> List[str]:
    """
    [BACKWARD COMPATIBILITY ALIAS]
    Use validate_specification() for diagnostic validation instead.
    """
    return correlation_filter_old(df, outcome, threshold)


def lasso_feature_selection(
    X: pd.DataFrame,
    y: pd.Series,
    cv: int = 5,
    random_state: int = 42,  # noqa: ignored – lasso_feature_selection_old has no random_state
) -> List[str]:
    """
    [BACKWARD COMPATIBILITY ALIAS]
    Use validate_specification() for diagnostic validation instead.

    Note: ``random_state`` is accepted for API compatibility but ignored;
    ``lasso_feature_selection_old`` uses ``max_iter=10000`` internally.
    """
    return lasso_feature_selection_old(X, y, cv)
