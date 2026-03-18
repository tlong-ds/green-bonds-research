"""
Utility module: Statistics, visualization, and validation.

Submodules:
    stats: Statistical utilities
    visualization: Plotting functions
    validation: Data validation utilities
"""

from .stats import (
    calculate_effect_size,
    calculate_confidence_interval,
    proportion_test,
    multiple_comparisons_correction,
    calculate_variance_inflation_factors,
    calculate_icc,
    create_summary_statistics,
)

from .visualization import (
    plot_propensity_score_overlap,
    plot_covariate_balance,
    plot_did_results,
    plot_event_study,
    plot_specification_sensitivity,
    plot_parallel_trends,
    plot_summary_statistics,
)

from .validation import (
    validate_panel_structure,
    check_missing_data,
    detect_outliers,
    validate_treatment_variation,
    check_parallel_trends_assumption,
    validate_regression_assumptions,
    generate_data_quality_report,
)

__all__ = [
    # Stats
    "calculate_effect_size",
    "calculate_confidence_interval",
    "proportion_test",
    "multiple_comparisons_correction",
    "calculate_variance_inflation_factors",
    "calculate_icc",
    "create_summary_statistics",
    # Visualization
    "plot_propensity_score_overlap",
    "plot_covariate_balance",
    "plot_did_results",
    "plot_event_study",
    "plot_specification_sensitivity",
    "plot_parallel_trends",
    "plot_summary_statistics",
    # Validation
    "validate_panel_structure",
    "check_missing_data",
    "detect_outliers",
    "validate_treatment_variation",
    "check_parallel_trends_assumption",
    "validate_regression_assumptions",
    "generate_data_quality_report",
]
