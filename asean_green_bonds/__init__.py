"""
ASEAN Green Bonds Research Package

A comprehensive Python package for analyzing the impact of green bond issuance
on firm performance in ASEAN economies (2015-2024).

Modules:
    data: Data loading, processing, and feature selection
    analysis: Econometric analysis (PSM, DiD, event studies)
    utils: Utility functions for statistics and visualization
    config: Configuration constants

Quick Start:
    >>> from asean_green_bonds.data import load_processed_data
    >>> from asean_green_bonds.analysis import estimate_did
    >>> data = load_processed_data()
    >>> results = estimate_did(data)

Documentation:
    https://asean-green-bonds.readthedocs.io

License:
    MIT

Author:
    ASEAN Green Bonds Research Team
"""

from . import config
from . import data
from . import analysis
from . import utils

__version__ = "0.1.0"
__author__ = "ASEAN Green Bonds Research Team"
__license__ = "MIT"

__all__ = [
    "config",
    "data",
    "analysis",
    "utils",
]
