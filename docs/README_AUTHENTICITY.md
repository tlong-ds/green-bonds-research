# ASEAN Green Bonds: Authenticity Verification Guide

## Overview

This documentation covers the **bond authenticity verification system** for 333 ASEAN green bonds issued between 2015-2025. The system provides a comprehensive measure of green bond authenticity through a **composite score (0-100)** that combines three independent verification pillars.

## What is Authenticity Verification?

**Green bond authenticity** refers to the degree to which a bond labeled as "green" actually delivers environmental benefits or adheres to established green finance standards. A bond's authenticity depends on:

1. **ESG Performance**: Documented improvement in environmental, social, or governance metrics after issuance
2. **Framework Compliance**: Adherence to recognized certification standards (CBI, ICMA)
3. **Issuer Credibility**: Issuer track record, institutional commitment to green finance

## Why It Matters for Green Bonds Research

### The Greenwashing Problem

While 98.5% of bonds in our dataset are formally certified as green, **only 3.9% show statistically significant ESG performance improvement**. This gap highlights a critical research challenge:

- **Certification Inflation**: Most green bonds meet framework requirements but don't demonstrate measurable environmental benefit
- **Impact Uncertainty**: High certification rates mask heterogeneous actual environmental outcomes
- **Investor Confusion**: Researchers and investors lack standardized metrics to distinguish authentic from nominal green bonds

### Research Implications

Authenticity verification enables:
- **Impact Investing**: Identify bonds with proven environmental outcomes
- **Greenwashing Detection**: Flag bonds with misaligned certification and performance
- **Comparative Analysis**: Analyze issuer commitment across time and geography
- **Risk Assessment**: Understand environmental claims integrity in emerging markets

## The 3-Pillar Approach

### Pillar 1: ESG Divergence (40% weight)
**Most reliable indicator of actual environmental impact**

- **Definition**: Statistical test of pre- vs. post-issuance ESG performance improvement
- **Coverage**: 66/333 bonds (19.8%) with available ESG data
- **Authenticity Rate**: 13/333 (3.9%) show statistically significant improvement (p < 0.10)
- **Average Improvement**: 23.6 points (for authentic bonds)
- **Method**: Paired t-test on ESG scores across 5-year windows pre- and post-issuance

**Scoring Logic:**
- Base: `is_authentic == 1` → +30 points
- Bonus: `esg_improvement > 10` → +5 points
- Bonus: `p-value < 0.05` (significant) → +5 points
- Maximum: 40 points

### Pillar 2: Certification Compliance (35% weight)
**Framework adherence and institutional recognition**

#### CBI (Climate Bonds Initiative) Certification
- **Definition**: Climate Bonds Standard certification indicator
- **Coverage**: 328/333 bonds (98.5%)
- **Implementation**: Identified via "Green Bond Purposes" in Primary Use of Proceeds
- **Points**: +15 if certified

#### ICMA (International Capital Market Association) Certification
- **Definition**: Green Bond Principles (GBP) compliance
- **Coverage**: 326/333 bonds (97.9%)
- **Average Confidence**: 0.89 (scale 0-1)
- **Confidence Thresholds**: 
  - HIGH (0.8-1.0): 263 bonds (79%)
  - MEDIUM (0.6-0.8): 60 bonds (18%)
  - LOW (0.4-0.6): 10 bonds (3%)
- **Points**: +15 if certified, +5 bonus if confidence > 0.9

**Scoring Logic:**
- CBI certification: +15 points
- ICMA certification: +15 points
- High ICMA confidence (>0.9): +5 bonus points
- Maximum: 35 points

### Pillar 3: Issuer Verification (25% weight)
**Issuer credibility and institutional commitment to green finance**

- **Coverage**: 100% of bonds verified
- **Components**:
  - **issuer_nation** (10 pts): Issuer country matches issuer nation field
  - **issuer_track_record** (10 pts): Cumulative green bonds issued by issuer
    - 263/333 (79%) have track record (>1 prior green bond)
  - **has_green_framework** (5 pts): Documented green bond framework
    - 328/333 (98.5%) have framework

