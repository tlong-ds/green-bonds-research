"""
Example usage of ICMA (International Capital Market Association) Green Bond
Principles certification functions.

This script demonstrates how to use the authenticity module to extract, validate,
and compute statistics on ICMA certification for green bonds, and compares
ICMA certification with CBI certification.
"""

import pandas as pd
from pathlib import Path
import sys

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from asean_green_bonds.authenticity import (
    extract_cbi_certification,
    extract_icma_certification,
    compute_cbi_stats,
    compute_icma_stats,
    validate_cbi_data,
    validate_icma_data,
    compare_cbi_vs_icma
)


def example_1_icma_basic_extraction():
    """Example 1: Basic ICMA certification extraction."""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Basic ICMA Certification Extraction")
    print("=" * 80)
    
    # Create sample data
    data = {
        'Bond ID': ['BOND001', 'BOND002', 'BOND003', 'BOND004', 'BOND005'],
        'Issuer': ['Company A', 'Company B', 'Company C', 'Company D', 'Company E'],
        'Dates: Issue Date': [
            pd.Timestamp('2020-01-15'),
            pd.Timestamp('2012-06-01'),  # Before ICMA GBP
            pd.Timestamp('2021-03-20'),
            pd.Timestamp('2019-11-30'),
            pd.Timestamp('2015-05-10')
        ],
        'Primary Use Of Proceeds': [
            'Green Bond Purposes',
            'Green Bond Purposes',
            'Environmental Protection Proj.',
            'Green Bond Purposes',
            'Green Bond Purposes'
        ],
        'Offering Technique': [
            'Negotiated Sale',
            None,
            'Issued off MTN programme',
            'Best Efforts',
            'Issued off MTN programme'
        ]
    }
    df = pd.DataFrame(data)
    
    print("\nOriginal DataFrame:")
    print(df)
    
    # Extract ICMA certification
    df_icma = extract_icma_certification(df)
    
    print("\nDataFrame with ICMA certification:")
    print(df_icma[['Bond ID', 'Dates: Issue Date', 'Primary Use Of Proceeds', 
                    'is_icma_certified', 'icma_confidence']])
    
    print("\nInterpretation:")
    for idx, row in df_icma.iterrows():
        bond_id = row['Bond ID']
        cert = row['is_icma_certified']
        conf = row['icma_confidence']
        status = "CERTIFIED" if cert == 1 else "NOT CERTIFIED"
        confidence_level = "HIGH" if conf >= 0.8 else "MEDIUM" if conf >= 0.6 else "LOW"
        print(f"  {bond_id}: {status} (confidence: {conf:.2f} - {confidence_level})")


def example_2_icma_confidence_scores():
    """Example 2: Understanding ICMA confidence scores."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: ICMA Confidence Scores Explanation")
    print("=" * 80)
    
    print("""
ICMA Certification Confidence Scores:
────────────────────────────────────

The confidence score (0.0 - 1.0) reflects how likely a bond is to be ICMA
Green Bond Principles compliant, based on available data.

Scoring Breakdown:
- Issue Date after June 2014 (ICMA launch):        +0.5
- Primary Use = "Green Bond Purposes":              +0.4
- Other Environmental Use of Proceeds:             +0.1
- Bonus: All criteria met:                         No additional

Score Interpretation:
- ≥ 0.8 (HIGH):     Likely ICMA certified (uses GBP, recent, documented)
- 0.6-0.8 (MEDIUM): Possibly ICMA certified (uses GBP, recent)
- 0.4-0.6 (LOW):    Environmental but uncertain alignment
- < 0.4 (UNCERTAIN): Insufficient evidence

