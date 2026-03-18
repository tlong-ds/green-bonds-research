# Green Bond Authenticity Verification Methodology

## Overview

This document describes the comprehensive authenticity verification system for ASEAN green bonds (2015-2025). The system uses a **three-pillar approach** combining green bond certifications, ESG performance metrics, and issuer credibility to assess bond authenticity.

## Key Files

- **Primary Output**: `data/green_bonds_authenticated.csv` (333 bonds × 64 columns)
- **Consolidated Data**: `data/consolidated_authenticity_attributes.csv` (333 bonds × 59 columns)
- **Sample Data**: `data/issuer_fields_sample.csv`

## Executive Summary

| Metric | Value | Interpretation |
|--------|-------|-----------------|
| **Total Bonds** | 333 | ASEAN green bonds 2015-2025 |
| **CBI Certified** | 328 (98.5%) | Meet Climate Bonds Initiative standards |
| **ICMA Certified** | 326 (97.9%) | Align with ICMA Green Bond Principles |
| **ESG Authentic** | 13 (3.9%) | Show statistically significant ESG improvement |
| **Mean Authenticity Score** | 53.81 (0-100) | Mostly Low authenticity, few High |

## Three-Pillar Framework

### Pillar 1: Green Bond Certification (35% weight)

#### CBI (Climate Bonds Initiative) Certification

**Definition**: Bonds marked as "Green Bond Purposes" in the Primary Use of Proceeds field indicate CBI alignment.

**Coverage**: 328/333 bonds (98.5%)

**Interpretation**:
- ✅ Certified: Bond explicitly declared for environmental purposes
- ❌ Not Certified: Other purposes (environmental protection, waste, construction)

**Data Source**: LSEG green_bonds_authentic.csv, "Primary Use Of Proceeds" column

#### ICMA (International Capital Market Association) Certification

**Definition**: Heuristic scoring based on ICMA Green Bond Principles alignment:
- Post-2014 issuance (+0.5 points)
- "Green Bond Purposes" designation (+0.4 points)
- Environmental focus (+0.1 points)
- Threshold: ≥ 0.7 for certification

**Coverage**: 326/333 bonds (97.9%)
**Average Confidence**: 0.891 (High)

**Interpretation**:
- High confidence (≥0.9): 326 bonds - Reliable ICMA alignment
- Medium confidence (0.7-0.89): 0 bonds
- Low confidence (<0.7): 7 bonds - May not align with ICMA standards

### Pillar 2: ESG Performance (40% weight)

#### ESG Divergence Method (Difference-in-Differences)

**Definition**: Statistical test comparing pre-vs-post issuance ESG scores to detect "greenwashing" (false environmental improvement claims).

**Methodology**:
1. Extract issuer's ESG score from year before issuance (pre-window)
2. Extract issuer's ESG score from year after issuance (post-window)
3. Calculate mean difference: `esg_improvement = post_mean - pre_mean`
4. Run t-test: `p_value = ttest(pre_scores, post_scores)`
5. Flag as authentic if `p_value < 0.10` AND `esg_improvement > 0`

**Coverage**:
- Complete ESG data: 25/333 bonds (7.5%)
- Insufficient ESG data: 24/333 bonds (7.2%)
- No ESG data: 284/333 bonds (85.3%)

**Results**:
- **Authentic** (p<0.10, improvement>0): 13 bonds (3.9%)
- **Unverified** (insufficient data or no improvement): 320 bonds (96.1%)

**Key Authentic Issuers**:
1. **BTS Group Holdings** (Bangkok Mass Transit): +29.59 pts (p=0.005)
2. **Energy Absolute** (Renewable energy): +31.68 pts (p=0.023)
3. **PTT** (Energy transition): +4.27 pts (p=0.034)

**Interpretation**:
- ✅ ESG improvement > 10 pts with p<0.10: Strong authenticity signal
- ⚠️ Small improvement (0-10 pts): Weak signal, needs other verification
- ❌ ESG decline or no data: Cannot verify authenticity via ESG

### Pillar 3: Issuer Verification (25% weight)

#### Issuer Credibility Indicators

**Fields Extracted** (100% coverage):
- `issuer_nation`: Country of issuance (11 countries)
- `issuer_sector`: TRBC Business Sector classification
- `issuer_type`: Classification (Corporate 77.5%, Sovereign 22.5%)
- `issuer_track_record`: Count of prior green bond issuances (0-65)
- `has_green_framework`: Binary flag for documented framework

**Interpretation**:
- **Issuer Track Record**: Repeat issuers (track_record > 3) show commitment
- **Framework Documentation**: Framework = higher credibility
- **Sector**: Utilities (29.4%) and Banking (34.2%) dominate

#### Geographic & Sector Breakdown

