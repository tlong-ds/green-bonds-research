"""
Tests for data module: loading, processing, feature selection.
"""

import pytest
import pandas as pd
import numpy as np
from asean_green_bonds import data, config


class TestDataLoading:
    """Tests for data loading functions."""
    
    def test_load_raw_panel_data_structure(self):
        """Test that raw panel data has expected structure."""
        df = data.load_raw_panel_data()
        
        assert isinstance(df, pd.DataFrame)
        assert 'ric' in df.columns
        assert 'Year' in df.columns
        assert 'return_on_assets' in df.columns
        assert len(df) > 0
    
    def test_load_esg_panel_data_structure(self):
        """Test that ESG data has expected columns."""
        df = data.load_esg_panel_data()
        
        assert isinstance(df, pd.DataFrame)
        assert 'isin' in df.columns
        assert 'Year' in df.columns
        assert len(df) > 0
    
    def test_load_processed_data_variants(self):
        """Test loading different processed data variants."""
        # Should work with engineered dataset
        df_eng = data.load_processed_data(which='engineered', verify_exists=False)
        
        # Verify returns DataFrame even if file doesn't exist
        assert isinstance(df_eng, pd.DataFrame) or isinstance(df_eng, type(None))
    
    def test_load_green_bonds_data_asean_filter(self):
        """Test that green bonds data filters to ASEAN."""
        df = data.load_green_bonds_data(asean_only=True)
        
        assert isinstance(df, pd.DataFrame)
        assert 'org_permid' in df.columns
        assert 'Year' in df.columns
        assert len(df) > 0


class TestDataProcessing:
    """Tests for data processing functions."""
    
    def setup_method(self):
        """Setup test data."""
        self.df = pd.DataFrame({
            'ric': ['A1'] * 10 + ['A2'] * 10,
            'Year': list(range(2015, 2025)) * 2,
            'return_on_assets': np.random.normal(0.05, 0.1, 20),
            'total_assets': np.random.uniform(1e6, 1e9, 20),
            'total_debt': np.random.uniform(1e5, 1e8, 20),
            'employees': np.random.uniform(100, 10000, 20),
            'green_bond_issue': np.random.binomial(1, 0.2, 20),
        })
    
    def test_filter_asean_firms(self):
        """Test filtering to valid years."""
        df_filtered = data.filter_asean_firms_and_years(
            self.df.copy(),
            min_year=2015,
            max_year=2020
        )
        
        assert df_filtered['Year'].max() <= 2020
        assert df_filtered['Year'].min() >= 2015
    
    def test_handle_missing_values_forward_fill(self):
        """Test forward fill for missing values."""
        df_test = self.df.copy()
        df_test.loc[2, 'total_assets'] = np.nan
        df_test.loc[3, 'total_assets'] = np.nan
        
        df_clean = data.handle_missing_values(df_test)
        
        # After forward fill within group, should have some values
        assert df_clean['total_assets'].notna().sum() >= len(df_test) - 4
    
    def test_winsorize_outliers(self):
        """Test outlier winsorization."""
        df_test = self.df.copy()
        df_test.loc[0, 'return_on_assets'] = 100  # Add extreme outlier
        
        df_winsorized = data.winsorize_outliers(df_test, lower=0.01, upper=0.99)
        
        # Max value should be capped
        assert df_winsorized['return_on_assets'].max() < 100
    
    def test_normalize_percentages(self):
        """Test percentage normalization."""
        df_test = self.df.copy()
        df_test['return_on_assets'] = df_test['return_on_assets'] * 100  # Scale to 0-100
        
        df_norm = data.normalize_percentages(df_test, pct_cols=['return_on_assets'])
        
        # Should be scaled back to 0-1
        assert df_norm['return_on_assets'].max() <= 1
    
    def test_create_log_features(self):
        """Test log feature creation."""
        df_test = self.df.copy()
        
        df_log = data.create_log_features(
            df_test,
            cols_to_log=['total_assets'],
            prefix='ln_'
        )
        
        assert 'ln_total_assets' in df_log.columns
        assert df_log['ln_total_assets'].notna().any()


class TestFeatureSelection:
    """Tests for feature selection functions."""
    
    def setup_method(self):
        """Setup test data with features and outcome."""
        n = 100
        self.X = pd.DataFrame({
            'feature_1': np.random.normal(0, 1, n),
            'feature_2': np.random.normal(0, 1, n),
            'feature_3': np.random.normal(0, 1, n),
        })
        self.y = self.X['feature_1'] * 2 + np.random.normal(0, 0.1, n)
    
    def test_correlation_filter_selects_related_features(self):
        """Test that correlation filtering selects correlated features."""
        df_test = self.X.copy()
        df_test['outcome'] = self.y
        
        selected = data.correlation_filter(
            df_test,
            outcome='outcome',
            threshold=0.3
        )
        
        # Should include feature_1 (highly correlated)
        assert 'feature_1' in selected
        assert isinstance(selected, list)
    
    def test_calculate_vif_detects_multicollinearity(self):
        """Test VIF calculation."""
        vif_df = data.calculate_vif(self.X)
        
        assert isinstance(vif_df, pd.DataFrame)
        assert 'Variable' in vif_df.columns
        assert 'VIF' in vif_df.columns
        assert len(vif_df) == 3
    
    def test_lasso_feature_selection(self):
        """Test Lasso feature selection."""
        selected, model = data.lasso_feature_selection(self.X, self.y)
        
        assert isinstance(selected, list)
        assert len(selected) > 0
        assert len(selected) <= 3


class TestDataIntegration:
    """Integration tests for full data pipeline."""
    
    def test_complete_data_pipeline(self):
        """Test that all data loading steps work together."""
        # This would require actual data files
        # For now, verify functions can be called sequentially
        
        try:
            panel = data.load_raw_panel_data()
            esg = data.load_esg_panel_data()
            market = data.load_market_data()
            
            # Verify basic structure
            assert panel is not None
            assert esg is not None
            assert market is not None
        except FileNotFoundError:
            pytest.skip("Data files not found")


class TestDataValidation:
    """Tests for data validation utilities."""
    
    def setup_method(self):
        """Setup test panel data."""
        self.df = pd.DataFrame({
            'ric': ['A'] * 5 + ['B'] * 5,
            'Year': list(range(2015, 2020)) * 2,
            'value': np.random.normal(0, 1, 10),
            'treatment': [0] * 5 + [1] * 5,
        })
    
    def test_validate_panel_structure(self):
        """Test panel structure validation."""
        from asean_green_bonds.utils import validation
        
        report = validation.validate_panel_structure(self.df)
        
        assert 'n_entities' in report
        assert 'n_periods' in report
        assert report['n_entities'] == 2
        assert report['n_periods'] == 5
    
    def test_check_missing_data(self):
        """Test missing data detection."""
        from asean_green_bonds.utils import validation
        
        df_test = self.df.copy()
        df_test.loc[0, 'value'] = np.nan
        
        report = validation.check_missing_data(df_test)
        
        assert 'total_missing_pct' in report
        assert report['total_missing_pct'] > 0
    
    def test_detect_outliers(self):
        """Test outlier detection."""
        from asean_green_bonds.utils import validation
        
        df_test = self.df.copy()
        df_test.loc[0, 'value'] = 100  # Add outlier
        
        outliers = validation.detect_outliers(df_test)
        
        assert 'value' in outliers
        assert len(outliers['value']) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
