"""
Configuration constants for ASEAN Green Bonds research.

Defines paths, variable names, and analysis parameters.
"""

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DATA_DIR = PROJECT_ROOT / "processed_data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

# Input files
RAW_DATA_FILES = {
    "panel": DATA_DIR / "panel_data.csv",
    "esg": DATA_DIR / "esg_panel_data.csv",
    "green_bonds": DATA_DIR / "green-bonds.csv",
    "market_data": {
        "vietnam": DATA_DIR / "vn-market.csv",
        "thailand": DATA_DIR / "tl-market.csv",
        "malaysia": DATA_DIR / "ml-market.csv",
        "singapore": DATA_DIR / "sing-market.csv",
        "philippines": DATA_DIR / "pp-market.csv",
        "indonesia": DATA_DIR / "indo-market.csv",
        "other": DATA_DIR / "other-market.csv",
    },
    "series_data": DATA_DIR / "series_data.csv",
}

# Output files
PROCESSED_DATA_FILES = {
    "cleaned": PROCESSED_DATA_DIR / "cleaned_panel_data.csv",
    "engineered": PROCESSED_DATA_DIR / "final_engineered_panel_data.csv",
    "selected_features": PROCESSED_DATA_DIR / "selected_features_panel_data.csv",
    "feature_report": PROCESSED_DATA_DIR / "feature_selection_report.csv",
}

# Analysis variables
OUTCOME_VARIABLES = [
    "return_on_assets",
    "Tobin_Q",
    "esg_score",
]

CONTROL_VARIABLES = [
    "L1_Firm_Size",
    "L1_Leverage",
    "L1_Asset_Turnover",
    "L1_Capital_Intensity",
    "L1_Cash_Ratio",  # Added for completeness
]

# PSM features - NOTE: prior_green_bonds removed due to perfect collinearity with issuer_track_record
PSM_FEATURES = [
    "L1_Firm_Size",
    "L1_Leverage",
    "L1_Asset_Turnover",
    "L1_Capital_Intensity",
    "L1_Cash_Ratio",
    # "prior_green_bonds",  # REMOVED: VIF=∞, identical to issuer_track_record
]

LAGGED_VARIABLES = [
    "L1_return_on_assets",
    "L1_Tobin_Q",
    "L1_esg_score",
    "L1_ln_emissions_intensity",
    "L1_ln_carbon_footprint",
    "L1_Cash_Ratio",
    "L1_CapEx_Ratio",
    "L1_Current_Ratio",
    "L1_Asset_Turnover",
    "L1_Operating_Margin",
]

# DiD specification parameters
TIME_PERIODS = {
    "pre_treatment_start": 2015,
    "pre_treatment_end": 2016,
    "treatment_start": 2017,
    "analysis_end": 2024,
}

# Event study parameters
EVENT_STUDY_WINDOW = {
    "lead": 5,  # years before treatment
    "lag": 5,   # years after treatment
}

# PSM parameters
PSM_CALIPER = 0.1  # Default caliper for matching (used when PSM_CALIPER_METHOD='fixed')
PSM_RATIO = 4      # Ratio of controls to treated
PSM_CALIPER_METHOD = "austin"  # 'austin' (0.25*SD), 'logit' (0.2*SD(logit)), or 'fixed'
PSM_CALIPER_MIN = 0.01  # Minimum caliper to prevent over-restriction
PSM_QUALITY_CONFIG = {
    "trim_to_common_support": True,  # Enable trimming by default before matching
    "trimming_method": "crump",  # 'crump' or 'percentile'
    "trimming_alpha": 0.1,  # Trimming threshold
    "min_matched_treated_ratio": 0.7,  # Quality gate for retained treated units
    "max_abs_std_diff": 0.1,  # Standardized mean difference gate
}

# Statistical significance levels
ALPHA_SIG = 0.05     # 5% significance level
ALPHA_MARGINAL = 0.10  # 10% marginal significance

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Data validation thresholds
MIN_OBSERVATIONS = 30  # Minimum observations per group
MAX_OUTLIER_SD = 3     # Outliers beyond 3 SD

# =============================================================================
# NEW CONFIGURATION SECTIONS (Pipeline Enhancements)
# =============================================================================

# Survivorship bias handling
SURVIVORSHIP_CONFIG = {
    "mode": "exclude",  # 'exclude' (drop), 'weight' (IPW), 'ignore' (no handling)
    "recent_years": [2023, 2024, 2025],  # Years to check for firm existence
    "min_recent_observations": 1,  # Min observations in recent years to keep firm
    "existence_col": "total_assets",  # Column to check for non-null as existence proxy
}

# System GMM estimation parameters
GMM_CONFIG = {
    "max_lags": 3,  # Maximum lags for automatic instrument selection
    "collapse_instruments": True,  # Backward-compatible fallback behavior
    "collapse_policy": "auto",  # 'auto', 'always', or 'never'
    "collapse_entity_threshold": 500,  # Auto-collapse only for large panels
    "robust_se": True,  # Use robust standard errors
    "ar_test_order": 2,  # Order for Arellano-Bond AR test (should be insignificant)
    "min_overid_df": 1,  # Minimum overidentification df for valid Sargan/Hansen interpretation
    "require_valid_overid_for_interpretation": True,  # Flag models not ready for causal interpretation
}

# ESG data gap handling (tiered authenticity scoring)
ESG_FALLBACK_CONFIG = {
    "tier1_min_obs": 2,  # Minimum pre/post ESG observations for Tier 1 (full analysis)
    "tier2_min_obs": 1,  # Minimum observations for Tier 2 (partial analysis)
    "tier3_cap_score": 60,  # Maximum authenticity score for Tier 3 (certification only)
    "default_fallback": "tiered",  # 'strict', 'tiered', or 'certification_only'
}
