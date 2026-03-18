"""
Unit tests for authenticity verification module (CBI certification).
"""

import pytest
import pandas as pd
import numpy as np
from asean_green_bonds.authenticity import (
    extract_cbi_certification,
    compute_cbi_stats,
    validate_cbi_data
)


class TestExtractCBICertification:
    """Tests for extract_cbi_certification function."""
    
    def test_basic_extraction(self):
        """Test basic CBI certification extraction."""
        df = pd.DataFrame({
            'Primary Use Of Proceeds': ['Green Bond Purposes', 'Environmental Protection Proj.']
        })
        result = extract_cbi_certification(df)
        
        assert 'is_cbi_certified' in result.columns
        assert list(result['is_cbi_certified']) == [1, 0]
    
    def test_all_certified(self):
        """Test when all bonds are CBI certified."""
        df = pd.DataFrame({
            'Primary Use Of Proceeds': ['Green Bond Purposes'] * 5
        })
        result = extract_cbi_certification(df)
        
        assert (result['is_cbi_certified'] == 1).all()
    
    def test_none_certified(self):
        """Test when no bonds are CBI certified."""
        df = pd.DataFrame({
            'Primary Use Of Proceeds': ['Environmental Protection Proj.', 'Green Construction', 'Waste and Pollution Control']
        })
        result = extract_cbi_certification(df)
        
        assert (result['is_cbi_certified'] == 0).all()
    
    def test_null_handling(self):
        """Test handling of null values."""
        df = pd.DataFrame({
            'Primary Use Of Proceeds': ['Green Bond Purposes', None, 'Environmental Protection Proj.', np.nan]
        })
        result = extract_cbi_certification(df)
        
        # Nulls should be treated as not certified (0)
        assert list(result['is_cbi_certified']) == [1, 0, 0, 0]
    
    def test_custom_column_name(self):
        """Test with custom column name."""
        df = pd.DataFrame({
            'CustomColumn': ['Green Bond Purposes', 'Other']
        })
        result = extract_cbi_certification(df, column='CustomColumn')
        
        assert 'is_cbi_certified' in result.columns
        assert list(result['is_cbi_certified']) == [1, 0]
    
    def test_dataframe_not_modified(self):
        """Test that original DataFrame is not modified."""
        df = pd.DataFrame({
            'Primary Use Of Proceeds': ['Green Bond Purposes']
        })
        original_cols = df.columns.tolist()
        
        result = extract_cbi_certification(df)
        
        assert df.columns.tolist() == original_cols
        assert 'is_cbi_certified' not in df.columns
    
    def test_output_dtype(self):
        """Test that output is integer type."""
        df = pd.DataFrame({
            'Primary Use Of Proceeds': ['Green Bond Purposes', 'Other']
        })
        result = extract_cbi_certification(df)
        
        assert result['is_cbi_certified'].dtype == np.int64


class TestComputeCBIStats:
    """Tests for compute_cbi_stats function."""
    
    def test_basic_stats(self):
        """Test basic statistics computation."""
        df = pd.DataFrame({
            'is_cbi_certified': [1, 1, 0, 0, 1]
        })
        stats = compute_cbi_stats(df)
        
        assert stats['total'] == 5
        assert stats['cbi_certified'] == 3
        assert stats['not_certified'] == 2
        assert stats['coverage_pct'] == 60.0
    
    def test_all_certified_stats(self):
        """Test statistics when all are certified."""
        df = pd.DataFrame({
            'is_cbi_certified': [1] * 10
        })
        stats = compute_cbi_stats(df)
        
        assert stats['total'] == 10
        assert stats['cbi_certified'] == 10
        assert stats['not_certified'] == 0
        assert stats['coverage_pct'] == 100.0
    
    def test_none_certified_stats(self):
        """Test statistics when none are certified."""
        df = pd.DataFrame({
            'is_cbi_certified': [0] * 10
        })
        stats = compute_cbi_stats(df)
        
        assert stats['total'] == 10
        assert stats['cbi_certified'] == 0
        assert stats['not_certified'] == 10
        assert stats['coverage_pct'] == 0.0
    
    def test_empty_dataframe_stats(self):
        """Test statistics with empty DataFrame."""
        df = pd.DataFrame({
            'is_cbi_certified': []
        })
        stats = compute_cbi_stats(df)
        
        assert stats['total'] == 0
        assert stats['cbi_certified'] == 0
        assert stats['not_certified'] == 0
        assert stats['coverage_pct'] == 0.0
    
    def test_custom_column_name_stats(self):
        """Test statistics with custom column name."""
        df = pd.DataFrame({
            'custom_col': [1, 0, 1]
        })
        stats = compute_cbi_stats(df, cbi_column='custom_col')
        
        assert stats['total'] == 3
        assert stats['cbi_certified'] == 2
        assert stats['not_certified'] == 1
    
    def test_coverage_precision(self):
        """Test that coverage percentage is properly rounded."""
        df = pd.DataFrame({
            'is_cbi_certified': [1, 1, 0]  # 66.666...%
        })
        stats = compute_cbi_stats(df)
        
        assert stats['coverage_pct'] == 66.67


