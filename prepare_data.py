"""
Data loader utilities for ASEAN Green Bonds research.

Functions for loading raw data files and managing data sources.
"""

import os
import pandas as pd
import numpy as np
import re
from pathlib import Path
from typing import Dict, Optional, Tuple, Any, List

COUNTRIES = ["Vietnam", "Thailand", "Malaysia", "Singapore", "Philippines", "Indonesia", "Other"]

# Sheet mappings from Excel source
FINANCIAL_SHEET_NAME = ["Sheet1", "Sheet2", "Sheet3", "Sheet4", "Sheet5", "Sheet6", "Sheet7"]
MARKET_SHEET_NAME = ["Sheet8", "Sheet9", "Sheet10", "Sheet11", "Sheet12", "Sheet13", "Sheet14"]
STATIC_SHEET_NAME = ["Sheet15", "Sheet16", "Sheet17", "Sheet18", "Sheet19", "Sheet20", "Sheet21"]
ESG_SHEET_NAME = ["Sheet22", "Sheet23", "Sheet24", "Sheet25", "Sheet26", "Sheet27", "Sheet28"] # now include governance data as time series
# GOVERNANCE_SHEET_NAME = ["Sheet29", "Sheet30", "Sheet31", "Sheet32", "Sheet33", "Sheet34", "Sheet35"] -- depreciated 

# Financial Fundamentals (Worldscope)
FINANCIAL_ATTRIBUTE_COLUMNS = {
    'TOTAL ASSETS': 'total_assets',
    'CURRENT ASSETS - TOTAL': 'current_assets_total',
    'CAPITAL EXPENDITURES': 'capital_expenditures',
    'RETURN ON ASSETS': 'return_on_assets',
    'RETURN ON EQUITY - TOTAL (%)': 'return_on_equity_total',
    'EMPLOYEES': 'employees',
    'NET CASH FLOW-OPERATING ACTIVS': 'net_cash_flow_operating_actv',
    'TOTAL DEBT': 'total_debt',
    'TOTAL LIABILITIES': 'total_liabilities',
    'CURRENT LIABILITIES-TOTAL': 'current_liabilities_total',
    'OPERATING INCOME': 'operating_income',
    'NET SALES OR REVENUES': 'net_sales_or_revenues',
    'LONG TERM DEBT': 'long_term_debt',
    'MARKET CAPITALIZATION': 'market_capitalization',
    'TOTAL CAPITAL': 'total_capital',
    'EARNINGS BEF INTEREST & TAXES': 'earnings_bef_interest_tax',
    'INTEREST EXPENSE - TOTAL': 'interest_expense_total',
    'CASH': 'cash',
}

# Market & Price Data (Datastream)
MARKET_ATTRIBUTE_COLUMNS = {
    'TOT RETURN IND': 'tri',
    'MARKET VALUE': 'market_value',
    'ASK PRICE': 'ask_price',
    'BID PRICE': 'bid_price',
}

# ESG / Environmental (ASSET4 / Refinitiv ESG)
ESG_ATTRIBUTE_COLUMNS = {
    "ESG Score": "esg_score",
    "Total Energy Consumed": "total_energy_consumed",
    "Renewable Energy Use": "renewable_energy_use",
    "GHG Emissions Scope 1 2 3 Estimated Total To Revenue USD in Million": "emissions_intensity",
    "Scope 1 + 2 GHG Emissions": "scope_1_2_emissions",
    "CO2 Equivalent Emissions": "co2_equivalent_emissions",
    "Environmental Innovation Data Point": "environmental_innovation",
    "Internal Carbon Pricing": "internal_carbon_pricing",
    "Internal Carbon Price per Tonne": "internal_carbon_price_per_tonne",
    "GHG Emissions Scope 1 and 2 and 3 Estimated Total": "estimated_total_carbon_footprint",
    "Value - Emission Reduction/Environmental Expenditures": "environmental_investment",
    "Environmental Pillar Data Point": "environmental_pillar_data",
    "Environmental Pillar Data Point (Emissions/Resource Metric)": "environmental_resource_metric",
    # governance attributes
    "Board Size": "board_size",
    "Board Independence": "board_independence",
    "CEO–Chairman Separation": "ceo_separation", 
    "Board Independence Flag": "board_independence",
    "Independence": "board_independence",
    "CEO–Chairman Separation Flag": "ceo_separation",
    "CEO-Chairman Separation Flag": "ceo_separation",
    "Value - Board Structure/CEO-Chairman Separation": "ceo_separation",
}