Certification Flag:
- is_icma_certified = 1: confidence >= 0.7 (medium or higher)
- is_icma_certified = 0: confidence < 0.7 (low or uncertain)
    """)


def example_3_icma_statistics():
    """Example 3: Computing ICMA statistics."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Computing ICMA Statistics")
    print("=" * 80)
    
    # Create sample data (100 bonds)
    n = 100
    dates = pd.date_range(start='2014-01-01', end='2021-12-31', periods=n)
    data = {
        'Dates: Issue Date': dates,
        'Primary Use Of Proceeds': (
            ['Green Bond Purposes'] * 80 +
            ['Environmental Protection Proj.'] * 12 +
            ['Green Construction'] * 5 +
            ['Waste and Pollution Control'] * 3
        ),
        'Offering Technique': (
            ['Issued off MTN programme'] * 50 +
            [None] * 50
        )
    }
    df = pd.DataFrame(data)
    
    # Extract ICMA certification
    df_icma = extract_icma_certification(df)
    
    # Compute statistics
    stats = compute_icma_stats(df_icma)
    
    print(f"\nICMA Certification Statistics (100 bonds):")
    print(f"─" * 50)
    print(f"Total bonds:                    {stats['total']}")
    print(f"ICMA certified:                 {stats['icma_certified']}")
    print(f"Not certified:                  {stats['not_certified']}")
    print(f"Coverage:                       {stats['coverage_pct']}%")
    print(f"Average confidence score:       {stats['avg_confidence']}")
    
    print(f"\nConfidence Distribution:")
    print(f"─" * 50)
    for level, count in stats['confidence_distribution'].items():
        pct = round((count / stats['total'] * 100) if stats['total'] > 0 else 0, 1)
        bar = '█' * (count // 5)
        print(f"  {level:10s}: {count:3d} bonds ({pct:5.1f}%) {bar}")


def example_4_data_validation():
    """Example 4: Validating ICMA data quality."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: ICMA Data Quality Validation")
    print("=" * 80)
    
    # Create sample data with some quality issues
    data = {
        'Bond ID': list(range(1, 51)),
        'Dates: Issue Date': [
            pd.Timestamp('2020-01-15') if i % 2 == 0 else None
            for i in range(50)
        ],
        'Primary Use Of Proceeds': (
            ['Green Bond Purposes'] * 40 +
            ['Environmental Protection Proj.'] * 8 +
            [None] * 2
        ),
        'Offering Technique': (
            ['Negotiated Sale'] * 25 +
            [None] * 25
        )
    }
    df = pd.DataFrame(data)
    
    # Validate
    validation = validate_icma_data(df)
    
    print(f"\nData Validation Results (50 bonds):")
    print(f"─" * 50)
    print(f"Date coverage:                  {validation['date_coverage']}%")
    print(f"Use of Proceeds coverage:       {validation['use_of_proceeds_coverage']}%")
    print(f"Offering Technique coverage:    {validation['offering_technique_coverage']}%")
    print(f"Post-2014 bonds:                {validation['post_2014_pct']}%")
    print(f"Bonds with GBP purposes:        {validation['gbp_purposes_pct']}%")
    
    print(f"\nData Quality Assessment:")
    print(f"─" * 50)
    for issue in validation['issues']:
        status = "✓" if issue == "Data quality acceptable for ICMA detection" else "⚠"
        print(f"  {status} {issue}")


def example_5_cbi_vs_icma_comparison():
    """Example 5: Comparing CBI and ICMA certification."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: CBI vs ICMA Certification Comparison")
    print("=" * 80)
    
    # Create sample data
    data = {
        'Bond ID': list(range(1, 21)),
        'Issuer': [f'Company {chr(64+i)}' for i in range(1, 21)],
        'Dates: Issue Date': pd.date_range(start='2015-01-01', periods=20, freq='Q'),
        'Primary Use Of Proceeds': (
            ['Green Bond Purposes'] * 18 +
            ['Environmental Protection Proj.'] * 2
        ),
        'Offering Technique': (
            ['Issued off MTN programme'] * 12 +
            [None] * 8
        )
    }
    df = pd.DataFrame(data)
    
    # Extract both certifications
    df_cbi = extract_cbi_certification(df)
    df_both = extract_icma_certification(df_cbi)
    
    # Compare
    comparison = compare_cbi_vs_icma(df_both)
    
    print(f"\nCertification Comparison (20 bonds):")
    print(f"─" * 50)
    print(f"Both CBI and ICMA:              {comparison['both']} bonds")
    print(f"CBI only:                       {comparison['cbi_only']} bonds")
    print(f"ICMA only:                      {comparison['icma_only']} bonds")
    print(f"Neither:                        {comparison['neither']} bonds")
    print(f"\nTotal CBI certified:            {comparison['cbi_total']} bonds")
    print(f"Total ICMA certified:           {comparison['icma_total']} bonds")
    print(f"Overlap (ICMA of CBI):          {comparison['overlap_pct']}%")
    
    print(f"\nInterpretation:")
    print(f"─" * 50)
    print(f"All CBI-certified bonds are ICMA-compliant:" if comparison['cbi_only'] == 0 else f"{comparison['cbi_only']} CBI bonds lack ICMA criteria")
    if comparison['icma_only'] > 0:
        print(f"{comparison['icma_only']} additional bonds meet ICMA criteria but not CBI (older issues or")
        print(f"  different environmental focuses)")


