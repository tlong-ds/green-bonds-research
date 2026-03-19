"""
Data loader utilities for ASEAN Green Bonds research.

Functions for loading raw data files and managing data sources.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple, Any

from ..config import RAW_DATA_FILES, PROCESSED_DATA_FILES


def load_raw_panel_data() -> pd.DataFrame:
    """
    Load and merge raw panel data.
    
    Returns
    -------
    pd.DataFrame
        Merged financial panel data with 'ric' and 'Year' columns.
        
    Raises
    ------
    FileNotFoundError
        If data files are not found.
    """
    panel_file = RAW_DATA_FILES["panel"]
    if not panel_file.exists():
        raise FileNotFoundError(f"Panel data not found: {panel_file}")
    
    df = pd.read_csv(panel_file)
    
    # Drop extra header rows
    df = df[df["Year"] != "Year"]
    
    # Convert Year to integer
    df["Year"] = df["Year"].astype(int)
    
    # Standardize column names
    df.columns = [
        'company', 'ric', 'country', 'Year', 'ask_price', 'bid_price',
        'capital_expenditures', 'cash', 'current_assets_total',
        'current_liabilities_total', 'earnings_bef_interest_tax', 'employees',
        'interest_expense_total', 'long_term_debt', 'market_capitalization',
        'market_value', 'net_cash_flow_operating_actv', 'net_sales_or_revenues',
        'operating_income', 'return_on_assets', 'return_on_equity_total',
        'total_assets', 'total_capital', 'total_debt', 'total_liabilities', 'tri'
    ]
    
    return df


def load_esg_panel_data() -> pd.DataFrame:
    """
    Load ESG panel data.
    
    Returns
    -------
    pd.DataFrame
        ESG variables panel with 'isin' identifier.
    """
    esg_file = RAW_DATA_FILES["esg"]
    if not esg_file.exists():
        raise FileNotFoundError(f"ESG data not found: {esg_file}")
    
    df = pd.read_csv(esg_file)
    
    # Drop extra header rows
    df = df[df["Year"] != "Year"]
    
    # Rename ticker to isin for consistency
    df = df.rename(columns={"ticker": "isin"})
    
    # Convert Year to integer
    df["Year"] = df["Year"].astype(int)
    
    return df


def load_market_data() -> pd.DataFrame:
    """
    Load and combine market data from all ASEAN countries.
    
    Returns
    -------
    pd.DataFrame
        Combined market data with 'ric' and 'isin' identifiers.
    """
    market_files = RAW_DATA_FILES["market_data"]
    
    # Load country-specific files
    dfs = []
    for country, filepath in market_files.items():
        if country == "other":
            continue  # Handle separately
        if filepath.exists():
            df = pd.read_csv(filepath)
            dfs.append(df)
    
    market_data = pd.concat(dfs, ignore_index=True)
    
    # Drop redundant currency column
    if "currency" in market_data.columns:
        market_data = market_data.drop("currency", axis=1)
    
    # Load and append "other" markets
    other_file = market_files["other"]
    if other_file.exists():
        other_data = pd.read_csv(other_file)
        other_data = other_data.reindex(columns=["name", "ric", "org_permid", "isin"])
        market_data = pd.concat([market_data, other_data], ignore_index=True)
    
    return market_data


def load_green_bonds_data(asean_only: bool = True) -> pd.DataFrame:
    """
    Load green bonds issuance data.
    
    Parameters
    ----------
    asean_only : bool, optional
        If True, filter to ASEAN issuers only (default: True).
        
    Returns
    -------
    pd.DataFrame
        Green bonds data with 'org_permid', 'Year', proceeds, and certification indicator.
    """
    gb_file = RAW_DATA_FILES["green_bonds"]
    if not gb_file.exists():
        raise FileNotFoundError(f"Green bonds data not found: {gb_file}")
    
    gb = pd.read_csv(gb_file)
    
    if asean_only:
        # Filter to ASEAN countries
        asean_countries = {
            "Brunei", "Cambodia", "Indonesia", "Laos", "Malaysia",
            "Myanmar", "Philippines", "Singapore", "Thailand", "Vietnam", "Viet Nam"
        }
        gb = gb[gb["Issuer/Borrower Nation"].isin(asean_countries)].copy()
    
    # Extract issue year
    gb["Year"] = pd.to_datetime(gb["Dates: Issue Date"]).dt.year
    
    # Create certification indicator
    # Green bonds labeled "Green Bond Purposes" are CBI-certified
    gb['is_certified'] = gb['Primary Use Of Proceeds'].eq('Green Bond Purposes').astype(int)
    
    # Keep necessary columns
    gb = gb[
        ["Issuer/Borrower PermID", "Year", "Proceeds Amount This Market", "is_certified"]
    ].rename(columns={"Issuer/Borrower PermID": "org_permid"})
    
    # Standardize org_permid to string
    gb["org_permid"] = gb["org_permid"].apply(
        lambda x: str(int(x)) if pd.notna(x) else np.nan
    )
    
    return gb


def load_series_data() -> pd.DataFrame:
    """
    Load industry classification (GIC codes) data.
    
    Returns
    -------
    pd.DataFrame
        Series data with 'ric' and 'gic' columns.
    """
    series_file = RAW_DATA_FILES["series_data"]
    if not series_file.exists():
        raise FileNotFoundError(f"Series data not found: {series_file}")
    
    df = pd.read_csv(series_file)
    
    # Keep only ticker and GIC
    df = df[['ticker', 'gic']]
    
    # Rename ticker to ric
    df = df.rename(columns={'ticker': 'ric'})
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['ric'])
    
    return df


def load_processed_data(
    which: str = "engineered",
    verify_exists: bool = True
) -> pd.DataFrame:
    """
    Load pre-processed data from the pipeline.
    
    Parameters
    ----------
    which : str, optional
        Which processed dataset to load:
        - 'cleaned': After data cleaning
        - 'engineered': After feature engineering (default)
        - 'selected_features': After feature selection
        
    verify_exists : bool, optional
        If True, raise error if file doesn't exist (default: True).
        
    Returns
    -------
    pd.DataFrame
        Processed data ready for analysis.
        
    Raises
    ------
    ValueError
        If 'which' is not a valid option.
    FileNotFoundError
        If verify_exists=True and file not found.
    """
    valid_options = {"cleaned", "engineered", "selected_features"}
    if which not in valid_options:
        raise ValueError(f"which must be one of {valid_options}, got '{which}'")
    
    filepath = PROCESSED_DATA_FILES.get(which)
    
    if filepath is None:
        raise ValueError(f"No filepath configured for '{which}'")
    
    if verify_exists and not filepath.exists():
        raise FileNotFoundError(
            f"Processed data file not found: {filepath}\n"
            f"Run data processing pipeline first."
        )
    
    return pd.read_csv(filepath)


def get_data_info() -> Dict[str, Any]:
    """
    Get information about available data files.
    
    Returns
    -------
    dict
        Information about data file locations and status.
    """
    info = {
        "raw_data": {},
        "processed_data": {},
    }
    
    # Check raw data files
    for key, path in RAW_DATA_FILES.items():
        if isinstance(path, dict):
            info["raw_data"][key] = {
                subkey: str(subpath) for subkey, subpath in path.items()
            }
        else:
            info["raw_data"][key] = {
                "path": str(path),
                "exists": path.exists() if isinstance(path, Path) else False,
            }
    
    # Check processed data files
    for key, path in PROCESSED_DATA_FILES.items():
        info["processed_data"][key] = {
            "path": str(path),
            "exists": path.exists(),
        }
    
    return info