**Scoring Logic:**
- Issuer verified: +10 points (if nation fields match)
- Track record exists: +10 points (if issued >1 prior green bond)
- Green framework documented: +5 points
- Maximum: 25 points

## Composite Score Calculation

```
Final Score = ESG Component + Cert Component + Issuer Component
Range: 0-100 (continuous scale)
```

### Score Interpretation

| Category | Range | Bonds | % | Interpretation |
|----------|-------|-------|---|-----------------|
| **High Authenticity** | 80-100 | 13 | 3.9% | Robust verification across all pillars; proven ESG impact |
| **Medium Authenticity** | 60-79 | 0 | 0.0% | Moderate verification coverage; certified but impact unclear |
| **Low Authenticity** | 40-59 | 314 | 94.3% | Limited verification; certified but no ESG impact proof |
| **Unverified** | <40 | 6 | 1.8% | Minimal verification; missing certifications or framework |

## Key Findings

### Distribution Snapshot
- **Mean Score**: 53.81 (Std: 9.90)
- **Median Score**: 55.00
- **Score Range**: 10-95

### Component Breakdown
1. **Certification Component**: 29.46/35 points (average)
   - Drives most scores due to 98.5% certification rate
2. **Issuer Component**: 22.82/25 points (average)
   - Universal coverage; nearly all issuers verified
3. **ESG Component**: 1.53/40 points (average)
   - Most selective; only 3.9% authentic

### Geographic Concentration
- **Malaysia**: 125 bonds (37.5%)
- **Philippines**: 80 bonds (24.0%)
- **Thailand**: 59 bonds (17.7%)
- **Singapore**: 34 bonds (10.2%)
- **Indonesia**: 25 bonds (7.5%)

### Sector Distribution
- **Financials**: 114 bonds (34.2%)
- **Utilities**: 98 bonds (29.4%)
- **Industrials**: 65 bonds (19.5%)
- **Real Estate**: 25 bonds (7.5%)
- **Energy**: 16 bonds (4.8%)

## How to Use the Data

### Loading the Data

```python
import pandas as pd

# Load authenticated bond data
df = pd.read_csv('data/green_bonds_authenticated.csv')

# 333 bonds × 64 columns including:
# - Authenticity scores and components
# - Certification indicators
# - ESG performance data
# - Issuer information
```

### Basic Filtering

```python
# High authenticity bonds (likely to have ESG impact)
high_auth = df[df['authenticity_score'] >= 80]

# Authentic bonds by ESG divergence test
authentic_esg = df[df['is_authentic'] == 1]

# Certified but unauthentic bonds (potential greenwashing)
certified_unauth = df[(df['is_cbi_certified']==1) & (df['is_authentic']==0)]

# Bonds by country
malaysia_bonds = df[df['Issuer/Borrower Nation'] == 'Malaysia']

# Bonds by sector
utility_bonds = df[df['Issuer/Borrower TRBC Economic Sector'] == 'Utilities']
```

### Advanced Analysis

```python
# Score distribution by geography
df.groupby('Issuer/Borrower Nation')['authenticity_score'].agg(['mean', 'median', 'count'])

# Sector comparison
df.groupby('Issuer/Borrower TRBC Economic Sector').agg({
    'authenticity_score': 'mean',
    'is_authentic': 'sum',
    'is_cbi_certified': 'sum'
})

# Issuer comparison (top issuers by bonds)
df.groupby('Issuer/Borrower Name Full').agg({
    'authenticity_score': ['mean', 'count'],
    'is_authentic': 'sum'
}).sort_values(('authenticity_score', 'count'), ascending=False)
```

## Methodology Limitations

### ESG Data Availability
- **Only 19.8%** (66/333) bonds have available ESG performance data
- ESG metrics sourced from Refinitiv/LSEG databases
- Data availability varies significantly by issuer and time period
- Bonds without ESG data cannot be verified via Pillar 1

### Certification as Proxy
- **CBI/ICMA certifications** are inferred from available data fields
- "Green Bond Purposes" field used as CBI indicator (not external verification)
- ICMA confidence is heuristic-based, not definitive certification
- Actual external certification status may differ

