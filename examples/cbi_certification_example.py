"""
Example usage of CBI (Climate Bonds Initiative) certification functions.

This script demonstrates how to use the authenticity module to extract,
validate, and compute statistics on CBI certification for green bonds.
"""

import pandas as pd
from pathlib import Path
import sys

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from asean_green_bonds.authenticity import (
    extract_cbi_certification,
    compute_cbi_stats,
    validate_cbi_data
)


def example_1_basic_extraction():
    """Example 1: Basic CBI certification extraction."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic CBI Certification Extraction")
    print("=" * 70)
    
    # Create sample data
    data = {
        'Bond ID': ['BOND001', 'BOND002', 'BOND003', 'BOND004'],
        'Issuer': ['Company A', 'Company B', 'Company C', 'Company D'],
        'Primary Use Of Proceeds': [
            'Green Bond Purposes',
            'Environmental Protection Proj.',
            'Green Bond Purposes',
            'Green Construction'
        ]
    }
    df = pd.DataFrame(data)
    
    print("\nOriginal DataFrame:")
    print(df)
    
    # Extract CBI certification
    df_certified = extract_cbi_certification(df)
    
    print("\nDataFrame with CBI certification:")
    print(df_certified[['Bond ID', 'Primary Use Of Proceeds', 'is_cbi_certified']])


def example_2_statistics():
    """Example 2: Computing CBI statistics."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Computing CBI Statistics")
    print("=" * 70)
    
    # Create sample data
    data = {
        'Primary Use Of Proceeds': ['Green Bond Purposes'] * 80 + 
                                   ['Environmental Protection Proj.'] * 15 +
                                   ['Green Construction'] * 5
    }
    df = pd.DataFrame(data)
    df_certified = extract_cbi_certification(df)
    
    # Compute statistics
    stats = compute_cbi_stats(df_certified)
    
    print(f"\nTotal bonds:              {stats['total']}")
    print(f"CBI certified:            {stats['cbi_certified']}")
    print(f"Not certified:            {stats['not_certified']}")
    print(f"CBI coverage percentage:  {stats['coverage_pct']}%")


def example_3_data_validation():
    """Example 3: Validating CBI data quality."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Data Validation and Quality Checks")
    print("=" * 70)
    
    # Create sample data with some quality issues
    data = {
        'Bond ID': ['BOND001', 'BOND002', 'BOND003', 'BOND004', 'BOND005'],
        'Primary Use Of Proceeds': [
            'Green Bond Purposes',
            'Green Bond Purposes',
            None,
            'Environmental Protection Proj.',
            'Green Construction'
        ]
    }
    df = pd.DataFrame(data)
    
    # Validate
    validation = validate_cbi_data(df)
    
    print("\nData Validation Results:")
    print(f"Missing values: {validation['missing_count']}")
    print(f"Unique values: {len(validation['unique_values'])}")
    print("\nValue counts:")
    for value, count in validation['value_counts'].items():
        print(f"  {value}: {count}")
    print("\nData quality assessment:")
    for issue in validation['issues']:
        print(f"  - {issue}")


def example_4_real_data():
    """Example 4: Working with actual data file."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Processing Real Data File")
    print("=" * 70)
    
    # Load the actual data file
    data_file = project_root / 'data' / 'green_bonds_authentic.csv'
    
    if not data_file.exists():
        print(f"\nData file not found: {data_file}")
        print("Please ensure the data file exists before running this example.")
        return
    
    print(f"\nLoading data from: {data_file}")
    df = pd.read_csv(data_file)
    
    print(f"Loaded {len(df)} bonds")
    
    # Extract CBI certification
    df_certified = extract_cbi_certification(df)
    
    # Get validation results
    validation = validate_cbi_data(df)
    
    # Compute statistics
    stats = compute_cbi_stats(df_certified)
    
    # Display results
    print("\n--- CBI CERTIFICATION ANALYSIS ---")
    print(f"Total bonds:               {stats['total']}")
    print(f"CBI certified:             {stats['cbi_certified']}")
    print(f"Coverage:                  {stats['coverage_pct']}%")
    print(f"\nData quality:")
    print(f"  Missing values: {validation['missing_count']}")
    print(f"  Status: {validation['issues'][0]}")
    
    # Show sample
    print("\nSample of certified bonds:")
    sample = df_certified[df_certified['is_cbi_certified'] == 1].head(3)
    if len(sample) > 0:
        for idx, row in sample.iterrows():
            print(f"  - {row['Issuer/Borrower Name Full']}: {row['Primary Use Of Proceeds']}")


def example_5_filtering_and_analysis():
    """Example 5: Filtering and analysis by certification status."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Filtering and Analysis by Certification Status")
    print("=" * 70)
    
    # Create sample data
    data = {
        'Issuer': ['Company A', 'Company B', 'Company C', 'Company D', 'Company E'],
        'Amount (USD M)': [100, 150, 200, 75, 125],
        'Primary Use Of Proceeds': [
            'Green Bond Purposes',
            'Green Bond Purposes',
            'Environmental Protection Proj.',
            'Green Bond Purposes',
            'Waste and Pollution Control'
        ]
    }
    df = pd.DataFrame(data)
    df_certified = extract_cbi_certification(df)
    
    print("\nOriginal data:")
    print(df)
    
    # Analyze certified vs non-certified
    certified = df_certified[df_certified['is_cbi_certified'] == 1]
    non_certified = df_certified[df_certified['is_cbi_certified'] == 0]
    
    print("\n--- CBI Certified Bonds ---")
    print(f"Count: {len(certified)}")
    print(f"Total amount: ${certified['Amount (USD M)'].sum()}M")
    print(f"Average amount: ${certified['Amount (USD M)'].mean():.2f}M")
    
    print("\n--- Non-CBI Bonds ---")
    print(f"Count: {len(non_certified)}")
    print(f"Total amount: ${non_certified['Amount (USD M)'].sum()}M")
    if len(non_certified) > 0:
        print(f"Average amount: ${non_certified['Amount (USD M)'].mean():.2f}M")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("CBI CERTIFICATION FUNCTIONS - USAGE EXAMPLES")
    print("=" * 70)
    
    # Run examples
    example_1_basic_extraction()
    example_2_statistics()
    example_3_data_validation()
    example_4_real_data()
    example_5_filtering_and_analysis()
    
    print("\n" + "=" * 70)
    print("Examples completed!")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
