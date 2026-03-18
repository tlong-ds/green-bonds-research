"""
Test LSEG identifier resolution for green bond DealPermIds.

This script tests which of the 333 DealPermId identifiers actually resolve in LSEG.
It tries both numeric and string formats and tests a sample from the dataset.
"""

import pandas as pd
import sys
import traceback
from typing import List, Tuple, Dict

def load_identifiers(csv_path: str) -> List[str]:
    """Load DealPermId identifiers from CSV."""
    try:
        df = pd.read_csv(csv_path)
        if 'Deal PermID' in df.columns:
            identifiers = df['Deal PermID'].unique().tolist()
        else:
            raise ValueError("'Deal PermID' column not found")
        return [str(uid) for uid in identifiers if pd.notna(uid)]
    except Exception as e:
        print(f"Error loading identifiers: {e}")
        return []

def test_lseg_identifiers_sample(identifiers: List[str], sample_size: int = 20) -> Dict:
    """
    Test identifier resolution with LSEG API.
    
    Args:
        identifiers: List of DealPermId values (as strings)
        sample_size: Number to test
        
    Returns:
        Dictionary with test results
    """
    
    results = {
        'total_identifiers': len(identifiers),
        'sample_size': min(sample_size, len(identifiers)),
        'tested': [],
        'resolved': [],
        'failed': [],
        'errors': {}
    }
    
    sample_ids = identifiers[:results['sample_size']]
    
    try:
        import refinitiv.data as rd
        
        # Check if session is already open
        try:
            rd.get_session()
            print("✓ Existing LSEG session detected")
        except:
            print("Opening LSEG session...")
            try:
                rd.open_session()
                print("✓ Session opened")
                session_opened = True
            except Exception as e:
                print(f"✗ Cannot open LSEG session: {e}")
                print("  LSEG Workspace may not be running")
                return results
        
        # Test with string identifiers
        print(f"\nTesting {len(sample_ids)} sample identifiers with LSEG API...")
        print(f"Sample IDs: {sample_ids[:5]}...")
        
        # Try a simple get_data call to test resolution
        try:
            print(f"\nAttempting to query {len(sample_ids)} identifiers...")
            
            # Use get_data with a simple field that should be available
            data, err = rd.get_data(
                identifiers=sample_ids,
                fields=['TR.DealPermId'],
                raw_output=True
            )
            
            if err is not None and err.error_code != 0:
                print(f"API Error: {err.error_code} - {err.message}")
                results['errors']['api_error'] = f"{err.error_code}: {err.message}"
            
            if data is not None:
                # Check which identifiers were resolved
                data_dict = data.D
                if data_dict:
                    for identifier, values in data_dict.items():
                        results['tested'].append(identifier)
                        if values and len(values) > 0:
                            results['resolved'].append(identifier)
                        else:
                            results['failed'].append(identifier)
                else:
                    results['errors']['empty_response'] = "API returned no data"
                    
        except Exception as e:
            results['errors']['query_error'] = str(e)
            print(f"✗ Query error: {e}")
            traceback.print_exc()
            
    except ImportError:
        print("✗ refinitiv.data not installed")
        results['errors']['import_error'] = "refinitiv.data library not available"
        
        # Try alternative: provide diagnostic information
        print("\nDiagnostic Info:")
        print("  - Cannot test LSEG API without refinitiv.data")
        print("  - Install with: pip install refinitiv.data")
        print(f"  - Total identifiers to test: {len(identifiers)}")
        print(f"  - Sample identifiers: {sample_ids}")
    
    return results

def analyze_identifier_format(identifiers: List[str]) -> Dict:
    """Analyze the format and characteristics of identifiers."""
    analysis = {
        'total': len(identifiers),
        'min': min(int(x) for x in identifiers if x),
        'max': max(int(x) for x in identifiers if x),
        'avg_length': sum(len(x) for x in identifiers) / len(identifiers),
        'unique_lengths': set(len(x) for x in identifiers),
        'sample': identifiers[:10]
    }
    return analysis

def main():
    csv_path = 'data/green_bonds_authentic.csv'
    
    print("=" * 70)
    print("LSEG Identifier Resolution Test")
    print("=" * 70)
    
    # Load identifiers
    print(f"\n[1/3] Loading identifiers from {csv_path}...")
    identifiers = load_identifiers(csv_path)
    
    if not identifiers:
        print("✗ No identifiers loaded")
        sys.exit(1)
    
    print(f"✓ Loaded {len(identifiers)} unique identifiers")
    
    # Analyze format
    print(f"\n[2/3] Analyzing identifier format...")
    analysis = analyze_identifier_format(identifiers)
    print(f"  - Total: {analysis['total']}")
    print(f"  - Min value: {analysis['min']}")
    print(f"  - Max value: {analysis['max']}")
    print(f"  - Avg length: {analysis['avg_length']:.1f}")
    print(f"  - Unique lengths: {sorted(analysis['unique_lengths'])}")
    print(f"  - Sample: {analysis['sample']}")
    
    # Test with LSEG API
    print(f"\n[3/3] Testing identifier resolution with LSEG API...")
    results = test_lseg_identifiers_sample(identifiers, sample_size=20)
    
    # Print results
    print("\n" + "=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
    print(f"Total identifiers in dataset: {results['total_identifiers']}")
    print(f"Sample tested: {results['sample_size']}")
    print(f"Resolved: {len(results['resolved'])}")
    print(f"Failed: {len(results['failed'])}")
    
    if results['resolved']:
        print(f"\nResolved identifiers:")
        for identifier in results['resolved'][:5]:
            print(f"  ✓ {identifier}")
        if len(results['resolved']) > 5:
            print(f"  ... and {len(results['resolved']) - 5} more")
    
    if results['failed']:
        print(f"\nFailed identifiers:")
        for identifier in results['failed'][:5]:
            print(f"  ✗ {identifier}")
        if len(results['failed']) > 5:
            print(f"  ... and {len(results['failed']) - 5} more")
    
    if results['errors']:
        print(f"\nErrors encountered:")
        for error_type, error_msg in results['errors'].items():
            print(f"  - {error_type}: {error_msg}")
    
    # Try alternative formats if resolution failed
    if not results['resolved'] and not results['errors'].get('import_error'):
        print("\n" + "=" * 70)
        print("TROUBLESHOOTING")
        print("=" * 70)
        print("Identifiers may need format conversion. Common alternatives:")
        print("  1. ISIN format")
        print("  2. RIC codes")
        print("  3. CUSIP or other identifiers")
        print("  4. Package Identifier from the dataset")

if __name__ == '__main__':
    main()
