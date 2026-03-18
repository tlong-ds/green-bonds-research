"""
Tests for analysis module: PSM, DiD, event studies, diagnostics.
"""

import pytest
import pandas as pd
import numpy as np
from asean_green_bonds import analysis


class TestPropensityScore:
    """Tests for propensity score matching."""
    
    def setup_method(self):
        """Setup test data with treatment and covariates."""
        n = 200
        self.df = pd.DataFrame({
            'ric': np.repeat(np.arange(20), 10),
            'Year': np.tile(np.arange(2015, 2025), 20),
            'treatment': np.random.binomial(1, 0.3, n),
            'L1_Firm_Size': np.random.normal(10, 2, n),
            'L1_Leverage': np.random.uniform(0, 1, n),
            'L1_Asset_Turnover': np.random.uniform(0, 3, n),
            'L1_Capital_Intensity': np.random.uniform(0, 2, n),
            'L1_Cash_Ratio': np.random.uniform(0, 1, n),
        })
    
    def test_estimate_propensity_scores(self):
        """Test propensity score estimation."""
        ps = analysis.estimate_propensity_scores(
            self.df,
            treatment_col='treatment'
        )
        
        assert len(ps) == len(self.df)
        assert ps.min() >= 0 and ps.max() <= 1
        assert ps.notna().sum() > 0
    
    def test_check_common_support(self):
        """Test common support verification."""
        self.df['propensity_score'] = analysis.estimate_propensity_scores(
            self.df, treatment_col='treatment'
        )
        
        report = analysis.check_common_support(
            self.df,
            ps_col='propensity_score',
            treatment_col='treatment'
        )
        
        assert 'treated_mean_ps' in report
        assert 'control_mean_ps' in report
        assert 'overlap_region' in report
        assert report['treated_count'] > 0
        assert report['control_count'] > 0
    
    def test_nearest_neighbor_matching(self):
        """Test nearest neighbor matching."""
        self.df['propensity_score'] = analysis.estimate_propensity_scores(
            self.df, treatment_col='treatment'
        )
        
        matched_df, stats = analysis.nearest_neighbor_matching(
            self.df,
            ps_col='propensity_score',
            treatment_col='treatment',
            caliper=0.2,
            ratio=1
        )
        
        assert len(matched_df) <= len(self.df)
        assert 'matched_treated' in stats
        assert 'matched_controls' in stats
    
    def test_assess_balance(self):
        """Test covariate balance assessment."""
        features = ['L1_Firm_Size', 'L1_Leverage', 'L1_Asset_Turnover']
        
        balance = analysis.assess_balance(
            self.df,
            features=features,
            treatment_col='treatment'
        )
        
        assert isinstance(balance, pd.DataFrame)
        assert len(balance) == len(features)
        assert 'Std_Difference' in balance.columns


class TestDifferenceInDifferences:
    """Tests for DiD estimation."""
    
    def setup_method(self):
        """Setup test panel data."""
        n_firms = 10
        n_years = 10
        
        # Create panel structure
        firms = np.repeat(np.arange(1, n_firms + 1), n_years)
        years = np.tile(np.arange(2015, 2025), n_firms)
        
        # Generate outcome variable with treatment effect
        np.random.seed(42)
        treatment = np.where(
            (years >= 2020) & (firms <= 5), 1, 0
        )
        outcome = 0.1 * treatment + np.random.normal(0, 0.1, len(firms))
        
        self.df = pd.DataFrame({
            'ric': firms,
            'Year': years,
            'green_bond_active': treatment,
            'outcome': outcome,
            'L1_Firm_Size': np.random.normal(10, 2, len(firms)),
            'L1_Leverage': np.random.uniform(0, 1, len(firms)),
            'L1_Asset_Turnover': np.random.uniform(0.5, 2, len(firms)),
            'L1_Capital_Intensity': np.random.uniform(0, 1, len(firms)),
        })
    
    def test_prepare_panel_for_regression(self):
        """Test panel preparation."""
        df_reg = analysis.prepare_panel_for_regression(self.df)
        
        assert df_reg.index.names == ['ric', 'Year']
        assert len(df_reg) == len(self.df)
    
    def test_estimate_did_entity_fe(self):
        """Test DiD with entity fixed effects."""
        result = analysis.estimate_did(
            self.df,
            outcome='outcome',
            treatment_col='green_bond_active',
            specification='entity_fe'
        )
        
        assert 'coefficient' in result
        assert 'std_error' in result
        assert 'p_value' in result
        assert result['n_obs'] > 0
    
    def test_estimate_did_time_fe(self):
        """Test DiD with time fixed effects."""
        result = analysis.estimate_did(
            self.df,
            outcome='outcome',
            treatment_col='green_bond_active',
            specification='time_fe'
        )
        
        assert 'coefficient' in result
        assert not pd.isna(result.get('coefficient'))
    
    def test_run_multiple_outcomes(self):
        """Test batch DiD estimation."""
        self.df['outcome_2'] = np.random.normal(0, 1, len(self.df))
        
        results = analysis.run_multiple_outcomes(
            self.df,
            outcomes=['outcome', 'outcome_2'],
            treatment_col='green_bond_active',
            specifications=['entity_fe', 'time_fe']
        )
        
        assert isinstance(results, pd.DataFrame)
        assert len(results) >= 2
    
    def test_calculate_moulton_factor(self):
        """Test Moulton factor calculation."""
        factor = analysis.calculate_moulton_factor(
            self.df,
            outcome='outcome',
            treatment_col='green_bond_active'
        )
        
        assert isinstance(factor, float)
        assert factor >= 1.0  # Should be at least 1 (no inflation)


