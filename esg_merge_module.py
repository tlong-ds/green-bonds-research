"""
ESG Score Merging Module
========================
Merges ESG scores from LSEG and panel data to create comprehensive ESG attribute sets.
Handles matching between bond issuers and ESG companies, and extracts historical ESG trends.
"""

import pandas as pd
import numpy as np
import re
from typing import Tuple, Dict, List
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def normalize_company_name(name: str) -> str:
    """
    Normalize company names for matching by removing suffixes and punctuation.
    Reuses logic from bias_detection_tools.py for consistency.
    
    Args:
        name: Raw company name string
        
    Returns:
        Normalized company name in uppercase
    """
    if pd.isna(name):
        return ""
    name = str(name).upper()
    # Remove common corporate suffixes and punctuation
    suffixes = [
        r'\bPCL\b', r'\bPLC\b', r'\bLTD\b', r'\bLIMITED\b', r'\bCORP\b', 
        r'\bCORPORATION\b', r'\bINC\b', r'\bINCORPORATED\b', r'\bBHD\b', 
        r'\bSDN BHD\b', r'\bPT\b', r'\bTBK\b', r'\bCO\b', r'\bCOMPANY\b',
        r'\bGROUP\b', r'\bHOLDINGS\b', r'\bHOLDING\b', r'\bOJK\b', r'\bSA\b',
        r'\bCO LTD\b', r'\bCO., LTD\b', r'\bCONGLOMERATE\b'
    ]
    for suffix in suffixes:
        name = re.sub(suffix, '', name)
    name = re.sub(r'[^\w\s]', '', name)
    return name.strip()


def parse_issue_date(date_str: str) -> int:
    """
    Parse issue date string and extract year.
    
    Args:
        date_str: Date string in various formats (e.g., '8/1/2017', '2017-08-01')
        
    Returns:
        Year as integer, or None if parsing fails
    """
    if pd.isna(date_str):
        return None
    
    try:
        # Try to parse various date formats
        date_str = str(date_str).strip()
        
        # Try MM/DD/YYYY format
        if '/' in date_str:
            parts = date_str.split('/')
            if len(parts) == 3:
                return int(parts[-1])
        
        # Try YYYY-MM-DD format
        if '-' in date_str:
            parts = date_str.split('-')
            if len(parts) >= 1:
                return int(parts[0])
        
        # Try to parse as full date
        for fmt in ['%m/%d/%Y', '%Y-%m-%d', '%d/%m/%Y']:
            try:
                parsed = pd.to_datetime(date_str, format=fmt)
                return parsed.year
            except:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
    except Exception as e:
        logger.warning(f"Error parsing date {date_str}: {e}")
        return None


def normalize_country_name(country: str) -> str:
    """
    Normalize country names for consistent matching.
    
    Args:
        country: Country name string
        
    Returns:
        Normalized country name
    """
    if pd.isna(country):
        return ""
    
    # Country name mappings for common variations
    country_mapping = {
        'Philippines': ['PH', 'PHIL', 'PHILIPPINES', 'PHLIPPINES'],
        'India': ['IN', 'IND', 'INDIA'],
        'Singapore': ['SG', 'SING', 'SINGAPORE'],
        'Malaysia': ['MY', 'MAL', 'MALAYSIA'],
        'Vietnam': ['VN', 'VIE', 'VIETNAM'],
        'Thailand': ['TH', 'THAI', 'THAILAND'],
        'Indonesia': ['ID', 'IDO', 'INDONESIA'],
    }
    
    country_upper = str(country).upper().strip()
    
    for normalized, variants in country_mapping.items():
        if country_upper in variants or country_upper in [v.upper() for v in variants]:
            return normalized
    
    return country_upper


