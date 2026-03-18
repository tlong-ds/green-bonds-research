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
PSM_CALIPER = 0.1  # Default caliper for matching
PSM_RATIO = 4      # Ratio of controls to treated

# Statistical significance levels
ALPHA_SIG = 0.05     # 5% significance level
ALPHA_MARGINAL = 0.10  # 10% marginal significance

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Data validation thresholds
MIN_OBSERVATIONS = 30  # Minimum observations per group
MAX_OUTLIER_SD = 3     # Outliers beyond 3 SD
