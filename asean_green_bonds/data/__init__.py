"""
Data module: Loading, processing, and feature selection.

Submodules:
    loader: Data loading utilities
    processing: Data cleaning and engineering
    feature_selection: Feature selection methods
"""

from .processing import (
    merge_panel_data,
    merge_green_bonds,
    merge_industry_data,
    filter_asean_firms_and_years,
    handle_missing_values,
    convert_currency_to_usd,
    winsorize_outliers,
    normalize_percentages,
    create_log_features,
    encode_categorical_features,
    create_financial_ratios,
    create_lagged_features,
    filter_survived_firms,
    calculate_survivorship_weights,
    prepare_analysis_sample,
)

from .feature_engineering import (
    engineer_psm_attributes,
    merge_psm_into_panel,
    normalize_psm_attributes,
    calculate_tobin_q,
)

from .feature_selection import (
    calculate_vif,
    correlation_filter,
    lasso_feature_selection,
    stepwise_selection,
    compile_selected_features,
    create_feature_selection_report,
    # Diagnostic functions
    diagnose_multicollinearity,
    validate_specification,
    compare_specifications,
    DiagnosticReport,
)

__all__ = [
    # Processing
    "merge_panel_data",
    "merge_green_bonds",
    "merge_industry_data",
    "filter_asean_firms_and_years",
    "handle_missing_values",
    "convert_currency_to_usd",
    "winsorize_outliers",
    "normalize_percentages",
    "create_log_features",
    "encode_categorical_features",
    "create_financial_ratios",
    "create_lagged_features",
    "filter_survived_firms",
    "calculate_survivorship_weights",
    "prepare_analysis_sample",
    # Feature Engineering
    "engineer_psm_attributes",
    "merge_psm_into_panel",
    "normalize_psm_attributes",
    "calculate_tobin_q",
    # Feature Selection
    "calculate_vif",
    "correlation_filter",
    "lasso_feature_selection",
    "stepwise_selection",
    "compile_selected_features",
    "create_feature_selection_report",
    # Diagnostic functions
    "diagnose_multicollinearity",
    "validate_specification",
    "compare_specifications",
    "DiagnosticReport",
]
