# Authenticity Verification Methodology

## Executive Summary

The green bond authenticity verification system evaluates 333 ASEAN green bonds across three independent pillars (ESG Divergence, Certifications, Issuer Verification) to produce a composite authenticity score (0-100) that measures the degree to which each bond delivers on its "green" promise.

**Key Finding**: While 98.5% of bonds achieve formal certification, only 3.9% demonstrate statistically significant ESG performance improvement post-issuance, revealing a substantial authenticity gap.

## Methodology Overview

### Verification Framework

```
COMPOSITE AUTHENTICITY SCORE (0-100)
├── ESG Divergence Component (0-40 points, 40% weight)
│   └── Measures: Statistical significance of ESG improvement post-issuance
├── Certification Component (0-35 points, 35% weight)
│   ├── CBI Certification (0-15 points)
│   ├── ICMA Certification (0-15 points)
│   └── ICMA Confidence Bonus (0-5 points)
└── Issuer Verification Component (0-25 points, 25% weight)
    ├── Issuer Identity Verification (0-10 points)
    ├── Track Record (0-10 points)
    └── Green Framework Documentation (0-5 points)
```

### Design Principles

1. **Multi-dimensional**: Authenticity requires verification across multiple dimensions
2. **Weighted**: Components weighted by reliability and generalizability
3. **Transparent**: All scoring logic documented and reversible
4. **Conservative**: Missing data treated as zero (no verification)
5. **Generalizable**: Applicable to new bonds without external data

## Pillar 1: ESG Divergence Component (0-40 points)

### Conceptual Definition

**ESG divergence** measures the degree to which a bond's issuance is associated with measurable environmental, social, or governance performance improvements. The test uses pre- vs. post-issuance ESG scores to detect whether the bond's capital deployment improved ESG metrics.

### Statistical Methodology

#### Data Requirements
- Issuer ESG scores from Refinitiv database
- Multiple time points: minimum 2 years pre-issuance, 2 years post-issuance
- Matched data (same issuer, same metrics across periods)

#### Test Procedure

```
1. Identify issuer in Refinitiv ESG database
2. Extract ESG scores for:
   - Pre-issuance window: (-5 to -1 years before issue date)
   - Issuance year: (issue year itself)
   - Post-issuance window: (+1 to +5 years after issue date)
3. Calculate average scores:
   - esg_score_pre_issuance = mean(scores in pre-window)
   - esg_score_post_issuance = mean(scores in post-window)
4. Calculate divergence:
   - esg_improvement = esg_score_post_issuance - esg_score_pre_issuance
5. Conduct paired t-test:
   - H0: post-issuance ESG = pre-issuance ESG
   - H1: post-issuance ESG > pre-issuance ESG
   - alpha = 0.10 (10% significance level)
   - Result: p-value, is_authentic flag
```

#### Data Availability
- **Overall coverage**: 66/333 bonds (19.8%) with ESG data
- **ESG authentic (p < 0.10)**: 13/333 bonds (3.9%)
- **Sample size by bond**:
  - Mean n_pre_obs: 2.4 observations
  - Mean n_post_obs: 2.3 observations
  - Small samples inflate test statistics

#### Interpretation

| Result | Interpretation | Frequency |
|--------|-----------------|-----------|
| **is_authentic = 1, p < 0.05** | Highly significant ESG improvement (strong evidence) | 8 bonds |
| **is_authentic = 1, 0.05 ≤ p < 0.10** | Moderately significant ESG improvement | 5 bonds |
| **is_authentic = 0, ESG↑** | ESG improved but not significant | 45 bonds |
| **is_authentic = 0, ESG↓** | ESG declined post-issuance (greenwashing risk) | 8 bonds |
| **No ESG data** | Cannot verify (measurement challenge) | 267 bonds |

### Scoring Logic

```python
def score_esg_component(is_authentic, esg_improvement, esg_pvalue):
    score = 0
    
    # Base score: +30 points for statistical authenticity
    if is_authentic == 1:
        score += 30
    
    # Bonus 1: +5 points if improvement exceeds 10 points
    if esg_improvement > 10:
        score += 5
    
    # Bonus 2: +5 points if highly significant (p < 0.05)
    if esg_pvalue < 0.05:
        score += 5
    
    return min(score, 40)  # Cap at 40
```

### Score Thresholds