### Issuer Track Record
- **Track record** measured as cumulative green bonds issued
- Does not account for bond performance or issuer reputation
- Issuer history may not reflect current commitment quality

### Statistical Significance Threshold
- **ESG authenticity** requires p-value < 0.10 (10% significance level)
- This is more lenient than typical academic standards (5%)
- Chosen to maximize detection of smaller emerging markets effects
- Sample sizes vary by issuer (n_pre_obs, n_post_obs columns)

### Geographic Bias
- Dataset concentrates on **Southeast Asian** issuers
- Results may not generalize to other regions
- Country-level regulations and frameworks differ

## Caveats and Considerations

### The "Low Authenticity Gap"
94.3% of bonds (314/333) score in the "Low" category despite:
- 98.5% having formal CBI certification
- 100% having verified issuers
- 98.5% having documented green frameworks

**This gap likely reflects:**
1. **Measurement timing**: ESG scores measured at specific points; impacts may emerge later
2. **Lag effects**: Environmental improvements take time to materialize
3. **Data quality**: ESG metrics may be incomplete or inconsistent
4. **Sector differences**: Some sectors (e.g., infrastructure) show benefits over longer horizons

### Authenticity ≠ Impact
- High authenticity score indicates **verified ESG divergence**, not causation
- Other factors may drive ESG improvements (regulation, market conditions)
- Statistical significance doesn't prove the bond caused the improvement
- Impact attribution requires more sophisticated causal inference

### Certification Inflation Risk
- 98.5% certification rate suggests possible **certification inflation**
- Formal compliance may not match substantive environmental outcomes
- Framework standards may be too lenient for emerging markets
- Regular framework updates needed

## Data Quality Assessment

| Metric | Coverage | Status |
|--------|----------|--------|
| Authenticity Scores | 333/333 (100%) | ✓ Complete |
| ESG Data | 66/333 (19.8%) | ⚠ Limited |
| Certification Data | 333/333 (100%) | ✓ Complete |
| Issuer Verification | 333/333 (100%) | ✓ Complete |
| ESG Divergence Sig. | 13/333 (3.9%) | ⚠ Rare |

## Next Steps for Users

1. **For High-Authenticity Research**: Focus on 13 authentic bonds for impact investing analysis
2. **For Sector Analysis**: Compare authenticity across Financials, Utilities, and Industrials
3. **For Geographic Study**: Examine Malaysia (125 bonds) and Philippines (80 bonds) patterns
4. **For Greenwashing Investigation**: Analyze 320 certified-but-unauthentic bonds
5. **For ESG Tracking**: Use pre/post issuance scores to measure trajectory

## File Structure

```
data/
├── green_bonds_authenticated.csv          # Full dataset (333 × 64)
├── README_AUTHENTICITY.md                 # This guide
├── METHODOLOGY_AUTHENTICITY.md            # Technical methodology
├── FINDINGS_AUTHENTICITY.md               # Statistical analysis
├── USAGE_GUIDE_AUTHENTICITY.md            # How-to guide
├── FIELD_DEFINITIONS.md                   # Column descriptions
├── DATA_QUALITY_REPORT.md                 # Coverage report
└── LIMITATIONS_AND_CAVEATS.md             # Limitations detail
```

## References

- Climate Bonds Initiative. (2021). *Establishing and Operationalizing a Framework on Taxonomy and Criteria for Defining Green Bonds*.
- ICMA. (2021). *Green Bond Principles* (2021 Edition).
- Lindenberg, N. (2014). *Green Bonds: A Brief Assessment of the Emerging Market*. German Development Institute.

## Citation

If using this data, please cite:

```
ASEAN Green Bonds Research Dataset (2015-2025)
Green Bond Authenticity Verification System
Available at: [repository path]
```

## Questions & Support

For questions about the authenticity verification methodology or data:
- See METHODOLOGY_AUTHENTICITY.md for technical details
- See FINDINGS_AUTHENTICITY.md for statistical analysis
- See DATA_QUALITY_REPORT.md for coverage information

---

**Last Updated**: 2025  
**Analysis Period**: 2015-2025  
**Total Bonds**: 333  
**Geographic Focus**: ASEAN Region  