def normalize_and_match_issuers(bonds_df: pd.DataFrame, esg_df: pd.DataFrame) -> Tuple[Dict[int, Dict], Dict]:
    """
    Create a mapping between bond issuers and ESG panel companies.
    Uses multi-strategy approach: exact normalized match, prefix matching, key word matching.
    Requires high confidence to avoid false positives.
    
    Args:
        bonds_df: DataFrame with bond data (must have 'Issuer/Borrower Name Full' and 'Issuer/Borrower Nation')
        esg_df: DataFrame with ESG panel data (must have 'company' and 'country')
        
    Returns:
        Tuple of (matches dict mapping bond idx to ESG data, esg_lookup dict)
    """
    logger.info("Creating issuer name matching index...")
    
    # Create normalized lookup from ESG panel
    esg_df = esg_df.copy()
    esg_df['normalized_company'] = esg_df['company'].apply(normalize_company_name)
    esg_df['normalized_country'] = esg_df['country'].apply(normalize_country_name)
    
    # Create grouped ESG data for faster lookup
    esg_lookup = {}
    for (norm_name, norm_country), group in esg_df.groupby(['normalized_company', 'normalized_country']):
        key = (norm_name, norm_country)
        esg_lookup[key] = {
            'original_names': group['company'].unique().tolist(),
            'ticker': group['ticker'].iloc[0] if 'ticker' in group.columns else None,
            'years_available': sorted(group['Year'].unique()),
            'data': group
        }
    
    # Create index by country for fuzzy matching
    esg_by_country = {}
    for country, group in esg_df.groupby('normalized_country'):
        if country not in esg_by_country:
            esg_by_country[country] = []
        for norm_name, subgroup in group.groupby('normalized_company'):
            esg_by_country[country].append({
                'normalized': norm_name,
                'original_names': subgroup['company'].unique().tolist(),
                'ticker': subgroup['ticker'].iloc[0] if 'ticker' in subgroup.columns else None,
                'years_available': sorted(subgroup['Year'].unique()),
                'data': subgroup
            })
    
    def calculate_name_similarity(issuer_name: str, esg_name: str) -> float:
        """
        Calculate similarity between two normalized company names.
        Returns score from 0 to 1 (1 = exact match).
        """
        if issuer_name == esg_name:
            return 1.0
        
        issuer_parts = issuer_name.split()
        esg_parts = esg_name.split()
        
        if not issuer_parts or not esg_parts:
            return 0.0
        
        # Check if first word matches (most important signal)
        issuer_first = issuer_parts[0]
        esg_first = esg_parts[0]
        
        # Exact first word match
        if issuer_first == esg_first:
            # Count matching words
            matching_words = sum(1 for p in issuer_parts if p in esg_parts)
            total_words = len(issuer_parts)
            
            if matching_words == 0:
                return 0.3  # At least first word matched
            
            return matching_words / total_words
        
        # First words don't match - check if issuer is a short name that might be abbreviated
        # E.g., "PNB" might match "PNB GROUP" or issuer might contain first word of ESG
        if len(issuer_parts) == 1 and issuer_first in esg_name:
            # Single word issuer name, check if it's clearly in ESG name
            return 0.4
        
        # Check if both are multi-word and have significant overlap
        issuer_meaningful = [p for p in issuer_parts if len(p) > 2]
        esg_meaningful = [p for p in esg_parts if len(p) > 2]
        
        if issuer_meaningful and esg_meaningful:
            matching = sum(1 for p in issuer_meaningful if p in esg_meaningful)
            if matching >= len(issuer_meaningful):  # All meaningful words match
                return 0.5
        
        return 0.0
    
    # Match bonds to ESG companies
    matches = {}
    for idx, row in bonds_df.iterrows():
        issuer_name = row.get('Issuer/Borrower Name Full', '')
        issuer_country = row.get('Issuer/Borrower Nation', '')
        
        if pd.isna(issuer_name) or pd.isna(issuer_country):
            continue
        
        norm_issuer = normalize_company_name(issuer_name)
        norm_country = normalize_country_name(issuer_country)
        
        # Try exact match first
        key = (norm_issuer, norm_country)
        if key in esg_lookup:
            matches[idx] = esg_lookup[key]
            continue
        
        # Try fuzzy matching within the same country
        if norm_country in esg_by_country:
            best_match = None
            best_score = 0.0
            
            for esg_entry in esg_by_country[norm_country]:
                similarity = calculate_name_similarity(norm_issuer, esg_entry['normalized'])
                
                if similarity > best_score:
                    best_score = similarity
                    best_match = esg_entry
            
            # Only accept matches with high confidence (>= 0.6 means most words match)
            if best_match is not None and best_score >= 0.5:  # Slightly lower threshold to capture more
                matches[idx] = {
                    'original_names': best_match['original_names'],
                    'ticker': best_match['ticker'],
                    'years_available': best_match['years_available'],
                    'data': best_match['data']
                }
    
    logger.info(f"Matched {len(matches)}/{len(bonds_df)} bonds to ESG panel data")
    return matches, esg_lookup