# Series / Static Attributes
STATIC_ATTRIBUTE_COLUMNS = {
    "Industry / Sector Classification": "industry_group_code",
    "Date of Incorporation": "founding_year",
    "GIC": "gic",
}

# Combined mapping
ATTRIBUTE_COLUMNS = {
    **FINANCIAL_ATTRIBUTE_COLUMNS,
    **MARKET_ATTRIBUTE_COLUMNS,
    **ESG_ATTRIBUTE_COLUMNS,
    # **GOVERNANCE_ATTRIBUTE_COLUMNS,
    **STATIC_ATTRIBUTE_COLUMNS,
}

WORLDSCOPE_TO_ATTRIBUTE = {
    # Market Data
    "MV": "MARKET VALUE",
    "PA": "ASK PRICE",
    "PB": "BID PRICE",
    "RI": "TOT RETURN IND",
    # Financial Data
    "WC01001": "NET SALES OR REVENUES",
    "WC01075": "INTEREST EXPENSE - TOTAL",
    "WC01250": "OPERATING INCOME",
    "WC02003": "CASH",
    "WC02201": "CURRENT ASSETS - TOTAL",
    "WC02999": "TOTAL ASSETS",
    "WC03101": "CURRENT LIABILITIES-TOTAL",
    "WC03251": "LONG TERM DEBT",
    "WC03255": "TOTAL DEBT",
    "WC03351": "TOTAL LIABILITIES",
    "WC03998": "TOTAL CAPITAL",
    "WC04601": "CAPITAL EXPENDITURES",
    "WC04860": "NET CASH FLOW-OPERATING ACTIVS",
    "WC07011": "EMPLOYEES",
    "WC08001": "MARKET CAPITALIZATION",
    "WC08301": "RETURN ON EQUITY - TOTAL (%)",
    "WC08326": "RETURN ON ASSETS",
    "WC18191": "EARNINGS BEF INTEREST & TAXES",
    # Static / Others
    "WC06010": "Industry / Sector Classification",
    "WC18272": "Date of Incorporation",
    # ESG
    "TRESGS": "ESG Score",
    "ENERDP013": "Total Energy Consumed",
    "ENERDP014": "Renewable Energy Use",
    "ENERDP768": "GHG Emissions Scope 1 2 3 Estimated Total To Revenue USD in Million",
    "ENERO132V": "Scope 1 + 2 GHG Emissions",
    "ENERO24V": "CO2 Equivalent Emissions",
    "ENPIDP023": "Environmental Innovation Data Point",
    # Governance (Binary/Static Flags)
    "CGBSDP060": "Board Size",
    "CGBSDP0012": "Board Independence Flag",
    "CGBSO09V": "CEO–Chairman Separation Flag",
}


def longest_common_suffix(names: List[str]) -> str:
    """Find the longest common suffix among a list of strings."""
    if not names:
        return ""
    reversed_names = [n[::-1] for n in names]
    common = ''
    for chars in zip(*reversed_names):
        if len(set(chars)) == 1:
            common += chars[0]
        else:
            break
    return common[::-1].strip().lstrip('- ').strip()


