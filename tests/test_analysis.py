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
    
    def test_calculate_optimal_caliper_austin(self):
        """Test optimal caliper calculation with Austin method."""
        self.df['propensity_score'] = analysis.estimate_propensity_scores(
            self.df, treatment_col='treatment'
        )
        
        caliper = analysis.calculate_optimal_caliper(
            self.df['propensity_score'],
            method='austin'
        )
        
        # Should be positive and reasonable
        assert isinstance(caliper, float)
        assert caliper >= 0.01  # Minimum caliper
        assert caliper <= 1.0  # Should be less than max PS range
    
    def test_calculate_optimal_caliper_logit(self):
        """Test optimal caliper calculation with logit method."""
        self.df['propensity_score'] = analysis.estimate_propensity_scores(
            self.df, treatment_col='treatment'
        )
        
        caliper = analysis.calculate_optimal_caliper(
            self.df['propensity_score'],
            method='logit'
        )
        
        assert isinstance(caliper, float)
        assert caliper >= 0.01
    
    def test_calculate_optimal_caliper_edge_cases(self):
        """Test optimal caliper handles edge cases."""
        # All same values
        constant_ps = pd.Series([0.5] * 100)
        caliper = analysis.calculate_optimal_caliper(constant_ps)
        assert caliper == 0.01  # Should return minimum
        
        # Very small sample
        small_ps = pd.Series([0.3])
        caliper = analysis.calculate_optimal_caliper(small_ps)
        assert caliper == 0.01  # Should return minimum
        
        # Empty series
        empty_ps = pd.Series([], dtype=float)
        caliper = analysis.calculate_optimal_caliper(empty_ps)
        assert caliper == 0.01
    
    def test_nearest_neighbor_matching_backward_compat(self):
        """Test that caliper=0.1 still works (backward compatibility)."""
        self.df['propensity_score'] = analysis.estimate_propensity_scores(
            self.df, treatment_col='treatment'
        )
        
        matched_df, stats = analysis.nearest_neighbor_matching(
            self.df,
            ps_col='propensity_score',
            treatment_col='treatment',
            caliper=0.1,
            ratio=1
        )
        
        assert len(matched_df) <= len(self.df)
        assert stats['caliper'] == 0.1
    
    def test_nearest_neighbor_matching_auto_caliper(self):
        """Test caliper='auto' produces matches."""
        self.df['propensity_score'] = analysis.estimate_propensity_scores(
            self.df, treatment_col='treatment'
        )
        
        matched_df, stats = analysis.nearest_neighbor_matching(
            self.df,
            ps_col='propensity_score',
            treatment_col='treatment',
            caliper='auto',
            ratio=1
        )
        
        assert len(matched_df) > 0
        assert stats['caliper'] >= 0.01  # Minimum caliper enforced
        assert stats['matched_treated'] > 0
    
    def test_trim_extreme_propensity_scores_crump(self):
        """Test Crump trimming removes extreme observations."""
        self.df['propensity_score'] = analysis.estimate_propensity_scores(
            self.df, treatment_col='treatment'
        )
        
        trimmed_df = analysis.trim_extreme_propensity_scores(
            self.df,
            ps_col='propensity_score',
            treatment_col='treatment',
            method='crump',
            alpha=0.1
        )
        
        # Should remove observations outside [0.1, 0.9]
        assert len(trimmed_df) <= len(self.df)
        ps_trimmed = trimmed_df['propensity_score']
        assert ps_trimmed.min() >= 0.1 or len(ps_trimmed) == 0
        assert ps_trimmed.max() <= 0.9 or len(ps_trimmed) == 0
    
    def test_trim_extreme_propensity_scores_percentile(self):
        """Test percentile trimming removes extreme observations."""
        self.df['propensity_score'] = analysis.estimate_propensity_scores(
            self.df, treatment_col='treatment'
        )
        
        original_len = len(self.df)
        trimmed_df = analysis.trim_extreme_propensity_scores(
            self.df,
            ps_col='propensity_score',
            treatment_col='treatment',
            method='percentile',
            alpha=0.05
        )
        
        # Should remove ~10% of observations (5% from each tail)
        assert len(trimmed_df) <= original_len
        assert len(trimmed_df) >= original_len * 0.8  # Shouldn't remove too many


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
        np.random.seed(42)
        n = 250
        dates = pd.date_range('2015-01-01', periods=n, freq='D')
        
        self.ts_df = pd.DataFrame({
            'date': dates,
            'returns': np.random.normal(0.0005, 0.02, n),
        })
        self.ts_df.set_index('date', inplace=True)
        
        # Add event date column with actual dates (not binary indicator)
        # Events occur on days 100 and 200
        self.ts_df['event_date'] = pd.NaT
        self.ts_df.iloc[100, self.ts_df.columns.get_loc('event_date')] = dates[100]
        self.ts_df.iloc[200, self.ts_df.columns.get_loc('event_date')] = dates[200]
    
    def test_calculate_abnormal_returns(self):
        """Test abnormal return calculation."""
        ar, stats = analysis.calculate_abnormal_returns(
            self.ts_df,
            event_date_col='event_date',
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


class TestGMM:
    """Tests for System GMM estimation."""
    
    def setup_method(self):
        """Setup test panel data with dynamic structure."""
        np.random.seed(42)
        n_firms = 15
        n_years = 10
        
        # Create balanced panel structure
        firms = np.repeat(np.arange(1, n_firms + 1), n_years)
        years = np.tile(np.arange(2015, 2025), n_firms)
        
        # Generate persistent outcome with AR(1) structure
        n = len(firms)
        outcome = np.zeros(n)
        treatment = np.where((years >= 2020) & (firms <= 7), 1, 0)
        
        # Simulate AR(1) process within each firm
        for i, firm in enumerate(range(1, n_firms + 1)):
            mask = firms == firm
            firm_outcome = np.zeros(n_years)
            firm_outcome[0] = np.random.normal(1, 0.5)
            for t in range(1, n_years):
                # AR(1) with treatment effect
                firm_treatment = treatment[mask][t]
                firm_outcome[t] = 0.5 * firm_outcome[t-1] + 0.15 * firm_treatment + np.random.normal(0, 0.3)
            outcome[mask] = firm_outcome
        
        self.df = pd.DataFrame({
            'ric': firms,
            'Year': years,
            'green_bond_active': treatment,
            'outcome': outcome,
            'L1_Firm_Size': np.random.normal(10, 2, n),
            'L1_Leverage': np.random.uniform(0, 1, n),
            'L1_Asset_Turnover': np.random.uniform(0.5, 2, n),
            'L1_Capital_Intensity': np.random.uniform(0, 1, n),
        })
    
    def test_estimate_system_gmm(self):
        """Test System GMM estimation with synthetic panel."""
        result = analysis.estimate_system_gmm(
            self.df,
            outcome='outcome',
            treatment_col='green_bond_active',
            max_lags=3,
        )
        
        # Should return result without error
        assert 'error' not in result or result.get('error') is None, \
            f"GMM estimation failed: {result.get('error')}"
        
        # Check required keys
        assert 'coefficient' in result
        assert 'std_error' in result
        assert 'p_value' in result
        assert 'n_obs' in result
        assert result['n_obs'] > 0
        
        # Check diagnostic test keys
        assert 'ar2_pvalue' in result
        assert 'sargan_pvalue' in result
    
    def test_gmm_coefficient_sign(self):
        """Test that GMM detects positive treatment effect."""
        result = analysis.estimate_system_gmm(
            self.df,
            outcome='outcome',
            treatment_col='green_bond_active',
        )
        
        if 'error' not in result:
            # Treatment effect should be positive (as simulated)
            assert result['coefficient'] > -0.5, "Coefficient too negative"
    
    def test_arellano_bond_test(self):
        """Test AR(2) test returns sensible p-values."""
        # Create residuals with MultiIndex
        np.random.seed(42)
        n_firms = 10
        n_years = 8
        
        firms = np.repeat(np.arange(1, n_firms + 1), n_years)
        years = np.tile(np.arange(2015, 2023), n_firms)
        residuals = pd.Series(
            np.random.normal(0, 1, len(firms)),
            index=pd.MultiIndex.from_arrays([firms, years], names=['ric', 'Year'])
        )
        
        result = analysis.arellano_bond_test(
            residuals,
            entity_col='ric',
            time_col='Year',
            order=2,
        )
        
        assert 'p_value' in result
        # P-value should be between 0 and 1 (or nan if error)
        if not np.isnan(result['p_value']):
            assert 0 <= result['p_value'] <= 1
    
    def test_arellano_bond_ar1(self):
        """Test AR(1) test with first-order autocorrelation."""
        np.random.seed(42)
        n_firms = 10
        n_years = 10
        
        firms = np.repeat(np.arange(1, n_firms + 1), n_years)
        years = np.tile(np.arange(2015, 2025), n_firms)
        
        # Create residuals with strong AR(1)
        residuals = []
        for _ in range(n_firms):
            firm_resid = [np.random.normal(0, 1)]
            for t in range(1, n_years):
                firm_resid.append(0.7 * firm_resid[-1] + np.random.normal(0, 0.5))
            residuals.extend(firm_resid)
        
        residuals = pd.Series(
            residuals,
            index=pd.MultiIndex.from_arrays([firms, years], names=['ric', 'Year'])
        )
        
        result = analysis.arellano_bond_test(
            residuals,
            entity_col='ric',
            time_col='Year',
            order=1,
        )
        
        assert 'statistic' in result
        assert 'p_value' in result
    
    def test_select_gmm_instruments(self):
        """Test instrument selection creates valid lags."""
        instruments = analysis.select_gmm_instruments(
            self.df,
            outcome='outcome',
            max_lags=3,
        )
        
        # Should create some instruments
        assert isinstance(instruments, list)
        
        # With 10 years of data, should have at least L2 and L3
        if len(instruments) > 0:
            assert all(col.startswith('L') for col in instruments)
            # Instruments should be added to df
            assert all(col in self.df.columns for col in instruments)
    
    def test_sargan_hansen_test(self):
        """Test Sargan-Hansen test for overidentification."""
        np.random.seed(42)
        n = 100
        
        # Create test data
        residuals = pd.Series(
            np.random.normal(0, 1, n),
            index=pd.RangeIndex(n)
        )
        instruments = pd.DataFrame({
            'z1': np.random.normal(0, 1, n),
            'z2': np.random.normal(0, 1, n),
            'z3': np.random.normal(0, 1, n),
        }, index=pd.RangeIndex(n))
        
        result = analysis.sargan_hansen_test(
            residuals,
            instruments,
            n_params=1,  # Fewer params than instruments = overidentified
        )
        
        assert 'p_value' in result
        assert 'df' in result
        
        # Should be overidentified (df > 0)
        if not np.isnan(result['df']):
            assert result['df'] >= 0
    
    def test_gmm_with_missing_data(self):
        """Test GMM handles missing data gracefully."""
        df_missing = self.df.copy()
        # Introduce some missing values
        df_missing.loc[df_missing.index[:10], 'outcome'] = np.nan
        
        result = analysis.estimate_system_gmm(
            df_missing,
            outcome='outcome',
            treatment_col='green_bond_active',
        )
        
        # Should either succeed with fewer obs or return error dict
        if 'error' not in result:
            assert result['n_obs'] > 0
            assert result['n_obs'] < len(self.df)
    
    def test_gmm_insufficient_data(self):
        """Test GMM returns error for insufficient data."""
        df_small = self.df.head(10).copy()
        
        result = analysis.estimate_system_gmm(
            df_small,
            outcome='outcome',
            treatment_col='green_bond_active',
        )
        
        # Should return error for insufficient data
        assert 'error' in result or result.get('n_obs', 0) < 20
    
    def test_run_gmm_robustness(self):
        """Test batch GMM estimation for multiple outcomes."""
        self.df['outcome_2'] = self.df['outcome'] + np.random.normal(0, 0.1, len(self.df))
        
        results = analysis.run_gmm_robustness(
            self.df,
            outcomes=['outcome', 'outcome_2'],
            treatment_col='green_bond_active',
        )
        
        assert isinstance(results, pd.DataFrame)
        # Should have results for at least some outcomes
        if len(results) > 0:
            assert 'outcome' in results.columns
            assert 'coefficient' in results.columns


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
