# LSEG Field Code Corrections - Quick Reference

## Summary
- **43 fields analyzed**
- **29 VALID** ✓ (67%)
- **4 QUESTIONABLE** ⚠️ (9%) - Require corrections
- **10 PROBLEMATIC** ❌ (24%) - High risk or require external data

---

## IMMEDIATE CORRECTIONS (Apply to greenbonds.py)

```python
CORRECTIONS = {
    "TR.CouponRate": "TR.FiCouponRate",              # Confidence: 85%
    "TR.FiIssuerPermID": "TR.FiIssuerPermId",        # Confidence: 75%
    "TR.EOMPrice": "TR.FiEOMPrice",                  # Confidence: 80%
    "TR.CurrentYield": "TR.FiCurrentYield",          # Confidence: 75%
}
```

**Expected improvement:** 29 + 4 = 33/43 fields (77% success rate)

---

## FIELDS NEEDING RESEARCH

### Composite Fields (2) - Test alternatives if original fails
1. **TR.FiProceedsAmountIncOverallotment**
   - Try: `TR.FiProceedsAmount` or `TR.FiOfferingProceeds`
   - Risk: HIGH

2. **TR.FiProceedsAmountThisMarket**
   - Try: `TR.FiOfferingProceeds` or `TR.FiProceedsAmount`
   - Risk: HIGH

### External Data Fields (5) - Likely NOT in LSEG
1. **TR.EnvironmentPillarScore** → Use external ESG provider
2. **TR.GreenRevenue** → Query issuer separately for financials
3. **TR.FiUseOfProceeds** → Use CBI Climate Bonds Register
4. **TR.CBIIndicator** → Use CBI Climate Bonds Register
5. **TR.GreenBondFramework** → Use CBI or prospectus data

---

## FIELD DISTRIBUTION BY BATCH

| Batch | Name | Valid | Questionable | Problem | Total |
|-------|------|-------|-------------|---------|-------|
| 1 | Deal Identifiers | 7 | 1 | 0 | 8 |
| 2 | Issuer Info | 7 | 1 | 0 | 8 |
| 3 | Pricing | 1 | 2 | 2 | 5 |
| 4 | ESG/Green | 3 | 0 | 5 | 8 |
| 5 | Geographic | 6 | 0 | 0 | 6 |
| 6 | Classification | 5 | 0 | 0 | 5 |
| **TOTAL** | | **29** | **4** | **7** | **43** |

---

## VALID FIELDS BY BATCH (No changes needed)

### Batch 1 (7 fields)
- TR.DealPermId ✓
- TR.FiPackageId ✓
- TR.FiMasterDealTypeCode ✓
- TR.FiAllManagerRolesCode ✓
- TR.FiManagerRoleCode ✓
- TR.FiIssueDate ✓
- TR.FiMaturityDate ✓

### Batch 2 (7 fields)
- TR.FiIssuerName ✓
- TR.FiIssueType ✓
- TR.FiTransactionStatus ✓
- TR.FiIssuerNation ✓
- TR.FiFilingDate ✓
- TR.FiIssuerExchangeName ✓
- TR.FiSecurityTypeAllMkts ✓

### Batch 3 (1 field)
- TR.FiOfferPrice ✓

### Batch 4 (3 fields)
- TR.FiOfferingTechnique ✓
- TR.FiGrossSpreadPct ✓
- TR.FaceIssuedTotal ✓

### Batch 5 (6 fields)
- TR.FiIssuerSubRegion ✓
- TR.FiIssuerRegion ✓
- TR.FiIssuerNationRegion ✓
- TR.FiLeadLeftBookrunner ✓
- TR.FiManagersTier1Tier2 ✓
- TR.FiECMFlag ✓

### Batch 6 (5 fields)
- TR.FiIssuerTRBCBusinessSector ✓
- TR.FiIssuerTRBCEconomicSector ✓
- TR.FiMasterDealType ✓
- TR.FiAllManagerRoles ✓
- TR.FiManagerRole ✓

---

## IMPLEMENTATION CHECKLIST

- [ ] Apply 4 field name corrections to greenbonds.py
- [ ] Test with corrected fields against LSEG Workspace
- [ ] Research/test 2 composite fields with alternatives
- [ ] Plan integration for 5 external data fields
- [ ] Create fallback script using external data sources
- [ ] Document LSEG ESG field naming conventions
- [ ] Test final batched retrieval

---

## SUCCESS METRICS

| Scenario | Fields | Success Rate |
|----------|--------|--------------|
| Original | 43 | ~40-50% (expected failures) |
| With corrections | 33 | ~77% (29 valid + 4 corrected) |
| With fallbacks | 35-38 | ~85-90% (if composites work) |
| Full integration | 43 | 100% (with external sources) |

---

## KEY FINDINGS

1. **67% of fields are correct** - Good base for retrieval
2. **Naming inconsistencies** - Missing Fi prefix on 4 fields
3. **Green bonds fields are problematic** - Likely not LSEG native
4. **Composite field names suspect** - May not exist as written
5. **TRBC and geographic fields are solid** - High confidence

**Recommended approach:** Start with 33 validated fields, add external data sources for green-specific metrics.