def load_refinitiv_sheet(file_path: str, sheet_name: str, header: int = 3) -> pd.DataFrame:
    """Load and clean a single sheet from the Refinitiv Excel export."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Source file '{file_path}' not found.")
    
    df = pd.read_excel(file_path, engine="openpyxl", sheet_name=sheet_name, header=header)
    if "Name" in df.columns:
        df = df[df["Name"] != "#ERROR"].copy()
    return df


def prepare_refinitiv_data(file_path: str, output_dir: str = "data"):
    """
    Prepare panel data from raw Refinitiv Excel file.
    
    Implements melting and pivoting logic to create true panel data format.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Remove existing CSVs to prevent double-appending on re-run
    for f in ["panel_data.csv", "esg_panel_data.csv", "static_data.csv", "governance_data.csv", "financial_data.csv", "market_data.csv"]:
        path = os.path.join(output_dir, f)
        if os.path.exists(path):
            os.remove(path)

    print(f"Processing {file_path} into true panel data...")

    # 1. Extract Time Series Data (Financials)
    for sheet_name, country in zip(FINANCIAL_SHEET_NAME, COUNTRIES):
        df = load_refinitiv_sheet(file_path, sheet_name)

        if sheet_name == "Sheet7":
            conditions = [
                df["Code"].str.contains(".BK", na=False),
                df["Code"].str.contains(".HM", na=False),
                df["Code"].str.contains(".KL", na=False),
                df["Code"].str.contains(".SI", na=False),
                df["Code"].str.contains(".PS", na=False),
                df["Code"].str.contains(".JK", na=False),
            ]
            choices = ["Thailand", "Vietnam", "Malaysia", "Singapore", "Philippines", "Indonesia"]
            df['country'] = np.select(conditions, choices, default="Other")
        else:
            df['country'] = country
        
        attr_code = df['Code'].str.extract(r'\((.+)\)$')[0]
        attribute_raw = attr_code.map(WORLDSCOPE_TO_ATTRIBUTE)
        df['ticker'] = df['Code'].str.extract(r'^(.+?)\(')[0]
        df['attribute'] = attribute_raw
        
        # Extract company name by stripping suffix
        suffix_pattern = r'\s*-\s*(?:' + '|'.join(
            [re.escape(k) for k in ATTRIBUTE_COLUMNS.keys()] + 
            [re.escape(k) for k in WORLDSCOPE_TO_ATTRIBUTE.keys()]
        ) + r')\s*$'
        df['company'] = df['Name'].str.replace(suffix_pattern, '', regex=True)

        df['attr_col'] = df['attribute'].map(ATTRIBUTE_COLUMNS)
        df_mapped = df.dropna(subset=['attr_col'])

        year_cols = [c for c in df.columns if str(c).isdigit() and 2015 <= int(c) <= 2025]
        df_long = df_mapped.melt(
            id_vars=['company', 'ticker', 'country', 'attr_col'],
            value_vars=year_cols,
            var_name='Year',
            value_name='value'
        )

        df_wide = df_long.pivot_table(
            index=['company', 'ticker', 'country', 'Year'],
            columns='attr_col',
            values='value',
            aggfunc='first'
        ).reset_index()

        financial_path = os.path.join(output_dir, "financial_data.csv")
        header = not os.path.exists(financial_path)
        df_wide.to_csv(financial_path, index=False, mode='a', header=header)

    # 2. Extract Market Data
    for sheet_name, country in zip(MARKET_SHEET_NAME, COUNTRIES):
        df = load_refinitiv_sheet(file_path, sheet_name)

        if sheet_name == "Sheet14":
            conditions = [
                df["Code"].str.contains(".BK", na=False),
                df["Code"].str.contains(".HM", na=False),
                df["Code"].str.contains(".KL", na=False),
                df["Code"].str.contains(".SI", na=False),
                df["Code"].str.contains(".PS", na=False),
                df["Code"].str.contains(".JK", na=False),
            ]
            choices = ["Thailand", "Vietnam", "Malaysia", "Singapore", "Philippines", "Indonesia"]
            df['country'] = np.select(conditions, choices, default="Other")
        else:
            df['country'] = country
        
        attr_code = df['Code'].str.extract(r'\((.+)\)$')[0]
        attribute_raw = attr_code.map(WORLDSCOPE_TO_ATTRIBUTE)
        df['ticker'] = df['Code'].str.extract(r'^(.+?)\(')[0]
        df['attribute'] = attribute_raw
        
        # Extract company name by stripping suffix
        suffix_pattern = r'\s*-\s*(?:' + '|'.join(
            [re.escape(k) for k in ATTRIBUTE_COLUMNS.keys()] + 
            [re.escape(k) for k in WORLDSCOPE_TO_ATTRIBUTE.keys()]
        ) + r')\s*$'
        df['company'] = df['Name'].str.replace(suffix_pattern, '', regex=True)

        df['attr_col'] = df['attribute'].map(ATTRIBUTE_COLUMNS)
        df_mapped = df.dropna(subset=['attr_col'])

        year_cols = [c for c in df.columns if str(c).isdigit() and 2015 <= int(c) <= 2025]
        df_long = df_mapped.melt(
            id_vars=['company', 'ticker', 'country', 'attr_col'],
            value_vars=year_cols,
            var_name='Year',
            value_name='value'
        )

        df_wide = df_long.pivot_table(
            index=['company', 'ticker', 'country', 'Year'],
            columns='attr_col',
            values='value',
            aggfunc='first'
        ).reset_index()

        market_path = os.path.join(output_dir, "market_data.csv")
        header = not os.path.exists(market_path)
        df_wide.to_csv(market_path, index=False, mode='a', header=header)

    # 3. Extract Static Data (Transposed Layout)
    for sheet_name, country in zip(STATIC_SHEET_NAME, COUNTRIES):
        df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None, engine="openpyxl")
        tickers = df_raw.iloc[1, 1:].tolist()
        attr_codes = df_raw.iloc[2:, 0].tolist()
        
        static_data = []
        for i, ticker in enumerate(tickers):
            if pd.isna(ticker) or str(ticker) == "Date":
                continue
                
            ticker_str = str(ticker)
            country_name = country
            if sheet_name == "Sheet21":
                if ticker_str.endswith(".BK"): country_name = "Thailand"
                elif ticker_str.endswith(".HM"): country_name = "Vietnam"
                elif ticker_str.endswith(".KL"): country_name = "Malaysia"
                elif ticker_str.endswith(".SI"): country_name = "Singapore"
                elif ticker_str.endswith(".PS"): country_name = "Philippines"
                elif ticker_str.endswith(".JK"): country_name = "Indonesia"

            row_data = {
                "ticker": ticker_str,
                "country": country_name,
            }
            
            for j, code in enumerate(attr_codes):
                attr_name = WORLDSCOPE_TO_ATTRIBUTE.get(code)
                if not attr_name: continue
                
                attr_col = ATTRIBUTE_COLUMNS.get(attr_name)
                if not attr_col: continue
                
                val = df_raw.iloc[j + 2, i + 1]
                row_data[attr_col] = val
                
            static_data.append(row_data)
        
        static_path = os.path.join(output_dir, "static_data.csv")
        header = not os.path.exists(static_path)
        pd.DataFrame(static_data).to_csv(static_path, index=False, mode='a', header=header)

    # 4. Extract ESG Data (Time Series Layout)
    esg_frames = []
    for sheet_name, country in zip(ESG_SHEET_NAME, COUNTRIES):
        df = load_refinitiv_sheet(file_path, sheet_name)

        if sheet_name == "Sheet28":
            conditions = [
                df["Code"].str.contains(".BK", na=False),
                df["Code"].str.contains(".HM", na=False),
                df["Code"].str.contains(".KL", na=False),
                df["Code"].str.contains(".SI", na=False),
                df["Code"].str.contains(".PS", na=False),
                df["Code"].str.contains(".JK", na=False),
            ]
            choices = ["Thailand", "Vietnam", "Malaysia", "Singapore", "Philippines", "Indonesia"]
            df['country'] = np.select(conditions, choices, default="Other")
        else:
            df['country'] = country
        
        attr_code = df['Code'].str.extract(r'\((.+)\)$')[0]
        attr_map = df.groupby(attr_code)['Name'].apply(
            lambda g: longest_common_suffix(g.tolist())
        )
        # Prefer code-based mapping when available (governance codes)
        attr_from_code = attr_code.map(WORLDSCOPE_TO_ATTRIBUTE)
        df['attribute'] = attr_from_code.fillna(attr_code.map(attr_map))
        df['ticker'] = df['Code'].str.extract(r'^(.+?)\(')[0]
        df['company'] = df.apply(
            lambda row: row['Name'][:-(len(row['attribute']) + 3)] if pd.notna(row['attribute']) else row['Name'],
            axis=1
        )

        df['attr_col'] = df['attribute'].map(ESG_ATTRIBUTE_COLUMNS)
        df_mapped = df.dropna(subset=['attr_col'])

        year_cols = [c for c in df.columns if str(c).isdigit() and 2015 <= int(c) <= 2025]
        df_long = df_mapped.melt(
            id_vars=['company', 'ticker', 'country', 'attr_col'],
            value_vars=year_cols,
            var_name='Year',
            value_name='value'
        )

        df_wide = df_long.pivot_table(
            index=['company', 'ticker', 'country', 'Year'],
            columns='attr_col',
            values='value',
            aggfunc='first'
        ).reset_index()

        esg_frames.append(df_wide)

    # Write ESG data once to preserve all columns across sheets
    if esg_frames:
        esg_all = pd.concat(esg_frames, ignore_index=True, sort=False)
        esg_path = os.path.join(output_dir, "esg_data.csv")
        esg_all.to_csv(esg_path, index=False)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Prepare Refinitiv data.")
    parser.add_argument("--file", type=str, default="data2603.xlsx", help="Source Excel file")
    args = parser.parse_args()

    file_path = args.file
    if not os.path.exists(file_path):
        alt_path = os.path.join("data", file_path)
        if os.path.exists(alt_path):
            file_path = alt_path
        else:
            print(f"Error: {file_path} not found.")
            return

    prepare_refinitiv_data(file_path)


if __name__ == "__main__":
    main()