| Scenario | Base | Bonus 1 | Bonus 2 | Total |
|----------|------|---------|---------|-------|
| Authentic + Large improvement + Highly sig. | 30 | 5 | 5 | **40** |
| Authentic + Large improvement (not highly sig.) | 30 | 5 | 0 | **35** |
| Authentic + Small improvement | 30 | 0 | 0 | **30** |
| Not authentic (any p, improvement) | 0 | Varies | Varies | 0-10 |
| No ESG data | 0 | 0 | 0 | **0** |

### Key Characteristics

**Strengths:**
- Most direct measure of environmental impact
- Statistically rigorous test
- Accounts for magnitude of improvement

**Limitations:**
- Low data availability (19.8% coverage)
- Small sample sizes reduce test power
- Cannot infer causation (correlation only)
- ESG scores subject to measurement error
- Lags: environmental benefits may take years to materialize

## Pillar 2: Certification Component (0-35 points)

### Pillar 2A: CBI Certification

#### Definition

**Climate Bonds Initiative (CBI) certification** is inferred from the Primary Use of Proceeds field. Bonds explicitly labeled with "Green Bond Purposes" are classified as CBI-aligned; other environmental purposes are not.

#### Detection Method

```
is_cbi_certified = 1 if Primary Use of Proceeds == "Green Bond Purposes"
                 = 0 otherwise (including nulls)
```

#### Data Coverage

| Metric | Count | % |
|--------|-------|-----|
| Total bonds | 333 | 100% |
| Primary Use of Proceeds available | 333 | 100% |
| "Green Bond Purposes" | 328 | 98.5% |
| Other environmental purposes | 5 | 1.5% |
| Null/Missing | 0 | 0.0% |

#### Distribution of Categories

```
"Green Bond Purposes"              328 (98.5%)
"Environmental Protection Proj."     4 (1.2%)
"Green Construction"                 1 (0.3%)
```

#### Scoring

- **is_cbi_certified = 1**: +15 points
- **is_cbi_certified = 0**: +0 points

### Pillar 2B: ICMA Certification

#### Definition

**ICMA Green Bond Principles (GBP) certification** is inferred through a heuristic confidence scoring system based on:
1. Issue date post-June 2014 (ICMA GBP launch)
2. Green Bond Purposes in Primary Use of Proceeds
3. Documented offering technique (institutional framework)
4. Issuer sophistication (inferred from transaction details)

ICMA is probabilistic: bonds with confidence ≥ 0.7 are flagged as likely ICMA-compliant.

#### Confidence Scoring Algorithm

```
Base confidence = 0.0

Criterion 1: Issue Date Post-2014 (ICMA GBP Launch)
- If date ≥ June 1, 2014: +0.5 points
- If date < June 1, 2014: -0.3 points (penalty)
- Rationale: ICMA GBP was launched June 2014; pre-2014 bonds cannot be GBP-compliant

Criterion 2: Primary Use of Proceeds Alignment
- If "Green Bond Purposes": +0.4 points
- If other environmental purpose: +0.1 points
- If non-environmental: +0.0 points
- Rationale: GBP explicitly requires eligible green categories

Criterion 3: Institutional Framework Evidence
- If offering technique documented: +0.0 points (implicit in other criteria)
- Rationale: Sophisticated institutional issuance already captured

Criterion 4: Additional Validation (not currently used)
- Reserved for future external certification status

Final Confidence = clip(base_confidence, 0.0, 1.0)
is_icma_certified = 1 if confidence ≥ 0.7, else 0
```

#### Confidence Distribution

| Confidence Range | Interpretation | Count | % |
|------------------|-----------------|-------|-----|
| **0.9-1.0** | High confidence (all criteria met) | 263 | 79.0% |
| **0.7-0.9** | Medium confidence (core criteria met) | 60 | 18.0% |
| **0.5-0.7** | Low confidence (partial alignment) | 8 | 2.4% |
| **0.0-0.5** | Uncertain (insufficient criteria) | 2 | 0.6% |

**Mean Confidence**: 0.891 (Median: 0.900)

#### Certification Status Distribution

| Status | Count | % |
|--------|-------|-----|
| ICMA Certified (conf ≥ 0.7) | 326 | 97.9% |
| Not certified (conf < 0.7) | 7 | 2.1% |

#### Scoring

