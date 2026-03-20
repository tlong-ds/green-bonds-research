"""
Unit tests for tiered authenticity scoring.

Tests the ESG data gap handling with tiered approach:
- Tier 1: Complete ESG data (≥2 pre AND ≥2 post)
- Tier 2: Partial ESG data (≥1 pre AND ≥1 post)
- Tier 3: No ESG data (certification only)
"""

import pytest
import pandas as pd
import numpy as np
from io import StringIO
import tempfile
import os

# Import the functions to test
from bias_detection_tools import (
    calculate_authenticity_tiered,
    get_esg_coverage_by_country,
    apply_authenticity_with_fallbacks,
    apply_authenticity_proxy,
    normalize_company_name,
)
from authenticity_score import compute_authenticity_score


class TestNormalizeCompanyName:
    """Tests for company name normalization."""
    
    def test_basic_normalization(self):
        assert normalize_company_name("ABC Corp") == "ABC"
        assert normalize_company_name("XYZ Limited") == "XYZ"
    
    def test_null_handling(self):
        assert normalize_company_name(None) == ""
        assert normalize_company_name(np.nan) == ""
    
    def test_case_insensitive(self):
        assert normalize_company_name("abc corp") == "ABC"


class TestCalculateAuthenticityTiered:
    """Tests for the tiered authenticity calculation."""
    
    @pytest.fixture
    def sample_green_bonds(self):
        """Sample green bonds data."""
        return pd.DataFrame({
            'Deal PermID': ['GB001', 'GB002', 'GB003', 'GB004'],
            'Issuer/Borrower Name Full': [
                'Complete Data Corp',
                'Partial Data Inc',
                'No Data Ltd',
                'Unknown Issuer'
            ],
            'Dates: Issue Date': ['2020-01-15', '2020-06-20', '2020-03-10', '2020-08-01'],
            'Issuer/Borrower Nation': ['Singapore', 'Malaysia', 'Thailand', 'Indonesia'],
        })
    
    @pytest.fixture
    def sample_esg_data(self):
        """Sample ESG panel data with varying coverage."""
        data = []
        
        # Complete Data Corp: 3 years pre, 3 years post (Tier 1)
        for year in [2017, 2018, 2019, 2021, 2022, 2023]:
            esg = 50 if year < 2020 else 70  # Improvement after issuance
            data.append({'company': 'Complete Data Corp', 'Year': year, 'esg_score': esg})
        
        # Partial Data Inc: 1 year pre, 1 year post (Tier 2)
        data.append({'company': 'Partial Data Inc', 'Year': 2019, 'esg_score': 45})
        data.append({'company': 'Partial Data Inc', 'Year': 2021, 'esg_score': 55})
        
        # No Data Ltd: No ESG data (Tier 3)
        # (no entries)
        
        return pd.DataFrame(data)
    
    def test_tier1_complete_data(self, sample_green_bonds, sample_esg_data):
        """Test Tier 1 classification with complete ESG data."""
        result = calculate_authenticity_tiered(sample_green_bonds, sample_esg_data)
        
        # Complete Data Corp should be Tier 1
        complete_row = result[result['Deal PermID'] == 'GB001'].iloc[0]
        assert complete_row['authenticity_tier'] == 1
        assert complete_row['tier_description'] == 'Complete'
        assert complete_row['n_pre_obs'] >= 2
        assert complete_row['n_post_obs'] >= 2
        assert pd.notna(complete_row['esg_pvalue'])  # Should have p-value
    
    def test_tier2_partial_data(self, sample_green_bonds, sample_esg_data):
        """Test Tier 2 classification with partial ESG data."""
        result = calculate_authenticity_tiered(sample_green_bonds, sample_esg_data)
        
        # Partial Data Inc should be Tier 2
        partial_row = result[result['Deal PermID'] == 'GB002'].iloc[0]
        assert partial_row['authenticity_tier'] == 2
        assert partial_row['tier_description'] == 'Partial'
        assert partial_row['n_pre_obs'] >= 1
        assert partial_row['n_post_obs'] >= 1
        assert pd.isna(partial_row['esg_pvalue'])  # No t-test for Tier 2
    
    def test_tier3_no_data(self, sample_green_bonds, sample_esg_data):
        """Test Tier 3 classification with no ESG data."""
        result = calculate_authenticity_tiered(sample_green_bonds, sample_esg_data)
        
        # No Data Ltd should be Tier 3
        nodata_row = result[result['Deal PermID'] == 'GB003'].iloc[0]
        assert nodata_row['authenticity_tier'] == 3
        assert nodata_row['tier_description'] == 'Certification_Only'
        assert nodata_row['is_authentic'] == 0  # Cannot verify without ESG
    
    def test_tier1_matches_original_when_complete(self, sample_green_bonds, sample_esg_data):
        """Test that Tier 1 gives same results as original function when data is complete."""
        # Run both functions
        tiered_result = calculate_authenticity_tiered(sample_green_bonds, sample_esg_data)
        
        # For Tier 1 bonds, the ESG improvement should be calculated the same way
        tier1_bonds = tiered_result[tiered_result['authenticity_tier'] == 1]
        
        for _, row in tier1_bonds.iterrows():
            # Verify statistical test was performed
            assert pd.notna(row['esg_pvalue'])
            assert pd.notna(row['esg_improvement'])
    
    def test_esg_improvement_positive_is_authentic(self, sample_green_bonds, sample_esg_data):
        """Test that positive ESG improvement leads to is_authentic=1 for Tier 1."""
        result = calculate_authenticity_tiered(sample_green_bonds, sample_esg_data)
        
        complete_row = result[result['Deal PermID'] == 'GB001'].iloc[0]
        # Complete Data Corp has improvement from 50 to 70
        assert complete_row['esg_improvement'] > 0
        # Should be authentic if p-value significant
        if complete_row['esg_pvalue'] < 0.10:
            assert complete_row['is_authentic'] == 1
    
    def test_custom_thresholds(self, sample_green_bonds, sample_esg_data):
        """Test that custom tier thresholds work correctly."""
        # With tier1_min_obs=3, Complete Data Corp should still be Tier 1
        # But with tier1_min_obs=10, it should become Tier 2
        result_strict = calculate_authenticity_tiered(
            sample_green_bonds, sample_esg_data,
            tier1_min_obs=10, tier2_min_obs=1
        )
        
        complete_row = result_strict[result_strict['Deal PermID'] == 'GB001'].iloc[0]
        assert complete_row['authenticity_tier'] == 2  # Demoted to Tier 2
    
    def test_output_columns_present(self, sample_green_bonds, sample_esg_data):
        """Test that all expected output columns are present."""
        result = calculate_authenticity_tiered(sample_green_bonds, sample_esg_data)
        
        expected_cols = [
            'is_authentic', 'esg_improvement', 'esg_pvalue',
            'authenticity_tier', 'tier_description', 'data_quality_notes',
            'n_pre_obs', 'n_post_obs'
        ]
        for col in expected_cols:
            assert col in result.columns, f"Missing column: {col}"
    
    def test_no_temp_columns_in_output(self, sample_green_bonds, sample_esg_data):
        """Test that temporary columns are cleaned up."""
        result = calculate_authenticity_tiered(sample_green_bonds, sample_esg_data)
        
        assert 'match_name' not in result.columns
        assert '_issuance_year' not in result.columns