def example_6_real_data():
    """Example 6: Processing actual data file."""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Processing Real Data File")
    print("=" * 80)
    
    # Load the actual data file
    data_file = project_root / 'data' / 'green_bonds_authentic.csv'
    
    if not data_file.exists():
        print(f"\nData file not found: {data_file}")
        print("Please ensure the data file exists before running this example.")
        return
    
    print(f"\nLoading data from: {data_file}")
    df = pd.read_csv(data_file)
    
    print(f"Loaded {len(df)} bonds")
    
    # Extract both certifications
    df_cbi = extract_cbi_certification(df)
    df_icma = extract_icma_certification(df_cbi)
    
    # Get validation results
    validation = validate_icma_data(df)
    
    # Compute statistics
    cbi_stats = compute_cbi_stats(df_cbi)
    icma_stats = compute_icma_stats(df_icma)
    comparison = compare_cbi_vs_icma(df_icma)
    
    # Display results
    print("\n" + "─" * 80)
    print("COMPREHENSIVE CERTIFICATION ANALYSIS")
    print("─" * 80)
    
    print(f"\nDATA QUALITY ASSESSMENT:")
    print(f"  Date coverage:                {validation['date_coverage']}%")
    print(f"  Use of Proceeds coverage:     {validation['use_of_proceeds_coverage']}%")
    print(f"  Offering Technique coverage:  {validation['offering_technique_coverage']}%")
    print(f"  Post-2014 bonds:              {validation['post_2014_pct']}%")
    print(f"  Bonds with GBP purposes:      {validation['gbp_purposes_pct']}%")
    
    print(f"\nCBI CERTIFICATION RESULTS:")
    print(f"  Total bonds:                  {cbi_stats['total']}")
    print(f"  CBI certified:                {cbi_stats['cbi_certified']}")
    print(f"  Coverage:                     {cbi_stats['coverage_pct']}%")
    
    print(f"\nICMA CERTIFICATION RESULTS:")
    print(f"  Total bonds:                  {icma_stats['total']}")
    print(f"  ICMA certified:               {icma_stats['icma_certified']}")
    print(f"  Coverage:                     {icma_stats['coverage_pct']}%")
    print(f"  Average confidence:           {icma_stats['avg_confidence']}")
    
    print(f"\nCONFIDENCE DISTRIBUTION:")
    for level, count in icma_stats['confidence_distribution'].items():
        pct = round((count / icma_stats['total'] * 100), 1)
        print(f"  {level:10s}: {count:3d} bonds ({pct:6.1f}%)")
    
    print(f"\nCERT IFICATION COMPARISON:")
    print(f"  Both CBI & ICMA:              {comparison['both']} bonds")
    print(f"  CBI only:                     {comparison['cbi_only']} bonds")
    print(f"  ICMA only:                    {comparison['icma_only']} bonds")
    print(f"  Neither:                      {comparison['neither']} bonds")
    print(f"  Overlap (ICMA of CBI):        {comparison['overlap_pct']}%")
    
    print(f"\nSAMPLE ICMA CERTIFIED BONDS:")
    print(f"─" * 80)
    icma_certified = df_icma[df_icma['is_icma_certified'] == 1].head(5)
    for idx, row in icma_certified.iterrows():
        print(f"  • {row['Issuer/Borrower Name Full']}")
        print(f"    Date: {row['Dates: Issue Date']}, Purpose: {row['Primary Use Of Proceeds']}")
        print(f"    Confidence: {row['icma_confidence']:.2f}, Technique: {row['Offering Technique']}")
    
    print(f"\nSAMPLE NON-CERTIFIED BONDS:")
    print(f"─" * 80)
    non_certified = df_icma[df_icma['is_icma_certified'] == 0].head(5)
    for idx, row in non_certified.iterrows():
        print(f"  • {row['Issuer/Borrower Name Full']}")
        print(f"    Date: {row['Dates: Issue Date']}, Purpose: {row['Primary Use Of Proceeds']}")
        print(f"    Confidence: {row['icma_confidence']:.2f}")
    
    # Save results
    output_file = project_root / 'processed_data' / 'bonds_with_icma_certification.csv'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df_icma.to_csv(output_file, index=False)
    print(f"\n✓ Results saved to: {output_file}")


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("ICMA GREEN BOND PRINCIPLES CERTIFICATION - USAGE EXAMPLES")
    print("=" * 80)
    
    # Run examples
    example_1_icma_basic_extraction()
    example_2_icma_confidence_scores()
    example_3_icma_statistics()
    example_4_data_validation()
    example_5_cbi_vs_icma_comparison()
    example_6_real_data()
    
    print("\n" + "=" * 80)
    print("Examples completed!")
    print("=" * 80 + "\n")


if __name__ == '__main__':
    main()
