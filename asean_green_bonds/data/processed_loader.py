"""Helpers to load processed datasets (engineered/analysis/etc.).

This keeps a small, well-scoped helper separate from the larger loader module.
"""

import pandas as pd
from asean_green_bonds.config import PROCESSED_DATA_FILES


def load_processed_data(which: str = "full_panel") -> pd.DataFrame:
    """Load a processed dataset by key from config.PROCESSED_DATA_FILES.

    Args:
        which: key in PROCESSED_DATA_FILES (e.g., 'engineered', 'cleaned', 'analysis').

    Returns:
        A pandas DataFrame loaded from the CSV file. If the file does not exist,
        returns an empty DataFrame.
    """
    if which not in PROCESSED_DATA_FILES:
        raise ValueError(
            f"Unknown processed data key '{which}'. Valid keys: {list(PROCESSED_DATA_FILES.keys())}"
        )

    filepath = PROCESSED_DATA_FILES[which]
    if not filepath.exists():
        return pd.DataFrame()

    return pd.read_csv(filepath)