def get_esg_scores_for_years(esg_data: pd.DataFrame, years: List[int]) -> Dict[int, float]:
    """
    Extract ESG scores from a company's ESG data for specified years.
    Uses forward/backward fill as fallback for missing years.
    
    Args:
        esg_data: DataFrame with ESG data for a single company (must have 'Year' and 'esg_score')
        years: List of years to retrieve scores for
        
    Returns:
        Dictionary mapping year to ESG score (or None if unavailable)
    """
    result = {}
    
    if esg_data.empty:
        return {year: None for year in years}
    
    # Create a series indexed by year
    esg_series = esg_data.set_index('Year')['esg_score'].sort_index()
    
    for year in years:
        if year in esg_series.index:
            result[year] = esg_series[year]
        else:
            # Try forward fill (most recent data before year)
            before = esg_series[esg_series.index < year]
            if not before.empty:
                result[year] = before.iloc[-1]
            else:
                # Try backward fill (earliest data after year)
                after = esg_series[esg_series.index > year]
                if not after.empty:
                    result[year] = after.iloc[0]
                else:
                    result[year] = None
    
    return result


def get_environmental_investment(esg_data: pd.DataFrame, year: int) -> str:
    """
    Extract environmental investment for a given year.
    
    Args:
        esg_data: DataFrame with ESG data for a single company
        year: Year to retrieve data for
        
    Returns:
        Environmental investment value or None
    """
    if esg_data.empty or 'environmental_investment' not in esg_data.columns:
        return None
    
    year_data = esg_data[esg_data['Year'] == year]
    if not year_data.empty:
        value = year_data['environmental_investment'].iloc[0]
        return value if pd.notna(value) else None
    
    return None


