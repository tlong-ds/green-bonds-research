"""
Data processing and feature engineering for ASEAN Green Bonds research.

Functions for cleaning, merging, and engineering features from raw data.
"""

import pandas as pd
import numpy as np
import yfinance as yf
from typing import Optional, Tuple, List, Any
from scipy.stats.mstats import winsorize
import warnings

# Suppress only specific expected warnings
warnings.filterwarnings('ignore', category=FutureWarning)


def merge_panel_data(
    financial_df: pd.DataFrame,
    esg_df: pd.DataFrame,
    market_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Merge financial, ESG, and market data.
    
    Parameters
    ----------
    financial_df : pd.DataFrame
        Financial panel data with 'ric' and 'Year'.
    esg_df : pd.DataFrame
        ESG data with 'isin' identifier.
    market_df : pd.DataFrame
        Market data mapping 'isin' to 'ric'.
        
    Returns
    -------
    pd.DataFrame
        Merged financial and ESG data.
    """
    # Map RIC to ISIN via market data
    tmp1 = pd.merge(esg_df, market_df, on="isin", how="inner")
    tmp1 = tmp1.drop(
        [col for col in ["name", "org_permid", "company", "country"] 
         if col in tmp1.columns],
        axis=1,
        errors='ignore'
    )
    
    # Merge financial and ESG data
    tmp1["Year"] = tmp1["Year"].astype(int)
    merged = pd.merge(financial_df, tmp1, on=["ric", "Year"], how="left")
    
    # Reset index and remove duplicates
    merged = merged.reset_index(drop=True)
    merged = merged.drop_duplicates(subset=["ric", "Year"])
    
    return merged


def merge_green_bonds(
    panel_df: pd.DataFrame,
    gb_df: pd.DataFrame,
    market_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Merge green bonds issuance data into panel.
    
    Parameters
    ----------
    panel_df : pd.DataFrame
        Panel data with 'ric'.
    gb_df : pd.DataFrame
        Green bonds data with 'org_permid'.
    market_df : pd.DataFrame
        Market data mapping 'org_permid' to 'ric'.
        
    Returns
    -------
    pd.DataFrame
        Panel with green bonds indicators.
    """
    # Map PermID to RIC
    market_subset = market_df[["org_permid", "ric"]].copy()
    market_subset["org_permid_str"] = pd.to_numeric(
        market_subset["org_permid"], errors='coerce'
    )
    market_subset["org_permid_str"] = market_subset["org_permid_str"].apply(
        lambda x: str(int(x)) if pd.notna(x) else np.nan
    )
    
    gb_mapped = pd.merge(
        gb_df, 
        market_subset[["org_permid_str", "ric"]].dropna(),
        left_on="org_permid",
        right_on="org_permid_str",
        how="inner"
    )
    
    # Aggregate green bonds by firm-year
    gb_agg = gb_mapped.groupby(["ric", "Year"], as_index=False).agg(
        green_bond_proceeds=("Proceeds Amount This Market", "sum"),
    )
    
    # Calculate certified proceeds
    gb_agg["certified_proceeds"] = gb_mapped.groupby(
        ["ric", "Year"]
    ).apply(
        lambda x: x[x['is_certified'] == 1]["Proceeds Amount This Market"].sum()
    ).values
    
    gb_agg["green_bond_issue"] = 1
    gb_agg["prop_certified"] = gb_agg["certified_proceeds"] / gb_agg["green_bond_proceeds"]
    gb_agg["is_certified"] = (gb_agg["prop_certified"] >= 0.5).astype(int)
    
    # Merge into panel
    panel_df = pd.merge(
        panel_df, gb_agg, on=["ric", "Year"], how="left"
    )
    
    # Fill missing values (no issuance = 0)
    panel_df["green_bond_issue"] = panel_df["green_bond_issue"].fillna(0)
    panel_df["green_bond_proceeds"] = panel_df["green_bond_proceeds"].fillna(0)
    panel_df["is_certified"] = panel_df["is_certified"].fillna(0)
    
    # Create cumulative green bond dummy (ever issued)
    panel_df = panel_df.sort_values(by=["ric", "Year"])
    panel_df["green_bond_active"] = panel_df.groupby("ric")[
        "green_bond_issue"
    ].cumsum().clip(upper=1)
    
    # Create certified bond dummy (years after certified issuance)
    panel_df["certified_bond_active"] = 0
    for firm in panel_df["ric"].unique():
        firm_mask = panel_df["ric"] == firm
        firm_data = panel_df[firm_mask]
        certified_years = firm_data[firm_data["is_certified"] == 1]["Year"].values
        
        if len(certified_years) > 0:
            first_certified_year = certified_years.min()
            panel_df.loc[
                firm_mask & (panel_df["Year"] >= first_certified_year),
                "certified_bond_active"
            ] = 1
    
    return panel_df


def merge_industry_data(panel_df: pd.DataFrame, series_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge industry classification (GIC codes) into panel.
    
    Parameters
    ----------
    panel_df : pd.DataFrame
        Panel data with 'ric'.
    series_df : pd.DataFrame
        Series data with 'ric' and 'gic'.
        
    Returns
    -------
    pd.DataFrame
        Panel with GIC industry classification.
    """
    return pd.merge(panel_df, series_df, on="ric", how="left")


def filter_asean_firms_and_years(
    df: pd.DataFrame,
    min_year: int = 2015,
    max_year: int = 2024,
) -> pd.DataFrame:
    """
    Filter to ASEAN firms and valid year range.
    
    Parameters
    ----------
    df : pd.DataFrame
        Panel data with 'country' and 'Year'.
    min_year : int, optional
        Minimum year (default: 2015).
    max_year : int, optional
        Maximum year (default: 2024).
        
    Returns
    -------
    pd.DataFrame
        Filtered panel data.
    """
    df = df[df['country'] != 'Other'].copy()
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    df = df[(df['Year'] >= min_year) & (df['Year'] <= max_year)].copy()
    
    return df


def handle_missing_values(
    df: pd.DataFrame,
    firm_col: str = 'ticker',
    forward_fill_cols: Optional[list] = None,
    min_years_per_firm: int = 3,
) -> pd.DataFrame:
    """
    Handle missing values via forward fill and firm filtering.
    
    Parameters
    ----------
    df : pd.DataFrame
        Panel data with firm identifier column.
    firm_col : str, optional
        Name of firm identifier column (default: 'ticker'). Can be 'ric' or 'ticker'.
    forward_fill_cols : list, optional
        Columns to forward fill. If None, uses financial variables.
    min_years_per_firm : int, optional
        Minimum years of data per firm (default: 3).
        
    Returns
    -------
    pd.DataFrame
        Data with missing values handled.
    """
    if forward_fill_cols is None:
        forward_fill_cols = [
            'total_assets', 'total_debt', 'long_term_debt',
            'market_capitalization', 'employees'
        ]
    
    df = df.copy()
    
    # Forward fill financial variables (using pandas 2.0+ compatible syntax)
    for col in forward_fill_cols:
        if col in df.columns:
            df[col] = df.groupby(firm_col)[col].transform(lambda x: x.ffill())
    
    # Drop firms with insufficient data
    firm_years = df.groupby(firm_col).size()
    valid_firms = firm_years[firm_years >= min_years_per_firm].index
    df = df[df[firm_col].isin(valid_firms)].copy()
    
    return df


def convert_currency_to_usd(
    df: pd.DataFrame,
    country_col: str = 'country',
    amount_cols: Optional[list] = None,
) -> pd.DataFrame:
    """
    Convert financial amounts to USD using historical exchange rates.
    
    Parameters
    ----------
    df : pd.DataFrame
        Panel data with 'country' and 'Year'.
    country_col : str, optional
        Name of country column (default: 'country').
    amount_cols : list, optional
        Columns to convert. If None, detects automatically.
        
    Returns
    -------
    pd.DataFrame
        Data with amounts in USD.
        
    Notes
    -----
    - Ratio columns (ROA, ROE, etc.) are not converted
    - Uses average annual exchange rates from yfinance
    """
    if amount_cols is None:
        amount_cols = [
            'total_assets', 'total_debt', 'market_capitalization',
            'capital_expenditures', 'cash', 'net_sales_or_revenues',
            'earnings_bef_interest_tax', 'operating_income'
        ]
    
    # Currency mapping by country
    currency_map = {
        'Vietnam': 'VND', 'Thailand': 'THB', 'Malaysia': 'MYR',
        'Singapore': 'SGD', 'Philippines': 'PHP', 'Indonesia': 'IDR',
    }
    
    df = df.copy()
    
    # Apply exchange rates per country and year
    for country, currency in currency_map.items():
        country_mask = df[country_col] == country
        
        for year in df.loc[country_mask, 'Year'].unique():
            try:
                # Get historical exchange rate
                ticker = f"{currency}=X"
                year_start = f"{int(year)}-01-01"
                year_end = f"{int(year)}-12-31"
                
                rates = yf.download(ticker, start=year_start, end=year_end, progress=False)
                if len(rates) > 0:
                    avg_rate = rates['Close'].mean()
                    
                    # Apply conversion
                    mask = country_mask & (df['Year'] == year)
                    for col in amount_cols:
                        if col in df.columns:
                            df.loc[mask, col] = df.loc[mask, col] / avg_rate
            except Exception as e:
                warnings.warn(f"Failed to convert {currency} for {year}: {e}")
    
    return df


def winsorize_outliers(
    df: pd.DataFrame,
    lower: float = 0.01,
    upper: float = 0.99,
    exclude_cols: Optional[list] = None,
) -> pd.DataFrame:
    """
    Winsorize outliers at specified percentiles.
    
    Parameters
    ----------
    df : pd.DataFrame
        Panel data with numeric columns.
    lower : float, optional
        Lower percentile (default: 0.01 = 1st percentile).
    upper : float, optional
        Upper percentile (default: 0.99 = 99th percentile).
    exclude_cols : list, optional
        Columns to exclude from winsorization.
        
    Returns
    -------
    pd.DataFrame
        Data with outliers winsorized.
        
    Notes
    -----
    Uses scipy.stats.mstats.winsorize with limits parameter.
    limits=(lower_frac, upper_frac) where lower_frac + upper_frac <= 1
    For 1st/99th percentiles, use limits=(0.01, 0.01) not (0.01, 0.99)!
    """
    if exclude_cols is None:
        exclude_cols = [
            'ric', 'country', 'Year', 'gic', 'company',
            'green_bond_issue', 'green_bond_active', 'certified_bond_active'
        ]
    
    df = df.copy()
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    # Convert percentiles to limits for scipy winsorize
    # limits expects (fraction_to_trim_from_bottom, fraction_to_trim_from_top)
    lower_limit = lower
    upper_limit = 1.0 - upper  # Convert 0.99 percentile to 0.01 trim from top
    
    for col in numeric_cols:
        if col in exclude_cols:
            continue
        
        if df[col].notna().sum() > 0:
            # Preserve NaN positions by creating a mask and applying winsorize only to non-NaN values
            mask = df[col].notna()
            # Use proper limits: (trim_from_bottom, trim_from_top)
            winsorized_values = winsorize(df[col][mask], limits=(lower_limit, upper_limit))
            # Convert masked array to regular array to avoid issues
            df.loc[mask, col] = np.asarray(winsorized_values)
    
    return df


def normalize_percentages(df: pd.DataFrame, pct_cols: Optional[list] = None) -> pd.DataFrame:
    """
    Normalize percentage columns from [0-100] to [0-1].
    
    Parameters
    ----------
    df : pd.DataFrame
        Panel data.
    pct_cols : list, optional
        Columns to normalize. If None, detects ROA, ROE, ESG-related.
        
    Returns
    -------
    pd.DataFrame
        Data with percentages normalized to [0-1].
    """
    if pct_cols is None:
        pct_cols = [
            'return_on_assets', 'return_on_equity_total', 'esg_score'
        ]
    
    df = df.copy()
    for col in pct_cols:
        if col in df.columns and (df[col] > 1).any():
            df[col] = df[col] / 100
    
    return df


def create_log_features(
    df: pd.DataFrame,
    cols_to_log: Optional[list] = None,
    prefix: str = "ln_",
) -> pd.DataFrame:
    """
    Create log-transformed features.
    
    Parameters
    ----------
    df : pd.DataFrame
        Panel data.
    cols_to_log : list, optional
        Columns to log-transform. If None, uses size/scale variables.
    prefix : str, optional
        Prefix for new log columns (default: 'ln_').
        
    Returns
    -------
    pd.DataFrame
        Data with log features added.
    """
    if cols_to_log is None:
        cols_to_log = ['total_assets', 'employees', 'net_sales_or_revenues']
    
    df = df.copy()
    
    for col in cols_to_log:
        if col in df.columns:
            # Only log positive values
            df[f"{prefix}{col}"] = np.where(
                df[col] > 0,
                np.log(df[col]),
                np.nan
            )
    
    return df


def encode_categorical_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Encode categorical variables.
    
    Parameters
    ----------
    df : pd.DataFrame
        Panel data.
        
    Returns
    -------
    pd.DataFrame
        Data with encoded categorical features.
    """
    df = df.copy()
    
    # Environmental investment indicator
    if 'environmental_investment' in df.columns:
        df['environmental_investment'] = df['environmental_investment'].map(
            {'Y': 1, 'N': 0}
        )
    
    return df


def create_financial_ratios(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create financial ratio variables from raw metrics.
    
    Parameters
    ----------
    df : pd.DataFrame
        Panel data with raw financial metrics.
        
    Returns
    -------
    pd.DataFrame
        Data with computed financial ratios.
        
    Notes
    -----
    - Firm_Size = ln(total_assets)
    - Leverage = total_debt / total_assets
    - Asset_Turnover = net_sales_or_revenues / total_assets
    - Capital_Intensity = total_assets / net_sales_or_revenues
    - Cash_Ratio = cash / current_liabilities_total
    - Tobin_Q = (Market Capitalization + Total Liabilities) / Total Assets
    """
    df = df.copy()
    
    # Firm Size: log of total assets
    df['Firm_Size'] = np.where(
        (df['total_assets'] > 0) & (df['total_assets'].notna()),
        np.log(df['total_assets']),
        np.nan
    )
    
    # Leverage: total debt / total assets
    df['Leverage'] = np.where(
        (df['total_assets'] > 0) & (df['total_assets'].notna()) & (df['total_debt'].notna()),
        df['total_debt'] / df['total_assets'],
        np.nan
    )
    
    # Asset Turnover: net sales / total assets
    df['Asset_Turnover'] = np.where(
        (df['total_assets'] > 0) & (df['total_assets'].notna()) & (df['net_sales_or_revenues'].notna()),
        df['net_sales_or_revenues'] / df['total_assets'],
        np.nan
    )
    
    # Capital Intensity: total assets / net sales
    df['Capital_Intensity'] = np.where(
        (df['net_sales_or_revenues'] > 0) & (df['net_sales_or_revenues'].notna()) & (df['total_assets'].notna()),
        df['total_assets'] / df['net_sales_or_revenues'],
        np.nan
    )
    
    # Cash Ratio: cash / current liabilities
    df['Cash_Ratio'] = np.where(
        (df['current_liabilities_total'] > 0) & (df['current_liabilities_total'].notna()) & (df['cash'].notna()),
        df['cash'] / df['current_liabilities_total'],
        np.nan
    )

    # Tobin's Q = (Market Value of Equity + Total Liabilities) / Total Assets
    # Preference for market_capitalization, fallback to market_value
    mve_col = 'market_capitalization' if 'market_capitalization' in df.columns else 'market_value'
    
    if mve_col in df.columns and 'total_liabilities' in df.columns and 'total_assets' in df.columns:
        df['Tobin_Q'] = np.where(
            (df['total_assets'] > 0) & (df['total_assets'].notna()) & (df[mve_col].notna()) & (df['total_liabilities'].notna()),
            (df[mve_col] + df['total_liabilities']) / df['total_assets'],
            np.nan
        )
        
        # Explicitly handle extreme outliers for Tobin's Q
        df.loc[df['Tobin_Q'] < 0, 'Tobin_Q'] = np.nan
        df.loc[df['Tobin_Q'] > 10, 'Tobin_Q'] = 10  # Cap at 10
    
    return df


def create_lagged_features(
    df: pd.DataFrame,
    firm_col: str = 'ticker',
    vars_to_lag: Optional[list] = None,
    lags: Optional[list] = None,
) -> pd.DataFrame:
    """
    Create lagged features by firm-year.
    
    Parameters
    ----------
    df : pd.DataFrame
        Panel data with firm identifier and 'Year' columns, sorted by firm and year.
    firm_col : str, optional
        Name of firm identifier column (default: 'ticker'). Can be 'ric' or 'ticker'.
    vars_to_lag : list, optional
        Variables to lag. If None, lags key financial ratios and outcomes.
    lags : list, optional
        Lag periods (default: [1]).
        
    Returns
    -------
    pd.DataFrame
        Data with lagged variables added as L{n}_{var}.
        
    Notes
    -----
    - Lagging is done within firm to avoid cross-firm contamination
    - Lags within the same firm-year sequence are created
    """
    if vars_to_lag is None:
        vars_to_lag = [
            'Firm_Size', 'Leverage', 'Asset_Turnover', 'Capital_Intensity',
            'return_on_assets', 'Tobin_Q', 'esg_score'
        ]
    
    if lags is None:
        lags = [1]
    
    df = df.copy()
    df = df.sort_values(by=[firm_col, 'Year']).reset_index(drop=True)
    
    for var in vars_to_lag:
        if var in df.columns:
            for lag in lags:
                lagged_col = f"L{lag}_{var}"
                df[lagged_col] = df.groupby(firm_col)[var].shift(lag)
    
    return df
