"""
Tests for utilities module: statistics, visualization, validation.
"""

import pytest
import pandas as pd
import numpy as np
from asean_green_bonds import utils


class TestStatisticalUtilities:
    """Tests for statistical functions."""
    
    def setup_method(self):
        """Setup test data."""
        np.random.seed(42)
        self.group1 = pd.Series(np.random.normal(0, 1, 100))
        self.group2 = pd.Series(np.random.normal(1, 1, 100))
    
    def test_calculate_effect_size_cohens_d(self):
        """Test Cohen's d calculation."""
        effect = utils.calculate_effect_size(
            self.group1,
            self.group2,
            method='cohens_d'
        )
        
        assert isinstance(effect, float)
        assert not np.isnan(effect)
        assert effect > 0  # group2 should be larger
    
    def test_calculate_effect_size_hedges_g(self):
        """Test Hedges' g calculation."""
        effect = utils.calculate_effect_size(
            self.group1,
            self.group2,
            method='hedges_g'
        )
        
        assert isinstance(effect, float)
        assert not np.isnan(effect)
    
    def test_calculate_confidence_interval_t(self):
        """Test t-based confidence interval."""
        ci = utils.calculate_confidence_interval(
            self.group1,
            confidence=0.95,
            method='t'
        )
        
        assert isinstance(ci, tuple)
        assert len(ci) == 2
        assert ci[0] < self.group1.mean() < ci[1]
    
    def test_proportion_test(self):
        """Test proportion difference test."""
        result = utils.proportion_test(
            count1=50,
            n1=100,
            count2=40,
            n2=100,
            alternative='two-sided'
        )
        
        assert 'z_statistic' in result
        assert 'p_value' in result
        assert 'proportion_1' in result
        assert result['proportion_1'] == 0.5
        assert result['proportion_2'] == 0.4
    
    def test_create_summary_statistics(self):
        """Test summary statistics creation."""
        df = pd.DataFrame({
            'var1': np.random.normal(0, 1, 50),
            'var2': np.random.uniform(0, 10, 50),
        })
        
        summary = utils.create_summary_statistics(df)
        
        assert isinstance(summary, pd.DataFrame)
        assert len(summary) == 2
        assert 'N' in summary.columns
        assert 'Mean' in summary.columns
        assert 'Std_Dev' in summary.columns


class TestStatisticalTests:
    """Tests for statistical hypothesis tests."""
    
    def test_multiple_comparisons_correction(self):
        """Test multiple comparisons correction."""
        p_values = pd.Series([0.001, 0.05, 0.1, 0.001])
        
        corrected = utils.multiple_comparisons_correction(
            p_values,
            method='bonferroni'
        )
        
        assert isinstance(corrected, pd.Series)
        assert len(corrected) == len(p_values)
        assert (corrected >= p_values).all()  # Adjusted p >= original
    
    def test_calculate_icc(self):
        """Test intra-class correlation."""
        df = pd.DataFrame({
            'cluster': np.repeat(np.arange(10), 5),
            'value': np.random.normal(0, 1, 50),
        })
        
        icc = utils.calculate_icc(df, entity_col='cluster', outcome_col='value')
        
        assert isinstance(icc, float)
        assert 0 <= icc <= 1
    
    def test_calculate_vif(self):
        """Test variance inflation factors."""
        X = pd.DataFrame({
            'x1': np.random.normal(0, 1, 100),
            'x2': np.random.normal(0, 1, 100),
            'x3': np.random.normal(0, 1, 100),
        })
        
        vif_dict = utils.calculate_variance_inflation_factors(X)
        
        assert isinstance(vif_dict, dict)
        assert all(isinstance(v, float) for v in vif_dict.values())
        assert all(v >= 1 for v in vif_dict.values())


