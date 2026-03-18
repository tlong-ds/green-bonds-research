"""
Analysis module: Econometric methods and diagnostics.

Submodules:
    propensity_score: Propensity score matching
    difference_in_diff: Difference-in-differences estimation
    event_study: Event study analysis
    diagnostics: Assumption testing and robustness checks
"""

from .propensity_score import (
    estimate_propensity_scores,
    check_common_support,
    nearest_neighbor_matching,
    assess_balance,
    create_matched_dataset,
)

from .difference_in_diff import (
    prepare_panel_for_regression,
    estimate_did,
    run_multiple_outcomes,
    calculate_moulton_factor,
    parallel_trends_test,
)

from .event_study import (
    calculate_abnormal_returns,
    calculate_cumulative_abnormal_returns,
    analyze_market_reaction_by_firm,
    test_event_significance,
    run_event_study_analysis,
)

from .diagnostics import (
    placebo_test,
    leave_one_out_cv,
    specification_sensitivity,
    heterogeneous_effects_analysis,
    run_diagnostics_battery,
)

__all__ = [
    # Propensity Score
    "estimate_propensity_scores",
    "check_common_support",
    "nearest_neighbor_matching",
    "assess_balance",
    "create_matched_dataset",
    # DiD
    "prepare_panel_for_regression",
    "estimate_did",
    "run_multiple_outcomes",
    "calculate_moulton_factor",
    "parallel_trends_test",
    # Event Study
    "calculate_abnormal_returns",
    "calculate_cumulative_abnormal_returns",
    "analyze_market_reaction_by_firm",
    "test_event_significance",
    "run_event_study_analysis",
    # Diagnostics
    "placebo_test",
    "leave_one_out_cv",
    "specification_sensitivity",
    "heterogeneous_effects_analysis",
    "run_diagnostics_battery",
]