class TestValidateCBIData:
    """Tests for validate_cbi_data function."""
    
    def test_complete_data_validation(self):
        """Test validation of complete data."""
        df = pd.DataFrame({
            'Primary Use Of Proceeds': ['Green Bond Purposes'] * 5
        })
        validation = validate_cbi_data(df)
        
        assert validation['missing_count'] == 0
        assert len(validation['unique_values']) == 1
        assert 'No issues detected' in validation['issues']
    
    def test_missing_values_detection(self):
        """Test detection of missing values."""
        df = pd.DataFrame({
            'Primary Use Of Proceeds': ['Green Bond Purposes', None, 'Environmental Protection Proj.', np.nan]
        })
        validation = validate_cbi_data(df)
        
        assert validation['missing_count'] == 2
        assert any('null' in issue.lower() or 'missing' in issue.lower() 
                  for issue in validation['issues'])
    
    def test_value_counts(self):
        """Test value counts in validation."""
        df = pd.DataFrame({
            'Primary Use Of Proceeds': ['Green Bond Purposes'] * 3 + ['Environmental Protection Proj.'] * 2
        })
        validation = validate_cbi_data(df)
        
        assert validation['value_counts']['Green Bond Purposes'] == 3
        assert validation['value_counts']['Environmental Protection Proj.'] == 2
    
    def test_unique_values(self):
        """Test unique values detection."""
        df = pd.DataFrame({
            'Primary Use Of Proceeds': ['Green Bond Purposes', 'Environmental Protection Proj.', 'Green Construction']
        })
        validation = validate_cbi_data(df)
        
        assert len(validation['unique_values']) == 3
        assert 'Green Bond Purposes' in validation['unique_values']
    
    def test_custom_column_validation(self):
        """Test validation with custom column name."""
        df = pd.DataFrame({
            'CustomCol': ['Green Bond Purposes', None]
        })
        validation = validate_cbi_data(df, primary_use_col='CustomCol')
        
        assert validation['missing_count'] == 1
    
    def test_all_expected_values(self):
        """Test with all expected values present."""
        expected_vals = ['Green Bond Purposes', 'Environmental Protection Proj.', 
                        'Green Construction', 'Waste and Pollution Control']
        df = pd.DataFrame({
            'Primary Use Of Proceeds': expected_vals
        })
        validation = validate_cbi_data(df)
        
        # Should not flag unexpected values
        assert not any('unexpected' in issue.lower() for issue in validation['issues']) or \
               all('no issues' in issue.lower() for issue in validation['issues'])


class TestIntegration:
    """Integration tests using realistic data."""
    
    def test_end_to_end_workflow(self):
        """Test complete workflow from extraction to statistics."""
        df = pd.DataFrame({
            'Deal PermID': range(10),
            'Primary Use Of Proceeds': ['Green Bond Purposes'] * 8 + ['Environmental Protection Proj.', 'Green Construction']
        })
        
        # Extract
        df_with_cert = extract_cbi_certification(df)
        
        # Validate
        validation = validate_cbi_data(df)
        
        # Compute stats
        stats = compute_cbi_stats(df_with_cert)
        
        assert stats['total'] == 10
        assert stats['cbi_certified'] == 8
        assert stats['coverage_pct'] == 80.0
        assert validation['missing_count'] == 0
    
    def test_with_real_data_shape(self):
        """Test that operations preserve DataFrame shape and structure."""
        df = pd.DataFrame({
            'ID': range(333),
            'Primary Use Of Proceeds': ['Green Bond Purposes'] * 328 + 
                                      ['Environmental Protection Proj.'] * 3 +
                                      ['Green Construction'] + ['Waste and Pollution Control']
        })
        
        result = extract_cbi_certification(df)
        
        # Shape should be preserved with one new column
        assert result.shape[0] == 333
        assert result.shape[1] == 3
        
        stats = compute_cbi_stats(result)
        assert stats['total'] == 333
        assert stats['cbi_certified'] == 328
        assert stats['coverage_pct'] == 98.5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