def merge_esg_scores(bonds_df: pd.DataFrame, esg_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """
    Merge ESG scores from panel data into bond dataset.
    Extracts pre-issuance, issuance year, and post-issuance ESG scores.
    
    Args:
        bonds_df: DataFrame with bond data
        esg_df: DataFrame with ESG panel data
        
    Returns:
        Tuple of (merged DataFrame with new ESG columns, statistics dictionary)
    """
    logger.info("Starting ESG score merge...")
    
    # Initialize result DataFrame
    result_df = bonds_df.copy()
    
    # Initialize new columns
    result_df['esg_score_pre_issuance'] = np.nan
    result_df['esg_score_issuance_year'] = np.nan
    result_df['esg_score_post_issuance'] = np.nan
    result_df['environmental_investment'] = None
    result_df['has_esg_data'] = False
    result_df['esg_data_source'] = 'none'
    result_df['esg_matching_company'] = None
    result_df['esg_coverage_years'] = None
    
    # Get matches
    matches, esg_lookup = normalize_and_match_issuers(bonds_df, esg_df)
    
    # Statistics
    stats = {
        'total_bonds': len(bonds_df),
        'bonds_with_matches': 0,
        'bonds_with_esg_data': 0,
        'bonds_with_pre_issuance': 0,
        'bonds_with_issuance_year': 0,
        'bonds_with_post_issuance': 0,
        'missing_issue_dates': 0,
        'no_esg_panel_match': 0,
        'esg_gaps': [],
    }
    
    # Process each matched bond
    for bond_idx, match_info in matches.items():
        row = result_df.loc[bond_idx]
        
        # Parse issue date
        issue_year = parse_issue_date(row['Dates: Issue Date'])
        if issue_year is None:
            stats['missing_issue_dates'] += 1
            continue
        
        # Get ESG data for this company
        esg_data = match_info['data']
        years_needed = [issue_year - 1, issue_year, issue_year + 1]
        
        # Get scores
        scores = get_esg_scores_for_years(esg_data, years_needed)
        
        # Update result
        if scores[issue_year - 1] is not None:
            result_df.loc[bond_idx, 'esg_score_pre_issuance'] = scores[issue_year - 1]
            stats['bonds_with_pre_issuance'] += 1
        
        if scores[issue_year] is not None:
            result_df.loc[bond_idx, 'esg_score_issuance_year'] = scores[issue_year]
            stats['bonds_with_issuance_year'] += 1
        
        if scores[issue_year + 1] is not None:
            result_df.loc[bond_idx, 'esg_score_post_issuance'] = scores[issue_year + 1]
            stats['bonds_with_post_issuance'] += 1
        
        # Get environmental investment
        env_inv = get_environmental_investment(esg_data, issue_year)
        if env_inv is not None:
            result_df.loc[bond_idx, 'environmental_investment'] = env_inv
        
        # Mark as having ESG data
        has_any_score = (
            scores[issue_year - 1] is not None or 
            scores[issue_year] is not None or 
            scores[issue_year + 1] is not None
        )
        
        if has_any_score:
            result_df.loc[bond_idx, 'has_esg_data'] = True
            result_df.loc[bond_idx, 'esg_data_source'] = 'panel'
            result_df.loc[bond_idx, 'esg_matching_company'] = match_info['original_names'][0]
            result_df.loc[bond_idx, 'esg_coverage_years'] = str(match_info['years_available'])
            stats['bonds_with_esg_data'] += 1
        
        stats['bonds_with_matches'] += 1
    
    # Calculate coverage
    stats['esg_panel_coverage'] = (stats['bonds_with_esg_data'] / stats['total_bonds'] * 100) if stats['total_bonds'] > 0 else 0
    stats['match_rate'] = (stats['bonds_with_matches'] / stats['total_bonds'] * 100) if stats['total_bonds'] > 0 else 0
    stats['no_esg_panel_match'] = stats['total_bonds'] - stats['bonds_with_matches']
    
    logger.info(f"ESG merge complete:")
    logger.info(f"  - Bonds matched to ESG panel: {stats['bonds_with_matches']}/{stats['total_bonds']} ({stats['match_rate']:.1f}%)")
    logger.info(f"  - Bonds with ESG data: {stats['bonds_with_esg_data']}/{stats['total_bonds']} ({stats['esg_panel_coverage']:.1f}%)")
    logger.info(f"  - Pre-issuance scores: {stats['bonds_with_pre_issuance']}")
    logger.info(f"  - Issuance year scores: {stats['bonds_with_issuance_year']}")
    logger.info(f"  - Post-issuance scores: {stats['bonds_with_post_issuance']}")
    logger.info(f"  - Missing issue dates: {stats['missing_issue_dates']}")
    
    return result_df, stats


def create_esg_coverage_report(result_df: pd.DataFrame, stats: Dict) -> str:
    """
    Generate a detailed ESG coverage report.
    
    Args:
        result_df: Merged DataFrame with ESG data
        stats: Statistics dictionary from merge_esg_scores
        
    Returns:
        Formatted report string
    """
    report = []
    report.append("=" * 80)
    report.append("ESG SCORE MERGING COVERAGE REPORT")
    report.append("=" * 80)
    report.append("")
    
    # Summary statistics
    report.append("SUMMARY STATISTICS:")
    report.append(f"  Total bonds processed: {stats['total_bonds']}")
    report.append(f"  Bonds matched to ESG panel: {stats['bonds_with_matches']} ({stats['match_rate']:.1f}%)")
    report.append(f"  Bonds with ESG data: {stats['bonds_with_esg_data']} ({stats['esg_panel_coverage']:.1f}%)")
    report.append("")
    
    # Score availability
    report.append("SCORE AVAILABILITY:")
    report.append(f"  Pre-issuance ESG scores: {stats['bonds_with_pre_issuance']} ({stats['bonds_with_pre_issuance']/stats['total_bonds']*100:.1f}%)")
    report.append(f"  Issuance year ESG scores: {stats['bonds_with_issuance_year']} ({stats['bonds_with_issuance_year']/stats['total_bonds']*100:.1f}%)")
    report.append(f"  Post-issuance ESG scores: {stats['bonds_with_post_issuance']} ({stats['bonds_with_post_issuance']/stats['total_bonds']*100:.1f}%)")
    report.append("")
    
    # Data quality
    report.append("DATA QUALITY:")
    report.append(f"  Missing issue dates: {stats['missing_issue_dates']}")
    report.append(f"  No ESG panel match: {stats['no_esg_panel_match']}")
    report.append("")
    
    # ESG score statistics
    esg_scores = result_df['esg_score_issuance_year'].dropna()
    if len(esg_scores) > 0:
        report.append("ESG SCORE STATISTICS (Issuance Year):")
        report.append(f"  Mean: {esg_scores.mean():.2f}")
        report.append(f"  Median: {esg_scores.median():.2f}")
        report.append(f"  Std Dev: {esg_scores.std():.2f}")
        report.append(f"  Min: {esg_scores.min():.2f}")
        report.append(f"  Max: {esg_scores.max():.2f}")
        report.append("")
    
    # Coverage by country
    report.append("COVERAGE BY COUNTRY:")
    country_stats = result_df.groupby('Issuer/Borrower Nation').agg({
        'has_esg_data': ['sum', 'count'],
        'esg_score_issuance_year': 'mean'
    }).round(2)
    for country, row in country_stats.iterrows():
        esg_count = int(row[('has_esg_data', 'sum')])
        total_count = int(row[('has_esg_data', 'count')])
        pct = (esg_count / total_count * 100) if total_count > 0 else 0
        avg_score = row[('esg_score_issuance_year', 'mean')]
        report.append(f"  {country}: {esg_count}/{total_count} ({pct:.1f}%) - Avg ESG Score: {avg_score:.2f}" if not pd.isna(avg_score) else f"  {country}: {esg_count}/{total_count} ({pct:.1f}%)")
    report.append("")
    
    report.append("=" * 80)
    return "\n".join(report)


def create_sample_output(result_df: pd.DataFrame, n_samples: int = 10) -> str:
    """
    Create a sample of merged data showing key columns.
    
    Args:
        result_df: Merged DataFrame
        n_samples: Number of samples to show
        
    Returns:
        Formatted sample string
    """
    sample = result_df[result_df['has_esg_data']].head(n_samples)
    
    output = []
    output.append("=" * 80)
    output.append("SAMPLE OF MERGED ESG DATA")
    output.append("=" * 80)
    output.append("")
    
    key_cols = [
        'Issuer/Borrower Name Full', 'Dates: Issue Date', 'Issuer/Borrower Nation',
        'esg_matching_company', 'esg_score_pre_issuance', 'esg_score_issuance_year',
        'esg_score_post_issuance', 'environmental_investment', 'esg_coverage_years'
    ]
    
    for idx, (_, row) in enumerate(sample.iterrows(), 1):
        output.append(f"Record {idx}:")
        output.append(f"  Issuer: {row['Issuer/Borrower Name Full']}")
        output.append(f"  Issue Date: {row['Dates: Issue Date']}")
        output.append(f"  Country: {row['Issuer/Borrower Nation']}")
        output.append(f"  Matched to: {row['esg_matching_company']}")
        output.append(f"  ESG Score (Pre): {row['esg_score_pre_issuance']}")
        output.append(f"  ESG Score (Year): {row['esg_score_issuance_year']}")
        output.append(f"  ESG Score (Post): {row['esg_score_post_issuance']}")
        output.append(f"  Environmental Investment: {row['environmental_investment']}")
        output.append(f"  Coverage Years: {row['esg_coverage_years']}")
        output.append("")
    
    output.append("=" * 80)
    return "\n".join(output)