class TestEventStudy:
    """Tests for event study analysis."""
    
    def setup_method(self):
        """Setup test time series data."""
        n = 250
        dates = pd.date_range('2015-01-01', periods=n, freq='D')
        
        self.ts_df = pd.DataFrame({
            'date': dates,
            'returns': np.random.normal(0.0005, 0.02, n),
            'event': 0,
        })
        
        # Add event on day 100 and 200
        self.ts_df.loc[100, 'event'] = 1
        self.ts_df.loc[200, 'event'] = 1
        self.ts_df.set_index('date', inplace=True)
    
    def test_calculate_abnormal_returns(self):
        """Test abnormal return calculation."""
        ar, stats = analysis.calculate_abnormal_returns(
            self.ts_df,
            event_date_col='event',
            return_col='returns',
            window_start=-5,
            window_end=5
        )
        
        assert isinstance(ar, pd.DataFrame)
        assert 'abnormal_return' in ar.columns
        assert 'mean_ar' in stats
    
    def test_calculate_cumulative_abnormal_returns(self):
        """Test CAR calculation."""
        ar = pd.DataFrame({
            'days_from_event': np.arange(-5, 6),
            'abnormal_return': np.random.normal(0.01, 0.02, 11),
        })
        
        car = analysis.calculate_cumulative_abnormal_returns(ar)
        
        assert isinstance(car, pd.DataFrame)
        assert len(car) == 11


class TestDiagnostics:
    """Tests for diagnostic and robustness checks."""
    
    def setup_method(self):
        """Setup test panel data."""
        n_firms = 10
        n_years = 10
        
        firms = np.repeat(np.arange(1, n_firms + 1), n_years)
        years = np.tile(np.arange(2015, 2025), n_firms)
        
        np.random.seed(42)
        treatment = np.where((years >= 2020) & (firms <= 5), 1, 0)
        outcome = 0.1 * treatment + np.random.normal(0, 0.1, len(firms))
        
        self.df = pd.DataFrame({
            'ric': firms,
            'Year': years,
            'green_bond_active': treatment,
            'outcome': outcome,
            'L1_Firm_Size': np.random.normal(10, 2, len(firms)),
            'L1_Leverage': np.random.uniform(0, 1, len(firms)),
            'L1_Asset_Turnover': np.random.uniform(0.5, 2, len(firms)),
        })
    
    def test_placebo_test(self):
        """Test placebo/falsification test."""
        result = analysis.placebo_test(
            self.df,
            outcome='outcome',
            treatment_col='green_bond_active'
        )
        
        assert 'placebo_coefficient' in result
        assert 'placebo_p_value' in result
    
    def test_specification_sensitivity(self):
        """Test specification sensitivity."""
        results = analysis.specification_sensitivity(
            self.df,
            outcome='outcome',
            treatment_col='green_bond_active'
        )
        
        assert isinstance(results, pd.DataFrame)
        assert len(results) > 0
        assert 'specification' in results.columns
    
    def test_heterogeneous_effects(self):
        """Test heterogeneous effects analysis."""
        self.df['subgroup'] = np.random.binomial(1, 0.5, len(self.df))
        
        results = analysis.heterogeneous_effects_analysis(
            self.df,
            outcome='outcome',
            treatment_col='green_bond_active',
            heterogeneity_var='subgroup'
        )
        
        assert isinstance(results, dict)
        assert len(results) >= 1


class TestRegressionAssumptions:
    """Tests for regression assumption verification."""
    
    def test_residual_properties(self):
        """Test that residuals behave as expected."""
        from asean_green_bonds.utils import validation
        
        # Create residuals
        residuals = pd.Series(np.random.normal(0, 1, 100))
        x_var = pd.Series(np.random.normal(0, 1, 100))
        
        report = validation.validate_regression_assumptions(residuals, x_var)
        
        assert 'n_residuals' in report
        assert 'normality_p_value' in report
        assert report['n_residuals'] == 100


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