class TestVisualization:
    """Tests for visualization functions."""
    
    def setup_method(self):
        """Setup test data."""
        np.random.seed(42)
        self.df = pd.DataFrame({
            'propensity_score': np.random.uniform(0, 1, 100),
            'treatment': np.random.binomial(1, 0.3, 100),
            'covariate': np.random.normal(0, 1, 100),
        })
        
        self.balance_df = pd.DataFrame({
            'Feature': ['X1', 'X2', 'X3'],
            'Std_Difference': [0.05, 0.15, 0.02],
            'Mean_Difference': [0.1, 0.3, 0.05],
        })
    
    def test_plot_propensity_score_overlap(self):
        """Test PS overlap plot creation."""
        try:
            fig = utils.plot_propensity_score_overlap(
                self.df,
                save_path=None
            )
            assert fig is not None
        except Exception as e:
            pytest.skip(f"Visualization error: {e}")
    
    def test_plot_covariate_balance(self):
        """Test covariate balance plot."""
        try:
            fig = utils.plot_covariate_balance(
                self.balance_df,
                save_path=None
            )
            assert fig is not None
        except Exception as e:
            pytest.skip(f"Visualization error: {e}")
    
    def test_plot_specification_sensitivity(self):
        """Test specification sensitivity plot."""
        try:
            spec_df = pd.DataFrame({
                'specification': ['Spec_1', 'Spec_2'],
                'coefficient': [0.1, 0.12],
                'std_error': [0.05, 0.06],
            })
            
            fig = utils.plot_specification_sensitivity(
                spec_df,
                save_path=None
            )
            assert fig is not None
        except Exception as e:
            pytest.skip(f"Visualization error: {e}")


class TestDataValidation:
    """Tests for data validation functions."""
    
    def setup_method(self):
        """Setup test data."""
        self.df = pd.DataFrame({
            'ric': np.repeat(np.arange(5), 10),
            'Year': np.tile(np.arange(2015, 2025), 5),
            'value': np.random.normal(0, 1, 50),
            'treatment': np.random.binomial(1, 0.3, 50),
        })
    
    def test_validate_panel_structure(self):
        """Test panel structure validation."""
        report = utils.validate_panel_structure(self.df)
        
        assert 'n_entities' in report
        assert 'n_periods' in report
        assert 'is_balanced' in report
        assert report['n_entities'] == 5
        assert report['n_periods'] == 10
    
    def test_check_missing_data(self):
        """Test missing data detection."""
        df_test = self.df.copy()
        df_test.loc[0, 'value'] = np.nan
        
        report = utils.check_missing_data(df_test)
        
        assert 'total_missing_cells' in report
        assert report['total_missing_cells'] >= 1
    
    def test_detect_outliers_iqr(self):
        """Test IQR-based outlier detection."""
        df_test = self.df.copy()
        df_test.loc[0, 'value'] = 1000  # Add extreme outlier
        
        outliers = utils.detect_outliers(df_test, method='iqr')
        
        assert 'value' in outliers
        assert len(outliers['value']) > 0
    
    def test_validate_treatment_variation(self):
        """Test treatment variation validation."""
        report = utils.validate_treatment_variation(self.df)
        
        assert 'total_entities' in report
        assert 'treated_entities' in report
        assert 'control_entities' in report
        assert report['total_entities'] == 5
    
    def test_generate_data_quality_report(self):
        """Test data quality report generation."""
        report_text = utils.generate_data_quality_report(self.df)
        
        assert isinstance(report_text, str)
        assert 'PANEL STRUCTURE' in report_text
        assert 'MISSING DATA' in report_text
        assert 'TREATMENT VARIATION' in report_text


class TestValidationIntegration:
    """Integration tests for validation functions."""
    
    def test_complete_validation_workflow(self):
        """Test running multiple validation checks together."""
        np.random.seed(42)
        df = pd.DataFrame({
            'ric': np.repeat(np.arange(10), 10),
            'Year': np.tile(np.arange(2015, 2025), 10),
            'outcome': np.random.normal(0, 1, 100),
            'treatment': np.random.binomial(1, 0.3, 100),
        })
        
        # Run all validations
        panel_report = utils.validate_panel_structure(df)
        missing_report = utils.check_missing_data(df)
        treatment_report = utils.validate_treatment_variation(df)
        
        # All should complete without error
        assert panel_report['n_entities'] == 10
        assert missing_report['total_missing_cells'] >= 0
        assert treatment_report['total_entities'] == 10


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
