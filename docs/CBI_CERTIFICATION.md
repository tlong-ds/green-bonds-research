# CBI Certification Logic for Green Bonds

## Overview

This document describes the CBI (Climate Bonds Initiative) certification extraction and computation logic for green bonds in the ASEAN Green Bonds research project.

## What is CBI Certification?

CBI (Climate Bonds Initiative) is an international, non-profit organization working to mobilize capital for climate solutions. CBI-certified green bonds are securities that have been independently verified to meet the Climate Bonds Standard.

In this dataset, CBI certification can be inferred from the **"Primary Use Of Proceeds"** field:
- Bonds labeled with `"Green Bond Purposes"` are **CBI-certified**
- All other categories are **not CBI-certified**

## Data Source

**File:** `/Users/bunnypro/Projects/refinitiv-search/data/green_bonds_authentic.csv`

**Column:** `Primary Use Of Proceeds`

## Current Statistics

As of the latest analysis:

| Metric | Value |
|--------|-------|
| Total bonds | 333 |
| CBI certified | 328 |
| Not certified | 5 |
| Coverage | 98.50% |

### Breakdown of Non-CBI Values

| Category | Count |
|----------|-------|
| Green Bond Purposes (CBI) | 328 |
| Environmental Protection Proj. | 3 |
| Green Construction | 1 |
| Waste and Pollution Control | 1 |

## Implementation

### Module: `asean_green_bonds/authenticity.py`

The CBI certification logic is implemented in the `authenticity` module with three main functions:

#### 1. `extract_cbi_certification(df, column="Primary Use Of Proceeds")`

Extracts and computes the CBI certification indicator.

**Parameters:**
- `df` (pd.DataFrame): DataFrame containing bond data
- `column` (str, optional): Name of the Primary Use Of Proceeds column

**Returns:**
- `pd.DataFrame`: DataFrame with new `is_cbi_certified` column (0 or 1)

**Behavior:**
- Bonds with "Green Bond Purposes" are marked as `1` (certified)
- All other values are marked as `0` (not certified)
- Null/missing values are treated as `0` (not certified)

**Example:**
```python
import pandas as pd
from asean_green_bonds.authenticity import extract_cbi_certification

df = pd.read_csv('green_bonds_authentic.csv')
df_certified = extract_cbi_certification(df)

print(df_certified['is_cbi_certified'].value_counts())
# Output:
# 1    328
# 0      5
```

#### 2. `compute_cbi_stats(df, cbi_column="is_cbi_certified")`

Computes summary statistics about CBI certification in the dataset.

**Parameters:**
- `df` (pd.DataFrame): DataFrame with CBI certification indicator column
- `cbi_column` (str, optional): Name of the certification column

**Returns:**
- `dict`: Dictionary with keys:
  - `total`: Total number of bonds
  - `cbi_certified`: Number of CBI-certified bonds
  - `not_certified`: Number of non-certified bonds
  - `coverage_pct`: Percentage of CBI-certified bonds (rounded to 2 decimals)

**Example:**
```python
stats = compute_cbi_stats(df_certified)
print(f"Coverage: {stats['coverage_pct']}%")
# Output: Coverage: 98.50%
```

#### 3. `validate_cbi_data(df, primary_use_col="Primary Use Of Proceeds")`

Validates the CBI certification data for completeness and quality issues.

**Parameters:**
- `df` (pd.DataFrame): DataFrame containing bond data
- `primary_use_col` (str, optional): Name of the Primary Use Of Proceeds column

**Returns:**
- `dict`: Dictionary with keys:
  - `missing_count`: Number of null values
  - `unique_values`: List of unique values in the column
  - `value_counts`: Dictionary of value counts
  - `issues`: List of data quality issues (or "No issues detected")

**Example:**
```python
validation = validate_cbi_data(df)
print(f"Missing values: {validation['missing_count']}")
print(f"Issues: {validation['issues']}")
# Output:
# Missing values: 0
# Issues: ['No issues detected']
```

## Integration with Existing Code

The existing `loader.py` module already implements CBI certification extraction using inline code:

```python
gb['is_certified'] = gb['Primary Use Of Proceeds'].eq('Green Bond Purposes').astype(int)
```

The new `authenticity.py` module provides:
1. **Clearer naming**: `is_cbi_certified` vs `is_certified`
2. **Reusability**: Dedicated functions for extraction, statistics, and validation
3. **Documentation**: Comprehensive docstrings and validation logic
4. **Testing**: 21 comprehensive unit tests covering edge cases

