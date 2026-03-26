
def load_financial_data() -> pd.DataFrame:
    """Load combined market data (identifiers)."""
    from asean_green_bonds.config import RAW_DATA_FILES
    market_files = RAW_DATA_FILES["financial_data"]
    dfs = []
    for country, filepath in market_files.items():
        if filepath.exists():
            dfs.append(pd.read_csv(filepath))
    
    if not dfs:
        return pd.DataFrame(columns=["name", "ric", "org_permid", "isin"])
    
    financial_data = pd.concat(dfs, ignore_index=True)
    if "currency" in financial_data.columns:
        financial_data = financial_data.drop("currency", axis=1)
    return financial_data

def load_market_data() -> pd.DataFrame:
    """Load combined market data (identifiers)."""
    from asean_green_bonds.config import RAW_DATA_FILES
    market_files = RAW_DATA_FILES["market_data"]
    dfs = []
    for country, filepath in market_files.items():
        if filepath.exists():
            dfs.append(pd.read_csv(filepath))
    
    if not dfs:
        return pd.DataFrame(columns=["name", "ric", "org_permid", "isin"])
    
    market_data = pd.concat(dfs, ignore_index=True)
    if "currency" in market_data.columns:
        market_data = market_data.drop("currency", axis=1)
    return market_data

def load_static_data() -> pd.DataFrame:
    """Load combined static data (identifiers)."""
    from asean_green_bonds.config import RAW_DATA_FILES
    market_files = RAW_DATA_FILES["static_data"]
    dfs = []
    for country, filepath in market_files.items():
        if filepath.exists():
            dfs.append(pd.read_csv(filepath))
    
    if not dfs:
        return pd.DataFrame(columns=["name", "ric", "org_permid", "isin"])
    
    market_data = pd.concat(dfs, ignore_index=True)
    if "currency" in market_data.columns:
        market_data = market_data.drop("currency", axis=1)
    return market_data
