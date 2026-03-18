# Green Bonds LSEG Data Retrieval

## Overview

`greenbonds.py` is a refactored script that retrieves comprehensive green bond data from the LSEG (Refinitiv) database using the Desktop API. It implements batched field retrieval to avoid API overload errors and consolidates results into a single CSV file.

## Features

✓ **Batched retrieval** - Splits 43 fields into 6 logical batches (10-15 fields each)  
✓ **Automatic universe loading** - Extracts bond identifiers from existing data  
✓ **Error handling** - Gracefully handles API errors and continues with remaining batches  
✓ **Time delays** - 1.5-second delays between batch requests to prevent server overload  
✓ **Consolidation** - Merges multiple batch results into single DataFrame  
✓ **Quality reporting** - Provides data quality summary (record count, fields, memory usage, missing values)

## Prerequisites

1. **LSEG Workspace** must be running (Desktop API requirement)
2. **Python dependencies** installed:
   - `refinitiv.data`
   - `pandas`
3. **Existing data file** at `/data/green_bonds_authentic.csv` (recommended for universe loading)

## Usage

```bash
python greenbonds.py
```

The script will:
1. Open an LSEG Workspace session
2. Load bond identifiers from existing data
3. Execute 6 sequential batch requests (each with 1.5s delay)
4. Consolidate results
5. Save to `/data/green_bonds_lseg_full.csv`
6. Close the session

## Field Batches

### Batch 1: Deal Identifiers & Basic Info (8 fields)
- TR.DealPermId, TR.FiPackageId, TR.FiMasterDealTypeCode
- TR.FiAllManagerRolesCode, TR.FiManagerRoleCode
- TR.FiIssueDate, TR.FiMaturityDate, TR.CouponRate

### Batch 2: Issuer Info & Classification (8 fields)
- TR.FiIssuerName, TR.FiIssuerPermID, TR.FiIssueType
- TR.FiTransactionStatus, TR.FiIssuerNation, TR.FiFilingDate
- TR.FiIssuerExchangeName, TR.FiSecurityTypeAllMkts

### Batch 3: Pricing & Proceeds (5 fields)
- TR.FiOfferPrice, TR.FiProceedsAmountIncOverallotment
- TR.FiProceedsAmountThisMarket, TR.EOMPrice, TR.CurrentYield

### Batch 4: ESG & Green Bond Specific (8 fields)
- TR.EnvironmentPillarScore, TR.GreenRevenue
- TR.FiUseOfProceeds, TR.CBIIndicator, TR.GreenBondFramework
- TR.FiOfferingTechnique, TR.FiGrossSpreadPct, TR.FaceIssuedTotal

### Batch 5: Market & Geographic Info (6 fields)
- TR.FiIssuerSubRegion, TR.FiIssuerRegion, TR.FiIssuerNationRegion
- TR.FiLeadLeftBookrunner, TR.FiManagersTier1Tier2, TR.FiECMFlag

### Batch 6: Sector & Classification (5 fields)
- TR.FiIssuerTRBCBusinessSector, TR.FiIssuerTRBCEconomicSector
- TR.FiMasterDealType, TR.FiAllManagerRoles, TR.FiManagerRole

**Total: 43 fields across 6 batches**

## Output

The script produces:
- **File**: `/data/green_bonds_lseg_full.csv`
- **Format**: CSV with headers (one row per record, one column per field)
- **Quality metrics**: Printed summary with record count, field count, memory usage, missing values

## Error Handling

- **Session errors**: Script exits if LSEG Workspace is not running
- **Data loading errors**: Script continues with empty universe if reference file not found
- **Batch errors**: Individual batch failures don't stop subsequent batches
- **Missing fields**: Fields unavailable for specific identifiers result in NaN values

## Configuration

To modify the script:
- **Batch size**: Edit `field_batches` dictionary to adjust field grouping
- **Delay interval**: Change `time.sleep(1.5)` to adjust delay between requests
- **Input universe**: Modify the universe loading logic to use different source
- **Output path**: Change `'data/green_bonds_lseg_full.csv'` to different location

## Notes

- Universe loading automatically falls back to first column if DealPermId not found
- Each batch request includes the full universe of identifiers
- Results are merged on DataFrame index (typically contains identifiers)
- No data manipulation is performed - output is raw LSEG data
- Memory usage scales with number of identifiers × number of fields

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Session not open" | Ensure LSEG Workspace is running |
| "Field not available" | Some fields may not be available for all instruments (NaN values expected) |
| "Unable to handle requests" | Script handles this by batching - all 43 fields are split across 6 requests |
| Empty universe | Check `/data/green_bonds_authentic.csv` exists and has valid identifiers |
| Large memory usage | Reduce universe size or split output into smaller time ranges |

## Data Validation

Before using output data, verify:
1. Row count matches expected number of identifiers
2. Key fields (DealPermId, FiIssuerName, FiIssueDate) are populated
3. Missing value pattern is reasonable (should be sparse)
4. Field types are appropriate (dates, numbers, text)

## References

- LSEG Refinitiv Data API: https://developers.refinitiv.com/
- Green Bond Framework: https://www.icmagroup.org/green-social-and-sustainability-bonds/
- ASEAN Green Bonds Research: See project documentation
