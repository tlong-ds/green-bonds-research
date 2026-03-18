"""
Pytest configuration and shared fixtures for ASEAN Green Bonds tests.
"""

import pytest
import pandas as pd
import numpy as np


@pytest.fixture
def sample_panel_data():
    """Create a sample panel dataset for testing."""
    n_firms = 10
    n_years = 10
    
    firms = np.repeat(np.arange(1, n_firms + 1), n_years)
    years = np.tile(np.arange(2015, 2025), n_firms)
    
    np.random.seed(42)
    df = pd.DataFrame({
        'ric': firms,
        'Year': years,
        'country': 'Thailand',
        'gic': np.random.choice([1010, 1510, 2010], len(firms)),
        'green_bond_active': np.where((years >= 2020) & (firms <= 5), 1, 0),
        'green_bond_issue': np.where((years == 2020) & (firms <= 5), 1, 0),
        'is_certified': np.random.binomial(1, 0.7, len(firms)),
        'return_on_assets': np.random.normal(0.05, 0.1, len(firms)),
        'Tobin_Q': np.random.uniform(0.5, 3, len(firms)),
        'esg_score': np.random.uniform(20, 80, len(firms)),
        'L1_Firm_Size': np.random.normal(10, 2, len(firms)),
        'L1_Leverage': np.random.uniform(0, 1, len(firms)),
        'L1_Asset_Turnover': np.random.uniform(0.5, 2, len(firms)),
        'L1_Capital_Intensity': np.random.uniform(0, 1, len(firms)),
        'L1_Cash_Ratio': np.random.uniform(0, 1, len(firms)),
        'total_assets': np.random.lognormal(20, 1, len(firms)),
        'total_debt': np.random.lognormal(18, 1, len(firms)),
    })
    
    return df


@pytest.fixture
def sample_time_series():
    """Create sample time series data."""
    n = 250
    dates = pd.date_range('2015-01-01', periods=n, freq='D')
    
    df = pd.DataFrame({
        'date': dates,
        'returns': np.random.normal(0.0005, 0.02, n),
        'stock_price': np.cumprod(1 + np.random.normal(0.0005, 0.02, n)),
    })
    
    df.set_index('date', inplace=True)
    return df


@pytest.fixture
def sample_features():
    """Create sample feature matrix for testing."""
    n = 100
    X = pd.DataFrame({
        'feature_1': np.random.normal(0, 1, n),
        'feature_2': np.random.normal(0, 1, n),
        'feature_3': np.random.normal(0, 1, n),
        'feature_4': np.random.normal(0, 1, n),
        'feature_5': np.random.normal(0, 1, n),
    })
    
    # Create outcome with some features being relevant
    y = X['feature_1'] * 2 + X['feature_2'] * 1.5 + np.random.normal(0, 0.1, n)
    
    return X, pd.Series(y, name='outcome')


@pytest.fixture
def sample_matching_data():
    """Create sample data for PSM testing."""
    n = 200
    
    df = pd.DataFrame({
        'firm_id': np.repeat(np.arange(20), 10),
        'year': np.tile(np.arange(2015, 2025), 20),
        'treatment': np.random.binomial(1, 0.3, n),
        'cov1': np.random.normal(0, 1, n),
        'cov2': np.random.normal(0, 1, n),
        'cov3': np.random.normal(0, 1, n),
        'outcome': np.random.normal(0, 1, n),
    })
    
    return df


# Pytest hooks

def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    for item in items:
        # Add markers based on test path
        if "test_data.py" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        elif "test_analysis.py" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        elif "test_utils.py" in item.nodeid:
            item.add_marker(pytest.mark.unit)
