import os
import pandas as pd 
import numpy as np

ATTRIBUTE_COLUMNS = {
    'TOT RETURN IND': 'tri',
    'MARKET VALUE': 'market_value',
    'ASK PRICE': 'ask_price',
    'BID PRICE': 'bid_price',
    'TOTAL CAPITAL': 'total_capital',
    'MARKET CAPITALIZATION': 'market_capitalization',
    'LONG TERM DEBT': 'long_term_debt',
    'NET SALES OR REVENUES': 'net_sales_or_revenues',
    'OPERATING INCOME': 'operating_income',
    'TOTAL ASSETS': 'total_assets',
    'TOTAL LIABILITIES': 'total_liabilities',
    'TOTAL DEBT': 'total_debt',
    'NET CASH FLOW-OPERATING ACTIVS': 'net_cash_flow_operating_actv',
    'RETURN ON EQUITY - TOTAL (%)': 'return_on_equity_total',
    'RETURN ON ASSETS': 'return_on_assets',
    'CAPITAL EXPENDITURES': 'capital_expenditures',
    'EARNINGS BEF INTEREST & TAXES': 'earnings_bef_interest_tax',
    'CASH': 'cash',
    'CURRENT LIABILITIES-TOTAL': 'current_liabilities_total',
    'CURRENT ASSETS - TOTAL': 'current_assets_total',
    'EMPLOYEES': 'employees',
    'INTEREST EXPENSE - TOTAL': 'interest_expense_total',
}

ESG_ATTRIBUTE_COLUMNS = {
    "ESG Score": "esg_score",
    "Internal Carbon Pricing": "internal_carbon_pricing",
    "Internal Carbon Price per Tonne": "internal_carbon_price_per_tonne",
    "GHG Emissions Scope 1 and 2 and 3 Estimated Total": "estimated_total_carbon_footprint",
    "GHG Emissions Scope 1 2 3 Estimated Total To Revenue USD in Million": "emissions_intensity",
    "Value - Emission Reduction/Environmental Expenditures": "environmental_investment",
    # "Environmental Innovation Data Point": "environmental_innovation"
}

WORLDSCOPE_TO_ATTRIBUTE = {
    "MV": "MARKET VALUE",
    "PA": "ASK PRICE",
    "PB": "BID PRICE",
    "RI": "TOT RETURN IND",
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
}

COUNTRIES = ["Vietnam", "Thailand", "Malaysia", "Singapore", "Indonesia", "Philippines", "Other"]
# NOTE: In the Excel file, TS Sheet13 contains Philippines (.PS) and Sheet14 contains Indonesia (.JK).
#       Similarly, Series Sheet20 contains Philippines and Sheet21 contains Indonesia.
#       The sheet order below is swapped (14 before 13, 21 before 20) to align with COUNTRIES.
#       ESG sheets (Sheet1-7) already match COUNTRIES order and need no swap.
TS_SHEET_NAME = ["Sheet9", "Sheet10", "Sheet11", "Sheet12", "Sheet14", "Sheet13", "Sheet15"]
SERIES_SHEET_NAME = ["Sheet16", "Sheet17", "Sheet18", "Sheet19", "Sheet21", "Sheet20", "Sheet22"]
ESG_SHEET_NAME = ["Sheet1", "Sheet2", "Sheet3", "Sheet4", "Sheet5", "Sheet6", "Sheet7"]


DATA_FILE = "data2802.xlsx"

def read_data(sheet_name: str, header: int = 3):
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(
            f"Source file '{DATA_FILE}' not found. "
            f"Place the Refinitiv export in the project root directory."
        )
    df = pd.read_excel(DATA_FILE, engine="openpyxl", sheet_name=sheet_name, header=header)
    if "Name" in df.columns:
        n_before = len(df)
        df = df[df["Name"] != "#ERROR"]
        n_dropped = n_before - len(df)
        if n_dropped > 0:
            print(f"  [{sheet_name}] Dropped {n_dropped} rows with #ERROR in Name column")

    return df

def longest_common_suffix(names):
    reversed_names = [n[::-1] for n in names]
    common = ''
    for chars in zip(*reversed_names):
        if len(set(chars)) == 1:
            common += chars[0]
        else:
            break
    return common[::-1].strip().lstrip('- ').strip()

