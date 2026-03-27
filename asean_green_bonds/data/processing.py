"""
Data processing and feature engineering for ASEAN Green Bonds research.

Functions for cleaning, merging, and engineering features from raw data.
"""

import pandas as pd
import numpy as np
import yfinance as yf
from typing import Optional, Tuple, List, Any, Union
from scipy.stats.mstats import winsorize
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
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
        ESG data with 'ticker' identifier.
    market_df : pd.DataFrame
        Market data (unused in new format, kept for compatibility).
        
    Returns
    -------
    pd.DataFrame
        Merged financial and ESG data.
    """
    # Merge financial and ESG data directly on ticker/ric and Year
    # In the new format, financial_df['ric'] and esg_df['ticker'] are equivalent
    esg_df = esg_df.copy()
    esg_df["Year"] = esg_df["Year"].astype(int)
    
    # Identify common identifier
    fid = 'ric' if 'ric' in financial_df.columns else 'ticker'
    eid = 'ticker' if 'ticker' in esg_df.columns else 'isin'
    
    # Drop redundant columns from ESG before merge
    drop_cols = [col for col in ["company", "country"] if col in esg_df.columns]
    esg_clean = esg_df.drop(drop_cols, axis=1)
    
    merged = pd.merge(financial_df, esg_clean, left_on=[fid, "Year"], right_on=[eid, "Year"], how="left")
    
    # If both columns exist, drop the redundant one
    if fid != eid and fid in merged.columns and eid in merged.columns:
        merged = merged.drop(eid, axis=1)
    
    # Reset index and remove duplicates
    merged = merged.reset_index(drop=True)
    merged = merged.drop_duplicates(subset=[fid, "Year"])
    
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

    if 'Year' in gb_mapped.columns:
        gb_mapped['Year'] = pd.to_numeric(gb_mapped['Year'], errors='coerce')

    cert_col_candidates = [
        'is_certified',
        'is_certified_processed',
        'is_cbi_certified',
        'is_icma_certified',
    ]
    cert_col = next((c for c in cert_col_candidates if c in gb_mapped.columns), None)
    if cert_col is None:
        gb_mapped['_cert_flag'] = 0
        cert_col = '_cert_flag'
    else:
        gb_mapped['_cert_flag'] = pd.to_numeric(gb_mapped[cert_col], errors='coerce').fillna(0).clip(0, 1)
    
    # Aggregate green bonds by firm-year
    gb_agg = gb_mapped.groupby(["ric", "Year"], as_index=False).agg(
        green_bond_proceeds=("Proceeds Amount This Market", "sum"),
    )
    
    # Calculate certified proceeds
    gb_agg["certified_proceeds"] = gb_mapped.groupby(
        ["ric", "Year"]
    ).apply(
        lambda x: x[x['_cert_flag'] == 1]["Proceeds Amount This Market"].sum()
    ).values
    
    gb_agg["green_bond_issue"] = 1
    gb_agg["prop_certified"] = (
        gb_agg["certified_proceeds"] / gb_agg["green_bond_proceeds"].replace({0: np.nan})
    ).fillna(0.0).clip(0.0, 1.0)
    gb_agg["share_certified_proceeds"] = gb_agg["prop_certified"]
    gb_agg["self_labeled_share"] = 1 - gb_agg["share_certified_proceeds"]
    gb_agg["is_certified_majority"] = (gb_agg["prop_certified"] >= 0.5).astype(int)
    gb_agg["has_green_bonds"] = 1
    
    # Merge into panel
    panel_df = pd.merge(
        panel_df, gb_agg, on=["ric", "Year"], how="left"
    )
    
    # Fill missing values (no issuance = 0)
    panel_df["green_bond_issue"] = panel_df["green_bond_issue"].fillna(0)
    panel_df["green_bond_proceeds"] = panel_df["green_bond_proceeds"].fillna(0)
    panel_df["is_certified_majority"] = panel_df["is_certified_majority"].fillna(0)
    panel_df["has_green_bonds"] = panel_df["has_green_bonds"].fillna(0).astype(int)
    panel_df["share_certified_proceeds"] = panel_df["share_certified_proceeds"].fillna(0)
    panel_df["self_labeled_share"] = panel_df["self_labeled_share"].fillna(0)
    
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
        certified_years = firm_data[firm_data["is_certified_majority"] == 1]["Year"].values
        
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
    fx_cache_path: Optional[Union[str, "Path"]] = None,
    allow_fetch: bool = True,
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
    - Uses average annual exchange rates from cache (and yfinance if enabled)
    """
    from pathlib import Path
    from asean_green_bonds import config
    import json
    if amount_cols is None:
        amount_cols = [
            'total_assets', 'total_debt', 'market_capitalization',
            'capital_expenditures', 'cash', 'net_sales_or_revenues',
            'earnings_bef_interest_tax', 'operating_income',
            'current_assets_total', 'current_liabilities_total',
            'total_liabilities', 'total_capital', 'long_term_debt',
            'net_cash_flow_operating_actv',
        ]
    
    # Currency mapping by country
    currency_map = {
        'Vietnam': 'VND', 'Thailand': 'THB', 'Malaysia': 'MYR',
        'Singapore': 'SGD', 'Philippines': 'PHP', 'Indonesia': 'IDR',
    }
    
    # FX cache handling
    if fx_cache_path is None:
        fx_cache_path = config.DATA_DIR / "fx_rates_cache.json"
    fx_cache_path = Path(fx_cache_path) if fx_cache_path is not None else None
    fx_cache = {}
    cache_updated = False
    if fx_cache_path is not None and fx_cache_path.exists():
        try:
            fx_cache = json.load(open(fx_cache_path))
        except Exception as e:
            warnings.warn(f"Failed to read FX cache at {fx_cache_path}: {e}")

    df = df.copy()
    
    # Apply exchange rates per country and year
    missing_fx = set()
    for country, currency in currency_map.items():
        country_mask = df[country_col] == country
        if country_mask.sum() == 0:
            continue
        
        for year in df.loc[country_mask, 'Year'].unique():
            if pd.isna(year):
                continue
            try:
                year_key = str(int(year))
                avg_rate = None
                if fx_cache.get(country) and year_key in fx_cache[country]:
                    avg_rate = fx_cache[country][year_key]
                elif allow_fetch:
                    # Get historical exchange rate
                    ticker = f"{currency}=X"
                    year_start = f"{int(year)}-01-01"
                    year_end = f"{int(year)}-12-31"
                    rates = yf.download(ticker, start=year_start, end=year_end, progress=False)
                    if len(rates) > 0:
                        avg_rate = float(rates['Close'].mean())
                        fx_cache.setdefault(country, {})[year_key] = avg_rate
                        cache_updated = True
                
                if avg_rate is None:
                    warnings.warn(f"Missing FX rate for {country} {year_key}; leaving amounts as-is.")
                    missing_fx.add((country, year_key))
                    continue
                
                # Apply conversion
                mask = country_mask & (df['Year'] == year)
                for col in amount_cols:
                    if col in df.columns:
                        df.loc[mask, col] = df.loc[mask, col] / avg_rate
            except Exception as e:
                warnings.warn(f"Failed to convert {currency} for {year}: {e}")
                missing_fx.add((country, str(int(year)) if not pd.isna(year) else "unknown"))

    if cache_updated and fx_cache_path is not None:
        try:
            fx_cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(fx_cache_path, "w") as f:
                json.dump(fx_cache, f)
        except Exception as e:
            warnings.warn(f"Failed to write FX cache at {fx_cache_path}: {e}")
    if missing_fx:
        missing_list = sorted(missing_fx)
        sample = ", ".join([f"{c}:{y}" for c, y in missing_list[:10]])
        warnings.warn(
            "FX conversion missing for %d country-years (sample: %s). "
            "Amounts for those rows remain in local currency."
            % (len(missing_list), sample)
        )
    
    return df