Both approaches produce identical results and can be used interchangeably.

## Testing

Comprehensive unit tests are included in `tests/test_authenticity.py`:

**Test Coverage:**
- Basic extraction and value handling
- Null/missing value handling
- Edge cases (all certified, none certified, empty DataFrame)
- Statistics computation with various scenarios
- Data validation and issue detection
- Integration tests with realistic data

**Run Tests:**
```bash
pytest tests/test_authenticity.py -v
```

**Test Results:**
```
tests/test_authenticity.py::TestExtractCBICertification::test_basic_extraction PASSED
tests/test_authenticity.py::TestExtractCBICertification::test_all_certified PASSED
tests/test_authenticity.py::TestExtractCBICertification::test_none_certified PASSED
tests/test_authenticity.py::TestExtractCBICertification::test_null_handling PASSED
tests/test_authenticity.py::TestExtractCBICertification::test_custom_column_name PASSED
tests/test_authenticity.py::TestExtractCBICertification::test_dataframe_not_modified PASSED
tests/test_authenticity.py::TestExtractCBICertification::test_output_dtype PASSED
tests/test_authenticity.py::TestComputeCBIStats::test_basic_stats PASSED
tests/test_authenticity.py::TestComputeCBIStats::test_all_certified_stats PASSED
tests/test_authenticity.py::TestComputeCBIStats::test_none_certified_stats PASSED
tests/test_authenticity.py::TestComputeCBIStats::test_empty_dataframe_stats PASSED
tests/test_authenticity.py::TestComputeCBIStats::test_custom_column_name_stats PASSED
tests/test_authenticity.py::TestComputeCBIStats::test_coverage_precision PASSED
tests/test_authenticity.py::TestValidateCBIData::test_complete_data_validation PASSED
tests/test_authenticity.py::TestValidateCBIData::test_missing_values_detection PASSED
tests/test_authenticity.py::TestValidateCBIData::test_value_counts PASSED
tests/test_authenticity.py::TestValidateCBIData::test_unique_values PASSED
tests/test_authenticity.py::TestValidateCBIData::test_custom_column_validation PASSED
tests/test_authenticity.py::TestValidateCBIData::test_all_expected_values PASSED
tests/test_authenticity.py::TestIntegration::test_end_to_end_workflow PASSED
tests/test_authenticity.py::TestIntegration::test_with_real_data_shape PASSED

21 passed in 0.61s
```

## Data Quality Notes

### Complete Coverage
- **No missing values** in the "Primary Use Of Proceeds" column
- All 333 bonds have valid category assignments

### Non-CBI Certified Bonds (5 total)
These bonds are not certified as "Green Bond Purposes" but still represent green finance:
1. **Environmental Protection Proj.** (3 bonds): Focus on environmental protection infrastructure
2. **Green Construction** (1 bond): Focus on green building practices
3. **Waste and Pollution Control** (1 bond): Focus on waste management and pollution mitigation

These may represent green bonds that don't meet the strict Climate Bonds Standard but still serve environmental purposes.

## Usage Recommendations

### For Data Analysis
```python
from asean_green_bonds.authenticity import extract_cbi_certification, compute_cbi_stats

df = pd.read_csv('green_bonds_authentic.csv')
df = extract_cbi_certification(df)
stats = compute_cbi_stats(df)

print(f"CBI Coverage: {stats['coverage_pct']}%")
```

### For Data Validation
```python
from asean_green_bonds.authenticity import validate_cbi_data

validation = validate_cbi_data(df)
if validation['missing_count'] > 0:
    print(f"Warning: {validation['missing_count']} missing values found")
```

### For Reports
```python
from asean_green_bonds.authenticity import compute_cbi_stats

stats = compute_cbi_stats(df)
print(f"Total bonds analyzed: {stats['total']}")
print(f"CBI certified: {stats['cbi_certified']} ({stats['coverage_pct']}%)")
```

## References

- Climate Bonds Initiative: https://www.climatebonds.net/
- Climate Bonds Standard: https://www.climatebonds.net/standard
- ASEAN Green Bonds Research Project: `/Users/bunnypro/Projects/refinitiv-search`

## Related Files

- Implementation: `asean_green_bonds/authenticity.py`
- Tests: `tests/test_authenticity.py`
- Data: `data/green_bonds_authentic.csv`
- Existing code: `asean_green_bonds/data/loader.py` (lines 149-151)