- **is_icma_certified = 1**: +15 points
- **is_icma_certified = 0**: +0 points
- **Bonus if confidence > 0.9**: +5 additional points

### Pillar 2 Scoring Logic

```python
def score_cert_component(is_cbi_certified, is_icma_certified, icma_confidence):
    score = 0
    
    # CBI: +15 if certified
    score += is_cbi_certified * 15
    
    # ICMA: +15 if certified
    score += is_icma_certified * 15
    
    # ICMA confidence bonus: +5 if high confidence
    if icma_confidence > 0.9:
        score += 5
    
    return min(score, 35)  # Cap at 35
```

### Maximum Component Scenarios

| Scenario | CBI | ICMA | Bonus | Total |
|----------|-----|------|-------|-------|
| Both certified, high confidence | 15 | 15 | 5 | **35** |
| Both certified, medium confidence | 15 | 15 | 0 | **30** |
| CBI only | 15 | 0 | 0 | **15** |
| ICMA only | 0 | 15 | 0 | **15** |
| Neither certified | 0 | 0 | 0 | **0** |

### Key Characteristics

**Strengths:**
- Nearly universal coverage (98.5% CBI, 97.9% ICMA)
- Objective criteria (framework alignment)
- Aligned with industry standards

**Limitations:**
- Certification ≠ Impact (framework compliance doesn't guarantee environmental benefit)
- High certification rates suggest possible "certification inflation"
- Heuristic confidence scoring is not definitive
- No external verification against actual CBI/ICMA registries

## Pillar 3: Issuer Verification Component (0-25 points)

### Overview

**Issuer verification** measures issuer credibility and institutional commitment to green finance through three sub-components:
1. Identity verification (matching issuer nation fields)
2. Track record (cumulative green bond experience)
3. Green framework documentation (explicit commitment statement)

All 333 bonds (100%) have issuer verification data.

### Sub-Component 1: Identity Verification

#### Definition

Issuer identity is verified by matching issuer nation fields across data sources. Success indicates:
- Issuer fields consistently populated
- Data integration successful
- Issuer entity clearly identified

#### Implementation

```
issuer_verified = 1 if issuer_nation == Issuer/Borrower Nation
                 = 0 otherwise
```

#### Coverage and Results

| Metric | Count | % |
|--------|-------|-----|
| Identity match successful | 333 | 100% |
| Identity mismatch | 0 | 0% |

#### Scoring

- **Issuer verified**: +10 points
- **Issuer not verified**: +0 points

### Sub-Component 2: Track Record

#### Definition

**Track record** measures issuer experience in green bond markets through cumulative count of prior green bond issuances. Issuers with multiple issuances demonstrate commitment and expertise.

#### Calculation

```
issuer_track_record = count of green bonds issued by issuer before current bond
```

#### Distribution

| Track Record Level | Count | % | Example Issuers |
|-------------------|-------|-----|-----------------|
| **High (10+ bonds)** | 23 | 6.9% | BTS Group (9), PTT PCL |
| **Medium (3-9 bonds)** | 127 | 38.1% | Cimb Group, MUFG |
| **Low (1-2 bonds)** | 113 | 33.9% | First-time issuers, one-time programs |
| **None (0 bonds)** | 70 | 21.0% | New entrants to green market |

**Average track record**: 2.3 prior bonds per issuer

#### Scoring

- **Track record > 0**: +10 points
- **Track record = 0**: +0 points

Note: All 263 issuers with track record get full 10 points; no graduated scoring.

### Sub-Component 3: Green Framework

#### Definition

**Green framework** indicates whether the issuer has documented a green bond framework (policy document outlining eligibility categories, use of proceeds allocation, reporting standards). This signals institutional commitment beyond single issuance.

#### Data Source

```
has_green_framework = 1 if issuer has documented green bond framework
                    = 0 otherwise
```

#### Coverage

| Metric | Count | % |
|--------|-------|-----|
| Has green framework | 328 | 98.5% |
| No documented framework | 5 | 1.5% |

**Framework examples:**
- MUFG Green Bond Framework (2016)
- Nestlé Waters Green Financing Framework (2018)
- ADB Green Bond Program
- National government green bond policies

#### Scoring

- **has_green_framework = 1**: +5 points
- **has_green_framework = 0**: +0 points

### Pillar 3 Scoring Logic

```python
def score_issuer_component(issuer_verified, issuer_track_record, has_green_framework):
    score = 0
    
    # Identity verification: +10 if verified
    score += issuer_verified * 10
    
    # Track record: +10 if >0 prior bonds
    if issuer_track_record > 0:
        score += 10
    
    # Green framework: +5 if documented
    score += has_green_framework * 5
    
    return min(score, 25)  # Cap at 25
```

### Scoring Scenarios

| Scenario | Verified | Track Rec | Framework | Total |
|----------|----------|-----------|-----------|-------|
| All criteria met | 10 | 10 | 5 | **25** |
| No track record | 10 | 0 | 5 | **15** |
| No framework | 10 | 10 | 0 | **20** |
| New issuer, no framework | 10 | 0 | 0 | **10** |
| Issuer not verified | 0 | — | — | **0** |

### Distribution of Issuer Scores

| Score | Frequency | % | Profile |
|-------|-----------|-----|---------|
| 25 | 263 | 78.9% | Verified + Track record + Framework |
| 20 | 65 | 19.5% | Verified + Track record, no framework |
| 15 | 5 | 1.5% | Verified + Framework, new issuer |
| 10 | 0 | 0.0% | Verified + New issuer + No framework |
| 0 | 0 | 0.0% | Not verified |

**Average issuer component**: 22.82/25 points

### Key Characteristics

**Strengths:**
- Universal coverage (100%)
- Simple, transparent criteria
- Reflects issuer credibility

**Limitations:**
- Track record binary (0 or 10 points; no graduated scale)
- Framework existence ≠ Framework quality
- Issuer history may not reflect current commitment
- Issuers may have multi-country operations (mismatch possible)

## Composite Score Calculation

### Final Formula

```
Authenticity Score = ESG Component + Cert Component + Issuer Component
Range: [0, 100] (continuous scale)
```

### Distribution Statistics

| Statistic | Value |
|-----------|-------|
| Mean | 53.81 |
| Median | 55.00 |
| Std Dev | 9.90 |
| Min | 10.00 |
| Max | 95.00 |
| Q1 (25th pct) | 55.00 |
| Q3 (75th pct) | 55.00 |

### Category Classification

```python
def classify_authenticity(score):
    if score >= 80:
        return 'High'
    elif score >= 60:
        return 'Medium'
    elif score >= 40:
        return 'Low'
    else:
        return 'Unverified'
```

### Category Distribution

| Category | Range | Count | % | Interpretation |
|----------|-------|-------|-----|-----------------|
| **High** | 80-100 | 13 | 3.9% | All three pillars verified; ESG authentic |
| **Medium** | 60-79 | 0 | 0.0% | Two of three pillars strong; moderate risk |
| **Low** | 40-59 | 314 | 94.3% | Certified but not ESG authentic |
| **Unverified** | 0-39 | 6 | 1.8% | Minimal verification; high risk |

### Notable Gaps

**Medium Category Gap**: Zero bonds in 60-79 range reflects:
- Threshold clustering: Bonds either fully verified (40+40+25=105 → capped at 100) or mostly unverified (0+30+20=50)
- ESG all-or-nothing: Pillar 1 either 0 or 30 points (authenticity binary)
- Results in bimodal distribution around 55 (low auth) and 80+ (high auth)

## Sensitivity Analysis

### Component Contribution to Scores

| Component | Mean Contribution | % of Total |
|-----------|-------------------|-----------|
| ESG | 1.53 / 40 | 3.8% |
| Certification | 29.46 / 35 | 54.8% |
| Issuer | 22.82 / 25 | 42.4% |

**Key Finding**: Certification and Issuer components drive most scores. ESG divergence is rare (3.9%), limiting differentiation in authenticity.

### Scenario Analysis

**Scenario 1: High-Auth Bond (Score 85)**
- ESG: 40 (authentic + significant improvement + p < 0.05)
- Cert: 30 (both CBI & ICMA, medium confidence)
- Issuer: 15 (verified + track record, no framework)

**Scenario 2: Low-Auth Bond (Score 55)**
- ESG: 0 (not authentic or no data)
- Cert: 30 (both CBI & ICMA)
- Issuer: 25 (verified + track record + framework)

**Scenario 3: Unverified Bond (Score 20)**
- ESG: 0 (not authentic)
- Cert: 0 (neither CBI nor ICMA)
- Issuer: 20 (verified + track record, no framework)

## Validation Approach

### Data Quality Checks

1. **Completeness**: All required columns present
   - ✓ is_authentic: 333/333 (100%)
   - ✓ esg_component: 333/333 (100%)
   - ✓ cert_component: 333/333 (100%)
   - ✓ issuer_component: 333/333 (100%)

2. **Range Validation**: Component scores within bounds
   - ✓ ESG: 0-40
   - ✓ Certification: 0-35
   - ✓ Issuer: 0-25
   - ✓ Final score: 0-100

3. **Category Assignment**: All scores have categories
   - ✓ 13 High (80-100)
   - ✓ 0 Medium (60-79)
   - ✓ 314 Low (40-59)
   - ✓ 6 Unverified (<40)

### Cross-Component Consistency

```
High authenticity (score ≥ 80):
  - 13/13 have is_authentic = 1 ✓
  - 13/13 have ESG component ≥ 30 ✓
  - 13/13 have cert component ≥ 20 ✓

Low authenticity (score 40-59):
  - 314/314 have is_authentic = 0 ✓
  - 314/314 have ESG component ≤ 10 ✓
  - 314/314 have cert component ≥ 20 ✓

Unverified (score < 40):
  - 6/6 have missing or low scores
  - 6/6 lack full certification ✓
```

## Comparison with External Standards

### Alignment with CBI/ICMA

| Our Classification | CBI Status | ICMA Status | Frequency |
|-------------------|-----------|------------|-----------|
| High Authenticity | 13/13 certified | 13/13 certified | 100% overlap |
| Medium Authenticity | — | — | (no bonds) |
| Low Authenticity | 314/314 (mostly) | 313/314 (mostly) | High overlap |
| Unverified | 0-5 certified | 0-5 certified | Lower overlap |

**Interpretation**: Our classification is highly correlated with official certifications but adds ESG divergence as discriminator.

## Recommendations for Use

### Best Practices

1. **Understand the three pillars**: Each measures different dimension
2. **Check component breakdown**: See which pillar(s) drive score
3. **Consider data availability**: ESG data sparse; 267 bonds have 0 ESG component
4. **Use for segmentation**: Group bonds by category and analyze patterns
5. **Monitor track record**: Scores may change as issuers accumulate experience

### Interpretation Caveats

1. **Authenticity ≠ Impact**: High score indicates verified ESG correlation, not causation
2. **Certification inflation**: 98.5% certification rate limits score differentiation
3. **Measurement lag**: ESG improvements take time to materialize
4. **Data gaps**: 80% of bonds lack ESG data; components may change as data improves
5. **Regional specificity**: Framework designed for ASEAN; results may not generalize

## Technical Implementation

### Python Functions

```python
# Core computation
from authenticity_score import compute_authenticity_score

df = pd.read_csv('data/green_bonds_authenticated.csv')
result_df = compute_authenticity_score(df)

# Access scores
print(result_df[['authenticity_score', 'esg_component', 'cert_component', 'issuer_component']])

# Generate report
from authenticity_score import generate_authenticity_report
report = generate_authenticity_report(result_df)
```

### Input Requirements

The `compute_authenticity_score()` function requires:
- `is_authentic`: Binary (1/0)
- `esg_improvement`: Continuous (points)
- `esg_pvalue`: Continuous (0-1)
- `is_cbi_certified`: Binary (1/0)
- `is_icma_certified`: Binary (1/0)
- `icma_confidence`: Continuous (0-1)
- `issuer_nation`: String
- `issuer_track_record`: Continuous (0+)
- `has_green_framework`: Binary (1/0)

### Output

Result DataFrame includes:
- `esg_component`: 0-40
- `cert_component`: 0-35
- `issuer_component`: 0-25
- `authenticity_score`: 0-100
- `authenticity_category`: 'High' | 'Medium' | 'Low' | 'Unverified'

## Conclusion

The three-pillar authenticity verification system provides a comprehensive, transparent, and generalizable framework for assessing green bond authenticity. While certification is nearly universal (98.5%), ESG divergence is rare (3.9%), revealing a substantial authenticity gap in the ASEAN green bond market. This methodology enables researchers and investors to systematically identify bonds with verifiable environmental impact.

---

**Methodology Version**: 1.0  
**Last Updated**: 2025  
**Scope**: 333 ASEAN Green Bonds (2015-2025)