def winsorize_outliers(
    df: pd.DataFrame,
    lower: float = 0.01,
    upper: float = 0.99,
    exclude_cols: Optional[list] = None,
    include_cols: Optional[list] = None,
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
    include_cols : list, optional
        If provided, only these columns will be winsorized (after exclusions).
        
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
    protected_cols = {
        'ric', 'country', 'Year', 'gic', 'company',
        'has_green_bonds', 'is_certified_majority', 'share_certified_proceeds', 'self_labeled_share',
        'green_bond_issue', 'green_bond_active', 'certified_bond_active',
    }
    if exclude_cols is None:
        exclude_cols = list(protected_cols)
    else:
        exclude_cols = list(set(exclude_cols).union(protected_cols))
    
    df = df.copy()
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if include_cols is not None:
        include_cols = [c for c in include_cols if c in df.columns]
        numeric_cols = [c for c in numeric_cols if c in include_cols]
    
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
        if col not in df.columns:
            continue
        vals = df[col].dropna()
        if len(vals) == 0:
            continue
        median = vals.median()
        q95 = vals.quantile(0.95)
        if (median > 1) or (q95 > 1):
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
            # Only log positive values (avoid evaluating log on non-positive)
            new_col = f"{prefix}{col}"
            df[new_col] = np.nan
            mask = df[col] > 0
            df.loc[mask, new_col] = np.log(df.loc[mask, col])
    
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
    
    # Firm Size: log of total assets (avoid logging non-positive)
    df['Firm_Size'] = np.nan
    mask = (df['total_assets'] > 0) & (df['total_assets'].notna())
    df.loc[mask, 'Firm_Size'] = np.log(df.loc[mask, 'total_assets'])
    
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


def scale_numeric_features(
    df: pd.DataFrame,
    method: str = "robust",
    prefix: str = "z_",
    exclude_cols: Optional[list] = None,
    include_cols: Optional[list] = None,
) -> pd.DataFrame:
    """
    Scale numeric features to improve comparability across magnitudes.

    Parameters
    ----------
    df : pd.DataFrame
        Panel data.
    method : str, optional
        Scaling method: "robust" (median/IQR), "zscore", or "minmax".
    prefix : str, optional
        Prefix for scaled columns (default: "z_").
    exclude_cols : list, optional
        Columns to exclude from scaling.
    include_cols : list, optional
        If provided, only these columns are scaled.
    """
    df = df.copy()
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    default_exclude = {
        "Year", "industry_group_code", "founding_year",
        "green_bond_issue", "green_bond_any", "has_green_bonds",
        "green_bond_active", "certified_bond_active",
        "is_certified_majority", "share_certified_proceeds",
        "self_labeled_share", "has_esg_score",
        "survived_recent", "survivorship_weight",
    }
    if exclude_cols is None:
        exclude_cols = list(default_exclude)
    else:
        exclude_cols = list(set(exclude_cols).union(default_exclude))

    if include_cols is not None:
        numeric_cols = [c for c in numeric_cols if c in include_cols]

    for col in numeric_cols:
        if col in exclude_cols:
            continue
        if col.startswith(prefix):
            continue

        series = df[col]
        vals = series.dropna()
        if len(vals) == 0:
            continue

        # Skip binary columns
        unique_vals = set(vals.unique())
        if unique_vals.issubset({0, 1}):
            continue

        if method == "robust":
            median = vals.median()
            q1 = vals.quantile(0.25)
            q3 = vals.quantile(0.75)
            iqr = q3 - q1
            if iqr == 0 or pd.isna(iqr):
                continue
            scaled = (series - median) / iqr
        elif method == "zscore":
            mean = vals.mean()
            std = vals.std(ddof=0)
            if std == 0 or pd.isna(std):
                continue
            scaled = (series - mean) / std
        elif method == "minmax":
            vmin = vals.min()
            vmax = vals.max()
            if vmin == vmax or pd.isna(vmin) or pd.isna(vmax):
                continue
            scaled = (series - vmin) / (vmax - vmin)
        else:
            raise ValueError(f"Unknown scaling method: {method}")

        df[f"{prefix}{col}"] = scaled

    return df


def filter_survived_firms(
    df: pd.DataFrame,
    firm_col: str = 'ric',
    time_col: str = 'Year',
    recent_years: Optional[List[int]] = None,
    min_recent_observations: int = 1,
    existence_col: str = 'total_assets',
) -> pd.DataFrame:
    """
    Filter panel to firms that exist in recent years (survivorship correction).
    
    This function identifies firms that have data in recent years and filters
    the panel to only include those firms. Useful for ensuring analysis
    focuses on firms that survived to the end of the sample period.
    
    Parameters
    ----------
    df : pd.DataFrame
        Panel data with firm identifier and time columns.
    firm_col : str, optional
        Firm identifier column (default: 'ric').
    time_col : str, optional
        Year column (default: 'Year').
    recent_years : list of int, optional
        Years to check for existence (default: [2023, 2024, 2025]).
    min_recent_observations : int, optional
        Minimum observations in recent years to keep firm (default: 1).
    existence_col : str, optional
        Column to check for non-null values as existence proxy (default: 'total_assets').
        
    Returns
    -------
    pd.DataFrame
        Filtered panel with only firms that survived to recent years.
        
    Examples
    --------
    >>> df_survived = filter_survived_firms(panel_df, recent_years=[2023, 2024])
    """
    if recent_years is None:
        recent_years = [2023, 2024, 2025]
    
    df = df.copy()
    
    # Identify firms with sufficient observations in recent years
    recent_mask = df[time_col].isin(recent_years)
    
    if existence_col in df.columns:
        # Count non-null observations in recent years per firm
        recent_obs = df[recent_mask].groupby(firm_col)[existence_col].apply(
            lambda x: x.notna().sum()
        )
    else:
        # If existence column not present, just count rows
        recent_obs = df[recent_mask].groupby(firm_col).size()
    
    # Filter to firms meeting minimum threshold
    survived_firms = recent_obs[recent_obs >= min_recent_observations].index
    
    return df[df[firm_col].isin(survived_firms)].copy()


def calculate_survivorship_weights(
    df: pd.DataFrame,
    firm_col: str = 'ric',
    time_col: str = 'Year',
    recent_years: Optional[List[int]] = None,
    early_years: Optional[List[int]] = None,
    covariates: Optional[List[str]] = None,
) -> pd.Series:
    """
    Calculate inverse probability weights for survivorship bias correction.
    
    Uses logistic regression to model P(survive to recent years | early characteristics).
    Firms with lower predicted survival probability receive higher weights,
    correcting for potential survivorship bias in the sample.
    
    Parameters
    ----------
    df : pd.DataFrame
        Panel data with firm identifier and time columns.
    firm_col : str, optional
        Firm identifier column (default: 'ric').
    time_col : str, optional
        Year column (default: 'Year').
    recent_years : list of int, optional
        Years defining survival (default: [2023, 2024, 2025]).
    early_years : list of int, optional
        Years for baseline characteristics (default: [2015, 2016, 2017]).
    covariates : list of str, optional
        Variables to use in survival model. If None, uses financial ratios.
        
    Returns
    -------
    pd.Series
        Weights indexed same as input df. Higher weights for firms less likely
        to survive. Weights are normalized to have mean 1.
        
    Notes
    -----
    - Uses inverse probability weighting (IPW) approach
    - Weights are clipped to [0.1, 10] to avoid extreme values
    - Returns weight of 1.0 for observations where weights cannot be computed
    """
    if recent_years is None:
        recent_years = [2023, 2024, 2025]
    if early_years is None:
        early_years = [2015, 2016, 2017]
    if covariates is None:
        covariates = ['total_assets', 'total_debt', 'return_on_assets']
    
    df = df.copy()
    
    # Identify which firms survived to recent years
    recent_mask = df[time_col].isin(recent_years)
    survived_firms = df[recent_mask][firm_col].unique()
    
    # Get early-period characteristics per firm
    early_mask = df[time_col].isin(early_years)
    early_data = df[early_mask].copy()
    
    # Available covariates
    available_covs = [c for c in covariates if c in early_data.columns]
    
    if len(available_covs) == 0:
        warnings.warn("No covariates available for survivorship weighting. Returning unit weights.")
        return pd.Series(1.0, index=df.index)
    
    # Aggregate early characteristics per firm (mean)
    firm_chars = early_data.groupby(firm_col)[available_covs].mean()
    firm_chars = firm_chars.dropna()
    
    if len(firm_chars) < 10:
        warnings.warn("Insufficient firms with early data for survivorship model. Returning unit weights.")
        return pd.Series(1.0, index=df.index)
    
    # Create survival indicator
    firm_chars['survived'] = firm_chars.index.isin(survived_firms).astype(int)
    
    # Fit logistic regression
    X = firm_chars[available_covs].values
    y = firm_chars['survived'].values
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    try:
        model = LogisticRegression(max_iter=1000, solver='lbfgs')
        model.fit(X_scaled, y)
        
        # Predict survival probability
        prob_survive = model.predict_proba(X_scaled)[:, 1]
        
        # Calculate inverse probability weights
        # IPW = 1 / P(survive) for survivors, which upweights firms unlikely to survive
        weights_per_firm = pd.Series(
            1.0 / np.clip(prob_survive, 0.1, 0.99),
            index=firm_chars.index
        )
        
        # Clip extreme weights
        weights_per_firm = weights_per_firm.clip(0.1, 10.0)
        
        # Normalize to mean 1
        weights_per_firm = weights_per_firm / weights_per_firm.mean()
        
    except Exception as e:
        warnings.warn(f"Survivorship model fitting failed: {e}. Returning unit weights.")
        return pd.Series(1.0, index=df.index)
    
    # Map firm weights to all observations
    weights = df[firm_col].map(weights_per_firm)
    weights = weights.fillna(1.0)  # Default weight for firms not in early data
    
    return weights


def normalize_country_name(country: str) -> str:
    """Normalize country names for consistent matching."""
    if pd.isna(country): return ""
    mapping = {
        'Philippines': ['PH', 'PHIL', 'PHILIPPINES', 'PHLIPPINES'],
        'Singapore': ['SG', 'SING', 'SINGAPORE'],
        'Malaysia': ['MY', 'MAL', 'MALAYSIA'],
        'Vietnam': ['VN', 'VIE', 'VIETNAM'],
        'Thailand': ['TH', 'THAI', 'THAILAND'],
        'Indonesia': ['ID', 'IDO', 'INDONESIA'],
    }
    c = str(country).upper().strip()
    for norm, variants in mapping.items():
        if c in [v.upper() for v in variants]: return norm
    return c


def normalize_and_match_issuers(bonds_df: pd.DataFrame, esg_df: pd.DataFrame) -> dict:
    """Create a mapping between bond issuers and ESG panel companies."""
    from ..authenticity import normalize_company_name
    
    esg_df = esg_df.copy()
    esg_df['norm_name'] = esg_df['company'].apply(normalize_company_name)
    esg_df['norm_country'] = esg_df['country'].apply(normalize_country_name)
    
    esg_lookup = {}
    for (name, country), group in esg_df.groupby(['norm_name', 'norm_country']):
        esg_lookup[(name, country)] = group
        
    matches = {}
    for idx, row in bonds_df.iterrows():
        norm_issuer = normalize_company_name(row.get('Issuer/Borrower Name Full', ''))
        norm_country = normalize_country_name(row.get('Issuer/Borrower Nation', ''))
        
        if (norm_issuer, norm_country) in esg_lookup:
            matches[idx] = esg_lookup[(norm_issuer, norm_country)]
            
    return matches


def merge_esg_scores_from_panel(bonds_df: pd.DataFrame, esg_df: pd.DataFrame) -> pd.DataFrame:
    """Merge ESG scores from panel data into bond dataset based on issuance year."""
    result_df = bonds_df.copy()
    matches = normalize_and_match_issuers(bonds_df, esg_df)
    
    for col in ['esg_score_pre', 'esg_score_issue', 'esg_score_post']:
        result_df[col] = np.nan
        
    for idx, esg_data in matches.items():
        date_str = str(result_df.at[idx, 'Dates: Issue Date'])
        year_match = re.search(r'(\d{4})', date_str)
        if not year_match: continue
        year = int(year_match.group(1))
        
        # Get scores for pre, issue, post years
        for offset, col in [(-1, 'esg_score_pre'), (0, 'esg_score_issue'), (1, 'esg_score_post')]:
            val = esg_data[esg_data['Year'] == year + offset]['esg_score']
            if not val.empty: result_df.at[idx, col] = val.iloc[0]
            
    return result_df


def prepare_analysis_sample(
    df: pd.DataFrame,
    survivorship_mode: str = 'ignore',
    firm_col: str = 'ric',
    time_col: str = 'Year',
    recent_years: Optional[List[int]] = None,
    **kwargs
) -> pd.DataFrame:
    """
    Prepare analysis sample with survivorship handling.
    
    Provides a unified interface for applying different survivorship bias
    correction strategies to panel data.
    
    Parameters
    ----------
    df : pd.DataFrame
        Panel data with firm identifier and time columns.
    survivorship_mode : str, optional
        Survivorship handling mode (default: 'ignore'):
        - 'exclude': Remove firms not in recent years
        - 'weight': Keep all firms, add survivorship_weight column
        - 'ignore': No survivorship handling (backward compatible)
    firm_col : str, optional
        Firm identifier column (default: 'ric').
    time_col : str, optional
        Year column (default: 'Year').
    recent_years : list of int, optional
        Years defining survival (default: [2023, 2024, 2025]).
    **kwargs
        Additional arguments passed to filter_survived_firms or
        calculate_survivorship_weights.
        
    Returns
    -------
    pd.DataFrame
        Prepared analysis sample. If mode is 'weight', includes
        'survivorship_weight' column.
        
    Raises
    ------
    ValueError
        If survivorship_mode is not one of 'exclude', 'weight', 'ignore'.
        
    Examples
    --------
    >>> # Backward compatible (no survivorship handling)
    >>> df_analysis = prepare_analysis_sample(panel_df)
    
    >>> # Filter to survived firms only
    >>> df_survived = prepare_analysis_sample(panel_df, survivorship_mode='exclude')
    
    >>> # Add IPW weights for survivorship correction
    >>> df_weighted = prepare_analysis_sample(panel_df, survivorship_mode='weight')
    """
    valid_modes = ['exclude', 'weight', 'ignore']
    if survivorship_mode not in valid_modes:
        raise ValueError(f"survivorship_mode must be one of {valid_modes}, got '{survivorship_mode}'")
    
    if survivorship_mode == 'ignore':
        return df.copy()
    
    # Route mode-specific kwargs to avoid passing unsupported arguments
    exclude_keys = {'min_recent_observations', 'existence_col'}
    weight_keys = {'early_years', 'covariates'}
    kwargs_exclude = {k: v for k, v in kwargs.items() if k in exclude_keys}
    kwargs_weight = {k: v for k, v in kwargs.items() if k in weight_keys}
    
    if survivorship_mode == 'exclude':
        return filter_survived_firms(
            df,
            firm_col=firm_col,
            time_col=time_col,
            recent_years=recent_years,
            **kwargs_exclude
        )
    
    if survivorship_mode == 'weight':
        df = df.copy()
        df['survivorship_weight'] = calculate_survivorship_weights(
            df,
            firm_col=firm_col,
            time_col=time_col,
            recent_years=recent_years,
            **kwargs_weight
        )
        return df


def build_full_panel_data(write_path: Optional["Path"] = None) -> pd.DataFrame:
    """
    Build the full firm-year panel by merging core, ESG, market, static,
    macro, green bond, and CBI data sources.

    Parameters
    ----------
    write_path : Path, optional
        If provided, writes the merged panel to this CSV path.

    Returns
    -------
    pd.DataFrame
        Full merged firm-year panel.
    """
    from pathlib import Path
    from asean_green_bonds import config

    def _first_non_null(series: pd.Series):
        non_null = series.dropna()
        if len(non_null) == 0:
            return np.nan
        return non_null.iloc[0]

    def _country_from_market_filename(path: Path) -> str:
        name = path.name.lower()
        if name.startswith("vn-"):
            return "Vietnam"
        if name.startswith("tl-"):
            return "Thailand"
        if name.startswith("ml-"):
            return "Malaysia"
        if name.startswith("sing-"):
            return "Singapore"
        if name.startswith("pp-"):
            return "Philippines"
        if name.startswith("indo-"):
            return "Indonesia"
        if name.startswith("other-"):
            return "Other"
        return "Other"

    data_dir = config.DATA_DIR

    # Core data
    financial_df = pd.read_csv(config.RAW_DATA_FILES["financial_data"])
    market_df = pd.read_csv(config.RAW_DATA_FILES["market_data"])
    static_df = pd.read_csv(config.RAW_DATA_FILES["static_data"])
    esg_df = pd.read_csv(config.RAW_DATA_FILES["esg_data"])

    # Optional macro data (handle both naming conventions)
    gdp_path = data_dir / "gdp-inflation.csv"
    if not gdp_path.exists():
        gdp_path = data_dir / "gdp_inflation.csv"
    gdp_df = pd.read_csv(gdp_path) if gdp_path.exists() else pd.DataFrame()

    # Green bonds and CBI
    green_bonds_path = data_dir / "green_bonds_authenticated.csv"
    green_bonds_df = pd.read_csv(green_bonds_path) if green_bonds_path.exists() else pd.DataFrame()
    cbi_path = data_dir / "cbi_certified_bonds.csv"
    cbi_df = pd.read_csv(cbi_path) if cbi_path.exists() else pd.DataFrame()

    # ------------------------------------------------------------------
    # Build market mapping table from *-market.csv
    # ------------------------------------------------------------------
    market_files = sorted(Path(data_dir).glob("*-market.csv"))
    market_map_parts = []
    for f in market_files:
        df = pd.read_csv(f)
        df = df.copy()
        df["country"] = _country_from_market_filename(f)
        market_map_parts.append(df)
    market_map = pd.concat(market_map_parts, ignore_index=True) if market_map_parts else pd.DataFrame()

    # Normalize mapping keys
    if not market_map.empty:
        if "isin" in market_map.columns:
            market_map["isin"] = market_map["isin"].astype(str).str.strip()
        if "org_permid" in market_map.columns:
            market_map["org_permid"] = pd.to_numeric(market_map["org_permid"], errors="coerce")
        if "ric" in market_map.columns:
            market_map["ric"] = market_map["ric"].astype(str).str.strip()

    # Base panel: financial data
    panel = financial_df.copy()
    if "ticker" in panel.columns and "ric" not in panel.columns:
        panel = panel.rename(columns={"ticker": "ric"})
    panel["Year"] = pd.to_numeric(panel["Year"], errors="coerce")

    # RIC frequency for ambiguity resolution
    ric_counts = panel["ric"].value_counts(dropna=True)

    # ------------------------------------------------------------------
    # Merge market data (prices)
    # ------------------------------------------------------------------
    market_work = market_df.copy()
    if "ticker" in market_work.columns and "ric" not in market_work.columns:
        market_work = market_work.rename(columns={"ticker": "ric"})
    if "Year" in market_work.columns:
        market_work["Year"] = pd.to_numeric(market_work["Year"], errors="coerce")

    market_cols = [c for c in ["ric", "Year", "ask_price", "bid_price", "market_value", "tri"] if c in market_work.columns]
    market_work = market_work[market_cols]
    if market_work.duplicated(subset=["ric", "Year"]).any():
        num_cols = [c for c in market_work.columns if c not in ["ric", "Year"]]
        market_work = market_work.groupby(["ric", "Year"], as_index=False)[num_cols].mean()

    panel = panel.merge(market_work, on=["ric", "Year"], how="left")

    # ------------------------------------------------------------------
    # Merge static data
    # ------------------------------------------------------------------
    static_work = static_df.copy()
    if "ticker" in static_work.columns and "ric" not in static_work.columns:
        static_work = static_work.rename(columns={"ticker": "ric"})
    static_cols = [c for c in static_work.columns if c in ["ric", "industry_group_code", "founding_year"]]
    static_work = static_work[static_cols].drop_duplicates(subset=["ric"])
    panel = panel.merge(static_work, on="ric", how="left")

    # ------------------------------------------------------------------
    # Merge ESG (ISIN -> RIC via market map)
    # ------------------------------------------------------------------
    esg_work = esg_df.copy()
    if "ticker" in esg_work.columns:
        esg_work = esg_work.rename(columns={"ticker": "isin"})
    esg_work["isin"] = esg_work["isin"].astype(str).str.strip()
    esg_work["Year"] = pd.to_numeric(esg_work["Year"], errors="coerce")

    if not market_map.empty and "isin" in market_map.columns:
        map_esg = market_map[["isin", "country", "ric"]].dropna()
        map_esg["ric_count"] = map_esg["ric"].map(ric_counts).fillna(0)
        map_esg = (
            map_esg.sort_values(["isin", "country", "ric_count", "ric"], ascending=[True, True, False, True])
            .drop_duplicates(subset=["isin", "country"], keep="first")
        )
        esg_work = esg_work.merge(map_esg, on=["isin", "country"], how="left")
        esg_work = esg_work.dropna(subset=["ric"])
        esg_work["ric"] = esg_work["ric"].astype(str)
    else:
        esg_work["ric"] = np.nan

    esg_num_cols = esg_work.select_dtypes(include=[np.number]).columns.tolist()
    esg_group_cols = ["ric", "Year"]
    esg_num_cols = [c for c in esg_num_cols if c not in esg_group_cols]
    esg_cat_cols = [c for c in esg_work.columns if c not in esg_group_cols + esg_num_cols]
    # Avoid overwriting panel's country/identifier columns
    for drop_col in ["country", "isin", "company"]:
        if drop_col in esg_cat_cols:
            esg_cat_cols.remove(drop_col)
    esg_agg_num = esg_work.groupby(esg_group_cols, as_index=False)[esg_num_cols].mean() if esg_num_cols else pd.DataFrame()
    esg_agg_cat = esg_work.groupby(esg_group_cols, as_index=False)[esg_cat_cols].agg(_first_non_null) if esg_cat_cols else pd.DataFrame()

    if not esg_agg_num.empty and not esg_agg_cat.empty:
        esg_agg = esg_agg_num.merge(esg_agg_cat, on=esg_group_cols, how="left")
    else:
        esg_agg = esg_agg_num if not esg_agg_num.empty else esg_agg_cat

    if not esg_agg.empty:
        panel = panel.merge(esg_agg, on=["ric", "Year"], how="left")

    # ------------------------------------------------------------------
    # Merge GDP/Inflation
    # ------------------------------------------------------------------
    if not gdp_df.empty:
        year_cols = [c for c in gdp_df.columns if "[" in c and "YR" in c]
        gdp_long = gdp_df.melt(
            id_vars=["Country Name", "Country Code", "Series Name", "Series Code"],
            value_vars=year_cols,
            var_name="Year",
            value_name="value",
        )
        gdp_long["Year"] = gdp_long["Year"].str.extract(r"(\\d{4})").astype(float).astype("Int64")
        gdp_pivot = gdp_long.pivot_table(
            index=["Country Name", "Year"],
            columns="Series Code",
            values="value",
            aggfunc="first",
        ).reset_index()
        gdp_pivot = gdp_pivot.rename(
            columns={
                "Country Name": "country",
                "NY.GDP.MKTP.KD.ZG": "gdp_growth",
                "FP.CPI.TOTL.ZG": "inflation_cpi",
            }
        )
        panel = panel.merge(gdp_pivot, on=["country", "Year"], how="left")

    # ------------------------------------------------------------------
    # Merge Green Bonds (firm-year aggregates)
    # ------------------------------------------------------------------
    if not green_bonds_df.empty and not market_map.empty:
        gb_work = green_bonds_df.copy()

        # Drop known normalized/derived fields
        normalized_cols = [
            "is_authentic", "esg_improvement", "esg_pvalue", "n_pre_obs", "n_post_obs",
            "data_quality", "icma_confidence", "issuer_nation", "issuer_sector",
            "issuer_type", "issuer_track_record", "has_green_framework", "esg_component",
            "cert_component", "issuer_component", "authenticity_score", "authenticity_category",
            "esg_score_pre_issuance", "esg_score_issuance_year", "esg_score_post_issuance",
            "environmental_investment", "has_esg_data", "esg_data_source",
            "esg_matching_company", "esg_coverage_years", "is_certified",
            "issuer_nation_issuer", "issuer_sector_issuer", "issuer_type_issuer",
            "issuer_track_record_issuer", "has_green_framework_issuer",
        ]
        gb_work = gb_work.drop(columns=[c for c in normalized_cols if c in gb_work.columns], errors="ignore")

        # Issue year
        if "Dates: Issue Date" in gb_work.columns:
            issue_year = pd.to_datetime(gb_work["Dates: Issue Date"], errors="coerce").dt.year
            gb_work["issue_year"] = issue_year

        # Bond-level CBI certification (issuer-year-country, fuzzy optional)
        if not cbi_df.empty:
            from asean_green_bonds.authenticity import merge_cbi_certification
            gb_work = merge_cbi_certification(
                gb_work,
                cbi_df=cbi_df,
                match_rule="issuer_year_country",
                asean_only=True,
                allow_fuzzy=True,
                fuzzy_threshold=90,
                use_proxy_if_missing=False,
            )

        # Map org_permid -> ric
        if "Issuer/Borrower PermID" in gb_work.columns and "org_permid" in market_map.columns:
            gb_work["Issuer/Borrower PermID"] = pd.to_numeric(gb_work["Issuer/Borrower PermID"], errors="coerce")
            map_gb = market_map[["org_permid", "ric"]].dropna()
            map_gb["ric_count"] = map_gb["ric"].map(ric_counts).fillna(0)
            map_gb = (
                map_gb.sort_values(["org_permid", "ric_count", "ric"], ascending=[True, False, True])
                .drop_duplicates(subset=["org_permid"], keep="first")
            )
            gb_work = gb_work.merge(map_gb, left_on="Issuer/Borrower PermID", right_on="org_permid", how="left")
            gb_work = gb_work.dropna(subset=["ric", "issue_year"])

        gb_work["issue_year"] = pd.to_numeric(gb_work["issue_year"], errors="coerce")
        gb_keys = ["ric", "issue_year"]

        sum_cols = [
            "Proceeds Amount This Market",
            "Proceeds Amount Incl Overallotment Sold All Markets",
        ]
        for col in sum_cols:
            if col in gb_work.columns:
                gb_work[col] = pd.to_numeric(gb_work[col], errors="coerce")

        if "is_cbi_certified" in gb_work.columns:
            gb_work["is_cbi_certified"] = (
                pd.to_numeric(gb_work["is_cbi_certified"], errors="coerce")
                .fillna(0)
                .clip(0, 1)
            )
        gb_num_cols = gb_work.select_dtypes(include=[np.number]).columns.tolist()
        gb_num_cols = [c for c in gb_num_cols if c not in gb_keys]
        gb_cat_cols = [c for c in gb_work.columns if c not in gb_keys + gb_num_cols]

        agg_numeric = {}
        for col in gb_num_cols:
            agg_numeric[col] = "sum" if col in sum_cols else "mean"

        gb_agg_num = gb_work.groupby(gb_keys, as_index=False)[gb_num_cols].agg(agg_numeric) if gb_num_cols else pd.DataFrame()
        gb_agg_cat = gb_work.groupby(gb_keys, as_index=False)[gb_cat_cols].agg(_first_non_null) if gb_cat_cols else pd.DataFrame()

        if not gb_agg_num.empty and not gb_agg_cat.empty:
            gb_agg = gb_agg_num.merge(gb_agg_cat, on=gb_keys, how="left")
        else:
            gb_agg = gb_agg_num if not gb_agg_num.empty else gb_agg_cat

        if not gb_agg.empty:
            gb_counts = gb_work.groupby(gb_keys).size().reset_index(name="green_bond_issue_count")
            gb_agg = gb_agg.merge(gb_counts, on=gb_keys, how="left")
            gb_agg["green_bond_issue"] = (gb_agg["green_bond_issue_count"] > 0).astype(int)
            gb_agg["green_bond_any"] = gb_agg["green_bond_issue"]
            gb_agg["has_green_bonds"] = gb_agg["green_bond_issue"]

            # Certified proceeds and shares (bond-level CBI)
            if "is_cbi_certified" in gb_work.columns and "Proceeds Amount This Market" in gb_work.columns:
                cert_proceeds = (
                    gb_work.loc[gb_work["is_cbi_certified"] == 1]
                    .groupby(gb_keys)["Proceeds Amount This Market"]
                    .sum()
                    .reset_index(name="certified_proceeds")
                )
                gb_agg = gb_agg.merge(cert_proceeds, on=gb_keys, how="left")
                gb_agg["certified_proceeds"] = gb_agg["certified_proceeds"].fillna(0)
                gb_agg["share_certified_proceeds"] = (
                    gb_agg["certified_proceeds"]
                    / gb_agg["Proceeds Amount This Market"].replace({0: np.nan})
                ).fillna(0.0).clip(0.0, 1.0)
                gb_agg["self_labeled_share"] = 1 - gb_agg["share_certified_proceeds"]
                gb_agg["is_certified_majority"] = (gb_agg["share_certified_proceeds"] >= 0.5).astype(int)
            gb_agg = gb_agg.rename(columns={"issue_year": "Year"})
            panel = panel.merge(gb_agg, on=["ric", "Year"], how="left")

    # ------------------------------------------------------------------
    # Merge CBI (country-year aggregates)
    # ------------------------------------------------------------------
    if not cbi_df.empty:
        cbi_work = cbi_df.copy()
        if "Issue date" in cbi_work.columns:
            cbi_work["issue_year"] = pd.to_datetime(cbi_work["Issue date"], errors="coerce").dt.year
        cbi_work["issue_year"] = pd.to_numeric(cbi_work["issue_year"], errors="coerce")
        if "Term" in cbi_work.columns:
            cbi_work["term_num"] = pd.to_numeric(cbi_work["Term"], errors="coerce")
        cbi_agg = cbi_work.groupby(["Issuer Country", "issue_year"], as_index=False).agg(
            cbi_bond_count=("Issuer / Applicant", "count"),
            cbi_size_usd_sum=("Size (USD equivalent)", "sum"),
            cbi_term_mean=("term_num", "mean"),
        )
        cbi_agg = cbi_agg.rename(columns={"Issuer Country": "country", "issue_year": "Year"})
        panel = panel.merge(cbi_agg, on=["country", "Year"], how="left")

    # Resolve duplicate firm-year observations (safety net)
    if panel.duplicated(subset=["ric", "Year"]).any():
        group_cols = ["ric", "Year"]
        num_cols = [c for c in panel.select_dtypes(include=[np.number]).columns if c not in group_cols]
        cat_cols = [c for c in panel.columns if c not in group_cols + num_cols]
        agg_num = panel.groupby(group_cols, as_index=False)[num_cols].mean() if num_cols else pd.DataFrame()
        agg_cat = panel.groupby(group_cols, as_index=False)[cat_cols].agg(_first_non_null) if cat_cols else pd.DataFrame()
        if not agg_num.empty and not agg_cat.empty:
            panel = agg_num.merge(agg_cat, on=group_cols, how="left")
        else:
            panel = agg_num if not agg_num.empty else agg_cat

    # Drop merge artifacts
    drop_cols = [c for c in ["ric_count_x", "ric_count_y", "org_permid"] if c in panel.columns]
    if drop_cols:
        panel = panel.drop(columns=drop_cols)

    # Write output if requested
    if write_path is None:
        write_path = config.PROCESSED_DATA_FILES.get("full_panel")
    if write_path is not None:
        Path(write_path).parent.mkdir(parents=True, exist_ok=True)
        panel.to_csv(write_path, index=False)

    return panel


def prepare_full_panel_data(
    write_path: Optional["Path"] = None,
    min_year: Optional[int] = None,
    max_year: Optional[int] = None,
    min_years_per_firm: int = 3,
    fx_cache_path: Optional[Union[str, "Path"]] = None,
    allow_fx_fetch: bool = True,
    survivorship_mode: Optional[str] = None,
    survivorship_kwargs: Optional[dict] = None,
    add_survivorship_flag: bool = True,
    analysis_write_path: Optional["Path"] = None,
) -> pd.DataFrame:
    """
    Build and clean the full firm-year panel with standardized preprocessing.

    Parameters
    ----------
    write_path : Path, optional
        If provided, writes the cleaned panel to this CSV path.
    min_year : int, optional
        Minimum year to keep. Defaults to config.TIME_PERIODS['pre_treatment_start'].
    max_year : int, optional
        Maximum year to keep. Defaults to config.TIME_PERIODS['analysis_end'].
    min_years_per_firm : int, optional
        Minimum years of data per firm.
    fx_cache_path : str or Path, optional
        Path to FX cache JSON file. Defaults to data/fx_rates_cache.json.
    allow_fx_fetch : bool, optional
        Whether to fetch missing FX rates via yfinance.
    survivorship_mode : str, optional
        Survivorship handling mode: 'exclude', 'weight', or 'ignore'. If None,
        uses config.SURVIVORSHIP_CONFIG['mode'].
    survivorship_kwargs : dict, optional
        Additional arguments for survivorship handling (e.g., recent_years,
        min_recent_observations, existence_col, early_years, covariates).
    add_survivorship_flag : bool, optional
        If True, adds a survived_recent flag based on recent-year existence.
    analysis_write_path : Path, optional
        If survivorship_mode != 'ignore', writes the survivorship-adjusted
        analysis panel to this CSV path (defaults to config.PROCESSED_DATA_FILES['analysis']).

    Returns
    -------
    pd.DataFrame
        Cleaned and engineered panel data. If survivorship_mode != 'ignore',
        returns the survivorship-adjusted analysis panel.
    """
    from asean_green_bonds import config

    def _first_non_null(series: pd.Series):
        non_null = series.dropna()
        if len(non_null) == 0:
            return np.nan
        return non_null.iloc[0]

    survivorship_kwargs = {} if survivorship_kwargs is None else dict(survivorship_kwargs)
    if survivorship_mode is None:
        survivorship_mode = config.SURVIVORSHIP_CONFIG.get("mode", "ignore")
    survivorship_config = config.SURVIVORSHIP_CONFIG
    recent_years = survivorship_kwargs.pop(
        "recent_years",
        survivorship_config.get("recent_years", [2023, 2024, 2025]),
    )
    survivorship_kwargs.setdefault(
        "min_recent_observations",
        survivorship_config.get("min_recent_observations", 1),
    )
    survivorship_kwargs.setdefault(
        "existence_col",
        survivorship_config.get("existence_col", "total_assets"),
    )
    min_recent_observations = survivorship_kwargs["min_recent_observations"]
    existence_col = survivorship_kwargs["existence_col"]

    # Build raw merged panel
    panel = build_full_panel_data(write_path=None)

    # Enforce types
    for col in ["ric", "isin", "company", "country"]:
        if col in panel.columns:
            panel[col] = panel[col].astype(str).str.strip()
            panel.loc[panel[col].isin(["nan", "None", ""]), col] = np.nan

    if "Year" in panel.columns:
        panel["Year"] = pd.to_numeric(panel["Year"], errors="coerce")
        panel = panel.dropna(subset=["Year"])
        panel["Year"] = panel["Year"].astype(int)

    # Drop rows without firm identifiers
    if "ric" in panel.columns:
        panel = panel.dropna(subset=["ric"])

    # Resolve duplicate firm-year observations
    if panel.duplicated(subset=["ric", "Year"]).any():
        group_cols = ["ric", "Year"]
        num_cols = [c for c in panel.select_dtypes(include=[np.number]).columns if c not in group_cols]
        cat_cols = [c for c in panel.columns if c not in group_cols + num_cols]
        agg_num = panel.groupby(group_cols, as_index=False)[num_cols].mean() if num_cols else pd.DataFrame()
        agg_cat = panel.groupby(group_cols, as_index=False)[cat_cols].agg(_first_non_null) if cat_cols else pd.DataFrame()
        if not agg_num.empty and not agg_cat.empty:
            panel = agg_num.merge(agg_cat, on=group_cols, how="left")
        else:
            panel = agg_num if not agg_num.empty else agg_cat

    # Filter ASEAN firms and year window
    if min_year is None:
        min_year = config.TIME_PERIODS["pre_treatment_start"]
    if max_year is None:
        max_year = config.TIME_PERIODS["analysis_end"]
    panel = filter_asean_firms_and_years(panel, min_year=min_year, max_year=max_year)

    # Handle missing values
    panel = handle_missing_values(
        panel,
        firm_col="ric",
        forward_fill_cols=[
            "total_assets", "total_debt", "long_term_debt",
            "market_capitalization", "employees"
        ],
        min_years_per_firm=min_years_per_firm,
    )

    # Currency conversion to USD for amount variables
    panel = convert_currency_to_usd(
        panel,
        country_col="country",
        fx_cache_path=fx_cache_path,
        allow_fetch=allow_fx_fetch,
    )

    # Normalize percentages (ROA, ROE, ESG score)
    panel = normalize_percentages(panel)

    # Feature engineering
    panel = create_financial_ratios(panel)
    panel = create_log_features(panel, cols_to_log=["total_assets", "employees", "net_sales_or_revenues"])

    # Winsorize core continuous variables (1st/99th percentile)
    winsor_cols = [
        "return_on_assets", "Tobin_Q", "Leverage",
        "Asset_Turnover", "Cash_Ratio", "Capital_Intensity",
    ]
    panel = winsorize_outliers(panel, include_cols=winsor_cols)

    # Lagged controls/outcomes
    panel = create_lagged_features(
        panel,
        firm_col="ric",
        vars_to_lag=[
            "Firm_Size", "Leverage", "Asset_Turnover", "Cash_Ratio",
            "Capital_Intensity", "return_on_assets", "Tobin_Q", "esg_score",
        ],
        lags=[1],
    )

    # Survivorship flag based on recent-year existence
    if add_survivorship_flag and "ric" in panel.columns and "Year" in panel.columns:
        recent_mask = panel["Year"].isin(recent_years) if recent_years is not None else pd.Series(False, index=panel.index)
        if existence_col in panel.columns:
            recent_obs = panel[recent_mask].groupby("ric")[existence_col].apply(lambda x: x.notna().sum())
        else:
            recent_obs = panel[recent_mask].groupby("ric").size()
        survived_firms = recent_obs[recent_obs >= min_recent_observations].index
        panel["survived_recent"] = panel["ric"].isin(survived_firms).astype(int)

    # Scale numeric features for econometric comparability
    panel = scale_numeric_features(panel, method="robust", prefix="z_")

    # Encode categorical features
    panel = encode_categorical_features(panel)

    # ESG coverage flags
    if "esg_score" in panel.columns:
        panel["has_esg_score"] = panel["esg_score"].notna().astype(int)
        panel["esg_years_covered"] = panel.groupby("ric")["has_esg_score"].transform("sum")

    # Ensure treatment dummies are integers
    # Backward compatibility: if green_bond_issue missing but green_bond_any exists
    if "green_bond_issue" not in panel.columns and "green_bond_any" in panel.columns:
        panel["green_bond_issue"] = panel["green_bond_any"]
    if "has_green_bonds" not in panel.columns and "green_bond_issue" in panel.columns:
        panel["has_green_bonds"] = panel["green_bond_issue"]

    for col in ["green_bond_any", "green_bond_active", "certified_bond_active", "green_bond_issue", "has_green_bonds"]:
        if col in panel.columns:
            panel[col] = panel[col].fillna(0).astype(int)

    # Create cumulative green bond dummy (ever issued)
    if "green_bond_issue" in panel.columns and "green_bond_active" not in panel.columns:
        panel = panel.sort_values(by=["ric", "Year"])
        panel["green_bond_active"] = panel.groupby("ric")["green_bond_issue"].cumsum().clip(upper=1)

    # Create certified bond dummy (years after certified issuance)
    if "is_certified_majority" in panel.columns and "certified_bond_active" not in panel.columns:
        panel = panel.sort_values(by=["ric", "Year"])
        panel["certified_bond_active"] = (panel.groupby("ric")["is_certified_majority"].cumsum() > 0).astype(int)

    panel = panel.sort_values(by=["ric", "Year"]).reset_index(drop=True)

    # Optional survivorship handling for analysis sample
    analysis_panel = panel
    if survivorship_mode != "ignore":
        analysis_panel = prepare_analysis_sample(
            panel,
            survivorship_mode=survivorship_mode,
            firm_col="ric",
            time_col="Year",
            recent_years=recent_years,
            **survivorship_kwargs,
        )

    # Write output if requested
    if write_path is None:
        write_path = config.PROCESSED_DATA_FILES.get("cleaned")
    if write_path is not None:
        from pathlib import Path
        Path(write_path).parent.mkdir(parents=True, exist_ok=True)
        panel.to_csv(write_path, index=False)

    if survivorship_mode != "ignore":
        if analysis_write_path is None:
            analysis_write_path = config.PROCESSED_DATA_FILES.get("analysis")
        if analysis_write_path is not None:
            from pathlib import Path
            Path(analysis_write_path).parent.mkdir(parents=True, exist_ok=True)
            analysis_panel.to_csv(analysis_write_path, index=False)

    return analysis_panel