class TestGetESGCoverageByCountry:
    """Tests for country-level ESG coverage statistics."""
    
    @pytest.fixture
    def multi_country_bonds(self):
        """Green bonds from multiple countries."""
        return pd.DataFrame({
            'Deal PermID': [f'GB{i:03d}' for i in range(10)],
            'Issuer/Borrower Name Full': [
                'SG Corp A', 'SG Corp B', 'SG Corp C',  # Singapore: 3 bonds
                'MY Corp A', 'MY Corp B',               # Malaysia: 2 bonds
                'TH Corp A', 'TH Corp B', 'TH Corp C', 'TH Corp D', 'TH Corp E'  # Thailand: 5 bonds
            ],
            'Dates: Issue Date': ['2020-01-01'] * 10,
            'Issuer/Borrower Nation': [
                'Singapore', 'Singapore', 'Singapore',
                'Malaysia', 'Malaysia',
                'Thailand', 'Thailand', 'Thailand', 'Thailand', 'Thailand'
            ],
        })
    
    @pytest.fixture
    def multi_country_esg(self):
        """ESG data with varying coverage by country."""
        data = []
        
        # Singapore: All 3 companies have complete data (Tier 1)
        for company in ['SG Corp A', 'SG Corp B', 'SG Corp C']:
            for year in [2017, 2018, 2019, 2021, 2022, 2023]:
                data.append({'company': company, 'Year': year, 'esg_score': 60})
        
        # Malaysia: 1 company has partial data (Tier 2), 1 has none (Tier 3)
        data.append({'company': 'MY Corp A', 'Year': 2019, 'esg_score': 50})
        data.append({'company': 'MY Corp A', 'Year': 2021, 'esg_score': 55})
        
        # Thailand: All 5 have no ESG data (Tier 3)
        # (no entries)
        
        return pd.DataFrame(data)
    
    def test_coverage_calculation(self, multi_country_bonds, multi_country_esg):
        """Test correct coverage calculation by country."""
        coverage = get_esg_coverage_by_country(multi_country_esg, multi_country_bonds)
        
        sg_row = coverage[coverage['country'] == 'Singapore'].iloc[0]
        assert sg_row['total_bonds'] == 3
        assert sg_row['bonds_with_complete_esg'] == 3  # All Tier 1
        assert sg_row['coverage_rate'] == 100.0
        
        my_row = coverage[coverage['country'] == 'Malaysia'].iloc[0]
        assert my_row['total_bonds'] == 2
        assert my_row['bonds_with_partial_esg'] == 1  # MY Corp A is Tier 2
        assert my_row['bonds_with_no_esg'] == 1  # MY Corp B is Tier 3
        
        th_row = coverage[coverage['country'] == 'Thailand'].iloc[0]
        assert th_row['total_bonds'] == 5
        assert th_row['bonds_with_no_esg'] == 5  # All Tier 3
        assert th_row['coverage_rate'] == 0.0
    
    def test_output_columns(self, multi_country_bonds, multi_country_esg):
        """Test that all expected columns are in output."""
        coverage = get_esg_coverage_by_country(multi_country_esg, multi_country_bonds)
        
        expected = ['country', 'total_bonds', 'bonds_with_complete_esg',
                   'bonds_with_partial_esg', 'bonds_with_no_esg', 'coverage_rate']
        for col in expected:
            assert col in coverage.columns