if __name__ == "__main__":
    # Validate source file exists before any processing
    if not os.path.exists(DATA_FILE):
        print(f"ERROR: '{DATA_FILE}' not found in {os.getcwd()}")
        print("Please place the Refinitiv data export file in the project root.")
        exit(1)

    # Remove existing CSVs to prevent double-appending on re-run
    os.makedirs("data", exist_ok=True)
    for f in ["data/panel_data.csv", "data/esg_panel_data.csv", "data/series_data.csv"]:
        if os.path.exists(f):
            os.remove(f)

    print(f"Processing {DATA_FILE}...")

    # Extract Time Series Data
    for sheet_name, country in zip(TS_SHEET_NAME, COUNTRIES):
        df = read_data(sheet_name)

        if sheet_name == "Sheet15":
            conditions = [
                df["Code"].str.contains(".BK", na=False),
                df["Code"].str.contains(".HM", na=False),
                df["Code"].str.contains(".KL", na=False),
                df["Code"].str.contains(".SI", na=False),
                df["Code"].str.contains(".JK", na=False),
                df["Code"].str.contains(".PS", na=False),
            ]
            choices = ["Thailand", "Vietnam", "Malaysia", "Singapore", "Indonesia", "Philippines"]
            df['country'] = np.select(conditions, choices, default="Other")
        else:
            df['country'] = country
        
        attr_code = df['Code'].str.extract(r'\((.+)\)$')[0]
        # Map WC codes directly to attribute names instead of using
        # longest_common_suffix (which breaks when any company name
        # uses the format "COMPANY - WC02999" instead of "COMPANY - TOTAL ASSETS")
        attribute_raw = attr_code.map(WORLDSCOPE_TO_ATTRIBUTE)
        
        # Extract ticker code (e.g., VIC.HM from VIC.HM(WC02999))
        df['ticker'] = df['Code'].str.extract(r'^(.+?)\(')[0]

        df['attribute'] = attribute_raw
        # Extract company name by stripping the " - ATTRIBUTE" or " - WC_CODE" suffix
        df['company'] = df['Name'].str.replace(r'\s*-\s*(?:' + '|'.join(
            list(ATTRIBUTE_COLUMNS.keys()) + list(WORLDSCOPE_TO_ATTRIBUTE.keys())
        ).replace('(', r'\(').replace(')', r'\)') + r')\s*$', '', regex=True)

        # Step 2: Map attributes and filter to only known ones
        df['attr_col'] = df['attribute'].map(ATTRIBUTE_COLUMNS)
        df_mapped = df.dropna(subset=['attr_col'])

        # Step 3: Melt year columns into long format (years are integers)
        year_cols = list(range(2015, 2026))
        df_long = df_mapped.melt(
            id_vars=['company', 'ticker', 'country', 'attr_col'],
            value_vars=year_cols,
            var_name='Year',
            value_name='value'
        )

        # Step 4: Pivot attributes into columns
        df_wide = df_long.pivot_table(
            index=['company', 'ticker', 'country', 'Year'],
            columns='attr_col',
            values='value',
            aggfunc='first'
        ).reset_index()

        header = not os.path.exists("data/panel_data.csv")
        df_wide.to_csv(f"data/panel_data.csv", index=False, mode='a', header=header)

    # Extract Series Data
    for sheet_name, country in zip(SERIES_SHEET_NAME, COUNTRIES):
        df = read_data(sheet_name, header=1)

        tickers = list(df.columns)[1:]
        
        new_data = []
        for ticker in tickers:
            country = "Other"
            if isinstance(ticker, (float, int)):
                continue

            if ticker.endswith(".BK"):
                country = "Thailand"
            elif ticker.endswith(".HM"):
                country = "Vietnam"
            elif ticker.endswith(".KL"):
                country = "Malaysia"
            elif ticker.endswith(".SI"):
                country = "Singapore"
            elif ticker.endswith(".JK"):
                country = "Indonesia"
            elif ticker.endswith(".PS"):
                country = "Philippines"

            new_data.append({
                "ticker": ticker,
                "country": country,
                "gic": df[ticker].iloc[0]
            })
        
        header = not os.path.exists("data/series_data.csv")
        df_new = pd.DataFrame(new_data)
        df_new.to_csv(f"data/series_data.csv", index=False, mode='a', header=header)

    # Extract ESG Data
    for sheet_name, country in zip(ESG_SHEET_NAME, COUNTRIES):
        df = read_data(sheet_name, header=3)

        if sheet_name == "Sheet7":
            conditions = [
                df["Code"].str.startswith("TH", na=False),
                df["Code"].str.startswith("VN", na=False),
                df["Code"].str.startswith("MY", na=False),
                df["Code"].str.startswith("SG", na=False),
                df["Code"].str.startswith("ID", na=False),
                df["Code"].str.startswith("PH", na=False),
            ]
            choices = ["Thailand", "Vietnam", "Malaysia", "Singapore", "Indonesia", "Philippines"]
            df['country'] = np.select(conditions, choices, default="Other")
        else:
            df['country'] = country
        
        attr_code = df['Code'].str.extract(r'\((.+)\)$')[0]
        attr_map = df.groupby(attr_code)['Name'].apply(
            lambda g: longest_common_suffix(g.tolist())
        )

        attribute_raw = attr_code.map(attr_map)
        
        # Extract ticker code (e.g., VIC.HM from VIC.HM(WC02999))
        df['ticker'] = df['Code'].str.extract(r'^(.+?)\(')[0]

        df['attribute'] = attribute_raw
        df['company'] = df.apply(
            lambda row: row['Name'][:-(len(row['attribute']) + 3)] if pd.notna(row['attribute']) else row['Name'],
            axis=1
        )

        # Step 2: Map attributes and filter to only known ones
        df['attr_col'] = df['attribute'].map(ESG_ATTRIBUTE_COLUMNS)
        df_mapped = df.dropna(subset=['attr_col'])

        # Step 3: Melt year columns into long format (years are integers)
        year_cols = list(range(2015, 2026))
        df_long = df_mapped.melt(
            id_vars=['company', 'ticker', 'country', 'attr_col'],
            value_vars=year_cols,
            var_name='Year',
            value_name='value'
        )

        # Step 4: Pivot attributes into columns
        df_wide = df_long.pivot_table(
            index=['company', 'ticker', 'country', 'Year'],
            columns='attr_col',
            values='value',
            aggfunc='first'
        ).reset_index()

        # Ensure all expected ESG columns are present (some sheets may lack
        # certain attributes, e.g. Vietnam has no "Internal Carbon Price per Tonne")
        all_esg_cols = list(ESG_ATTRIBUTE_COLUMNS.values())
        for col in all_esg_cols:
            if col not in df_wide.columns:
                df_wide[col] = np.nan

        # Strip whitespace from string columns to prevent downstream issues
        # (e.g., environmental_investment values stored as 'Y   ' instead of 'Y')
        for col in df_wide.select_dtypes(include='object').columns:
            df_wide[col] = df_wide[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

        header = not os.path.exists("data/esg_panel_data.csv")
        df_wide.to_csv(f"data/esg_panel_data.csv", index=False, mode='a', header=header)