**Top Countries** (by # of bonds):
1. Malaysia: 125 bonds (37.5%)
2. Philippines: 80 bonds (24%)
3. Thailand: 59 bonds (17.7%)
4. Singapore: 34 bonds (10.2%)
5. Indonesia: 25 bonds (7.5%)
6. Other ASEAN: 10 bonds (3%)

**Top Sectors** (by # of bonds):
1. Banking & Investment Services: 113 bonds (34%)
2. Utilities: 98 bonds (29.4%)
3. Transportation: 38 bonds (11.4%)
4. Energy: 24 bonds (7.2%)
5. Others: 60 bonds (18%)

## Composite Authenticity Score (0-100)

### Calculation Formula

```
authenticity_score = esg_component + cert_component + issuer_component

where:
  esg_component = ESG divergence points (0-40)
  cert_component = CBI + ICMA points (0-35)
  issuer_component = issuer credibility points (0-25)
```

### Component Scoring

#### ESG Component (0-40 points)
- `is_authentic` = 1 → 30 points
- `esg_improvement > 10` → 5 bonus points
- `esg_pvalue < 0.05` → 5 bonus points
- No ESG data → 0 points

#### Certification Component (0-35 points)
- `is_cbi_certified` = 1 → 15 points
- `is_icma_certified` = 1 → 15 points
- `icma_confidence > 0.9` → 5 bonus points

#### Issuer Component (0-25 points)
- Issuer in ESG panel → 10 points
- `issuer_track_record > 0` → 10 points
- `has_green_framework` = 1 → 5 points

### Score Distribution

| Range | Category | Count | % | Interpretation |
|-------|----------|-------|---|-----------------|
| 80-100 | **High** | 13 | 3.9% | Strong authenticity signal |
| 60-79 | **Medium** | 0 | 0% | Moderate credibility |
| 40-59 | **Low** | 314 | 94.3% | Certified but weak signal |
| 0-39 | **Unverified** | 6 | 1.8% | Insufficient verification |

**Score Statistics**:
- Mean: 53.81
- Median: 55.00
- Std Dev: 13.45
- Range: 10-95

## Data Fields

### Authenticity Fields (New)

| Field | Type | Coverage | Description |
|-------|------|----------|-------------|
| `is_cbi_certified` | Binary | 100% | Climate Bonds Initiative certified |
| `is_icma_certified` | Binary | 100% | ICMA Green Bond Principles aligned |
| `icma_confidence` | Float | 100% | Confidence score (0-1) |
| `is_authentic` | Binary | 100% | ESG divergence authenticated |
| `esg_improvement` | Float | 7.5% | Pre-post ESG score change |
| `esg_pvalue` | Float | 7.5% | Statistical significance |
| `authenticity_score` | Float | 100% | Composite 0-100 score |
| `authenticity_category` | String | 100% | High/Medium/Low/Unverified |

### Issuer Verification Fields (New)

| Field | Type | Coverage | Description |
|-------|------|----------|-------------|
| `issuer_nation` | String | 100% | Country of issuance |
| `issuer_sector` | String | 100% | TRBC sector classification |
| `issuer_type` | String | 100% | Corporate/Sovereign/etc |
| `issuer_track_record` | Integer | 100% | # of prior green bonds |
| `has_green_framework` | Binary | 100% | Framework exists |

## Limitations & Caveats

### Data Availability
- **ESG Coverage**: Only 7.5% have complete pre-post ESG data
- **Geographic Bias**: Malaysian bonds over-represented (37.5%)
- **Time Window**: ESG data from 2015-2023; limited recent data

### Methodology Limitations
- **ESG Divergence**: Requires 2+ observations per issuer; only 25 bonds qualify
- **ICMA Heuristic**: Cannot verify actual framework documentation or issuance impact
- **CBI Definition**: "Green Bond Purposes" is proxy; may not capture all CBI-certified bonds
- **Selection Bias**: Data limited to ASEAN; other regions may differ

### Interpretation Warnings

⚠️ **High Authenticity (3.9%) ≠ All Bonds Authentic**
- Majority (96.1%) lack statistical evidence of ESG improvement
- Absence of evidence ≠ evidence of greenwashing
- May reflect data limitations rather than actual performance

⚠️ **Certifications ≠ Real Impact**
- CBI/ICMA certification proves framework alignment, not environmental impact
- Bonds can be certified yet fail to deliver promised benefits

⚠️ **Issuer Track Record ≠ Quality**
- Repeat issuers may have governance commitment but weaker projects
- Track record indicates institutional engagement, not project outcomes

## How to Use This Data

### For Research
1. Load `green_bonds_authenticated.csv`
2. Filter by `authenticity_category` for analysis
3. Use `esg_improvement` for econometric models
4. Control for `issuer_track_record` and `issuer_sector`

### For Policy Analysis
1. Compare certification rates by country
2. Analyze sector-specific patterns
3. Identify greenwashing risk (certified but low ESG improvement)
4. Track issuer behavior over time

### For Investment
1. Flag high authenticity bonds (score ≥80)
2. Monitor issuer track record and framework
3. Consider ESG improvement for environmental impact
4. Use sector classification for portfolio diversification

## References

- Climate Bonds Initiative: https://www.climatebonds.net/
- ICMA Green Bond Principles: https://www.icmagroup.org/
- Refinitiv LSEG Data: https://developers.refinitiv.com/
- ESG Data Sources: esg_panel_data.csv (ASEAN firm-year panel)

## Contact & Questions

For questions about methodology or data, refer to:
- AUTHENTICITY_SCORE_IMPLEMENTATION.md (technical details)
- CONSOLIDATED_ATTRIBUTES_COLUMN_MAPPING.json (field definitions)
- FINAL_VALIDATION_SUMMARY.txt (data quality metrics)

---

**Last Updated**: March 18, 2026
**Data Version**: 1.0
**Status**: Complete - All 333 ASEAN green bonds (2015-2025) authenticated