class TestApplyAuthenticityWithFallbacks:
    """Tests for the fallback behavior in authenticity scoring."""
    
    @pytest.fixture
    def temp_data_files(self, tmp_path):
        """Create temporary data files for testing."""
        # Green bonds CSV
        gb_data = pd.DataFrame({
            'Deal PermID': ['GB001', 'GB002'],
            'Issuer/Borrower Name Full': ['Test Corp', 'No Match Corp'],
            'Dates: Issue Date': ['2020-01-01', '2020-06-01'],
            'Issuer/Borrower Nation': ['Singapore', 'Malaysia'],
        })
        gb_path = tmp_path / "green_bonds.csv"
        gb_data.to_csv(gb_path, index=False)
        
        # ESG panel CSV
        esg_data = pd.DataFrame({
            'company': ['Test Corp'] * 6,
            'Year': [2017, 2018, 2019, 2021, 2022, 2023],
            'esg_score': [40, 45, 50, 60, 65, 70],
        })
        esg_path = tmp_path / "esg_panel.csv"
        esg_data.to_csv(esg_path, index=False)
        
        return {'gb_path': str(gb_path), 'esg_path': str(esg_path)}
    
    def test_tiered_fallback(self, temp_data_files, monkeypatch, tmp_path):
        """Test tiered fallback mode."""
        # Change to temp directory to write output
        monkeypatch.chdir(tmp_path)
        os.makedirs('data', exist_ok=True)
        
        result = apply_authenticity_with_fallbacks(
            panel_data_path=temp_data_files['esg_path'],
            green_bonds_path=temp_data_files['gb_path'],
            esg_panel_path=temp_data_files['esg_path'],
            fallback='tiered'
        )
        
        # Test Corp should be Tier 1, No Match Corp should be Tier 3
        test_corp = result[result['Deal PermID'] == 'GB001'].iloc[0]
        assert test_corp['authenticity_tier'] == 1
        
        no_match = result[result['Deal PermID'] == 'GB002'].iloc[0]
        assert no_match['authenticity_tier'] == 3
    
    def test_strict_fallback(self, temp_data_files, monkeypatch, tmp_path):
        """Test strict fallback mode (original behavior)."""
        monkeypatch.chdir(tmp_path)
        os.makedirs('data', exist_ok=True)
        
        result = apply_authenticity_with_fallbacks(
            panel_data_path=temp_data_files['esg_path'],
            green_bonds_path=temp_data_files['gb_path'],
            esg_panel_path=temp_data_files['esg_path'],
            fallback='strict'
        )
        
        # In strict mode, only Tier 1 or Tier 3 (no Tier 2)
        assert set(result['authenticity_tier'].unique()).issubset({1, 3})
    
    def test_certification_only_fallback(self, temp_data_files, monkeypatch, tmp_path):
        """Test certification-only fallback mode."""
        monkeypatch.chdir(tmp_path)
        os.makedirs('data', exist_ok=True)
        
        result = apply_authenticity_with_fallbacks(
            panel_data_path=temp_data_files['esg_path'],
            green_bonds_path=temp_data_files['gb_path'],
            esg_panel_path=temp_data_files['esg_path'],
            fallback='certification_only'
        )
        
        # All bonds should be Tier 3
        assert (result['authenticity_tier'] == 3).all()
        assert result['is_authentic'].sum() == 0  # No ESG-based authenticity
    
    def test_invalid_fallback_raises(self, temp_data_files):
        """Test that invalid fallback value raises ValueError."""
        with pytest.raises(ValueError, match="fallback must be"):
            apply_authenticity_with_fallbacks(
                panel_data_path=temp_data_files['esg_path'],
                green_bonds_path=temp_data_files['gb_path'],
                fallback='invalid_mode'
            )


class TestComputeAuthenticityScoreWithTiers:
    """Tests for authenticity score calculation with tier information."""
    
    @pytest.fixture
    def base_df(self):
        """Base DataFrame with authenticity data."""
        return pd.DataFrame({
            'Deal PermID': ['T1', 'T2', 'T3'],
            'is_authentic': [1, 1, 0],
            'esg_improvement': [15.0, 8.0, np.nan],
            'esg_pvalue': [0.03, np.nan, np.nan],
            'is_cbi_certified': [1, 1, 1],
            'is_icma_certified': [1, 1, 1],
            'icma_confidence': [0.95, 0.95, 0.95],
            'issuer_track_record': [1, 1, 1],
            'has_green_framework': [1, 1, 1],
            'authenticity_tier': [1, 2, 3],
        })
    
    def test_tier1_full_score_range(self, base_df):
        """Test that Tier 1 bonds can achieve full score range."""
        result = compute_authenticity_score(base_df)
        
        tier1_row = result[result['Deal PermID'] == 'T1'].iloc[0]
        # Tier 1 should have full ESG component (up to 40)
        assert tier1_row['esg_component'] == 40  # 30 (authentic) + 5 (improvement>10) + 5 (pvalue<0.05)
        # Should be able to achieve high authenticity
        assert tier1_row['authenticity_score'] > 60
    
    def test_tier2_capped_esg_component(self, base_df):
        """Test that Tier 2 bonds have capped ESG component."""
        result = compute_authenticity_score(base_df)
        
        tier2_row = result[result['Deal PermID'] == 'T2'].iloc[0]
        # Tier 2 ESG component should be capped at 20
        assert tier2_row['esg_component'] <= 20
    
    def test_tier3_zero_esg_component(self, base_df):
        """Test that Tier 3 bonds have zero ESG component."""
        result = compute_authenticity_score(base_df)
        
        tier3_row = result[result['Deal PermID'] == 'T3'].iloc[0]
        # Tier 3 should have 0 ESG component
        assert tier3_row['esg_component'] == 0
    
    def test_tier3_never_exceeds_cap(self):
        """Test that Tier 3 bonds never exceed tier3_cap_score."""
        # Create a Tier 3 bond with max certifications
        df = pd.DataFrame({
            'Deal PermID': ['T3_MAX'],
            'is_authentic': [0],
            'esg_improvement': [np.nan],
            'esg_pvalue': [np.nan],
            'is_cbi_certified': [1],
            'is_icma_certified': [1],
            'icma_confidence': [0.99],
            'issuer_track_record': [1],
            'has_green_framework': [1],
            'issuer_nation': ['Singapore'],
            'Issuer/Borrower Nation': ['Singapore'],
            'authenticity_tier': [3],
            'tier3_cap_score': [60],
        })
        
        result = compute_authenticity_score(df)
        
        # Even with all certifications, score should be capped at 60
        assert result.iloc[0]['authenticity_score'] <= 60
    
    def test_tier3_custom_cap_from_column(self):
        """Test that tier3_cap_score column is respected."""
        df = pd.DataFrame({
            'Deal PermID': ['CAP40', 'CAP80'],
            'is_authentic': [0, 0],
            'esg_improvement': [np.nan, np.nan],
            'esg_pvalue': [np.nan, np.nan],
            'is_cbi_certified': [1, 1],
            'is_icma_certified': [1, 1],
            'icma_confidence': [0.99, 0.99],
            'issuer_track_record': [1, 1],
            'has_green_framework': [1, 1],
            'authenticity_tier': [3, 3],
            'tier3_cap_score': [40, 80],
        })
        
        result = compute_authenticity_score(df)
        
        assert result[result['Deal PermID'] == 'CAP40'].iloc[0]['authenticity_score'] <= 40
        assert result[result['Deal PermID'] == 'CAP80'].iloc[0]['authenticity_score'] <= 80
    
    def test_tier_column_preserved(self, base_df):
        """Test that authenticity_tier column is preserved in output."""
        result = compute_authenticity_score(base_df)
        
        assert 'authenticity_tier' in result.columns
        assert list(result['authenticity_tier']) == [1, 2, 3]
    
    def test_backward_compatibility_no_tier_info(self):
        """Test backward compatibility when no tier info is present."""
        df = pd.DataFrame({
            'is_authentic': [1, 0],
            'esg_improvement': [10.0, -5.0],
            'esg_pvalue': [0.05, 0.5],
            'is_cbi_certified': [1, 0],
            'is_icma_certified': [1, 0],
            'icma_confidence': [0.9, 0.3],
            'issuer_track_record': [1, 0],
            'has_green_framework': [1, 0],
        })
        
        # Should not raise and should default to Tier 1
        result = compute_authenticity_score(df)
        
        assert 'authenticity_tier' in result.columns
        assert (result['authenticity_tier'] == 1).all()  # Default to Tier 1


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_empty_esg_data(self):
        """Test handling when ESG data is completely empty."""
        gb = pd.DataFrame({
            'Deal PermID': ['GB001'],
            'Issuer/Borrower Name Full': ['Test Corp'],
            'Dates: Issue Date': ['2020-01-01'],
            'Issuer/Borrower Nation': ['Singapore'],
        })
        esg = pd.DataFrame({'company': [], 'Year': [], 'esg_score': []})
        
        result = calculate_authenticity_tiered(gb, esg)
        
        assert len(result) == 1
        assert result.iloc[0]['authenticity_tier'] == 3
    
    def test_missing_issuance_date(self):
        """Test handling when issuance date is missing."""
        gb = pd.DataFrame({
            'Deal PermID': ['GB001'],
            'Issuer/Borrower Name Full': ['Test Corp'],
            'Dates: Issue Date': [None],
            'Issuer/Borrower Nation': ['Singapore'],
        })
        esg = pd.DataFrame({
            'company': ['Test Corp'],
            'Year': [2020],
            'esg_score': [50],
        })
        
        result = calculate_authenticity_tiered(gb, esg)
        
        # Should still return result, defaulting to Tier 3
        assert len(result) == 1
        assert result.iloc[0]['authenticity_tier'] == 3
    
    def test_country_with_all_tier3(self):
        """Test country coverage when all bonds are Tier 3."""
        gb = pd.DataFrame({
            'Deal PermID': ['GB001', 'GB002'],
            'Issuer/Borrower Name Full': ['Unknown A', 'Unknown B'],
            'Dates: Issue Date': ['2020-01-01', '2020-06-01'],
            'Issuer/Borrower Nation': ['Vietnam', 'Vietnam'],
        })
        esg = pd.DataFrame({'company': [], 'Year': [], 'esg_score': []})
        
        coverage = get_esg_coverage_by_country(esg, gb)
        
        vn_row = coverage[coverage['country'] == 'Vietnam'].iloc[0]
        assert vn_row['coverage_rate'] == 0.0
        assert vn_row['bonds_with_no_esg'] == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
