# Usage Guide & Examples

## Quick Start Example

### Complete Analysis Pipeline in 10 Lines

```python
from asean_green_bonds import data, analysis, utils

# 1. Load processed data
df = data.load_processed_data(which='engineered')

# 2. Estimate propensity scores
df['ps'] = analysis.estimate_propensity_scores(df)

# 3. Run DiD estimation
results = analysis.estimate_did(df, outcome='return_on_assets')

# 4. Visualize results
utils.plot_did_results(results)

print(f"Treatment effect: {results['coefficient']:.4f}")
print(f"P-value: {results['p_value']:.4f}")
```

## Data Module Examples

### 1. Load Raw Data

```python
from asean_green_bonds import data

# Load individual datasets
panel = data.load_raw_panel_data()
esg = data.load_esg_panel_data()
green_bonds = data.load_green_bonds_data(asean_only=True)

print(f"Panel shape: {panel.shape}")
print(f"Green bond issuers: {green_bonds.shape[0]}")
```

### 2. Process Data

```python
# Merge datasets
df = data.merge_panel_data(panel, esg, market_data)

# Add green bond indicators
df = data.merge_green_bonds(df, green_bonds, market_data)

# Filter to ASEAN firms and valid years
df = data.filter_asean_firms_and_years(df, min_year=2015, max_year=2024)

# Handle missing values
df = data.handle_missing_values(df, min_years_per_firm=3)

# Create features
df = data.create_log_features(df)
df = data.winsorize_outliers(df)

print(f"Processed dataset: {df.shape}")
```

### 3. Feature Selection

```python
# Calculate VIF for multicollinearity
vif_df = data.calculate_vif(df)
print(vif_df[vif_df['VIF'] > 10])  # High VIF features

# Select features based on correlation
from asean_green_bonds.config import OUTCOME_VARIABLES
for outcome in OUTCOME_VARIABLES:
    features = data.correlation_filter(df, outcome=outcome)
    print(f"{outcome}: {len(features)} correlated features")

# Run full selection pipeline
selected_features, report = data.compile_selected_features(
    df,
    outcome_cols=OUTCOME_VARIABLES,
    control_cols=['L1_Firm_Size', 'L1_Leverage'],
    selection_method='union'
)

print(f"Selected {len(selected_features)} features")
```

## Analysis Module Examples

### 1. Propensity Score Matching

```python
from asean_green_bonds import analysis

# Step 1: Estimate propensity scores
df['propensity_score'] = analysis.estimate_propensity_scores(
    df,
    treatment_col='green_bond_active'
)

# Step 2: Check common support
support = analysis.check_common_support(df)
print(f"Treated overlap: {support['treated_overlap_pct']:.1f}%")
print(f"Control overlap: {support['control_overlap_pct']:.1f}%")

# Step 3: Perform matching
matched_df, stats = analysis.nearest_neighbor_matching(
    df,
    ps_col='propensity_score',
    caliper=0.1,
    ratio=4
)
print(f"Matched observations: {len(matched_df)}")

# Step 4: Check balance
balance = analysis.assess_balance(matched_df, features=['L1_Firm_Size'])
print(balance)
```

### 2. Difference-in-Differences Estimation

```python
# Single outcome, single specification
result = analysis.estimate_did(
    df,
    outcome='return_on_assets',
    treatment_col='green_bond_active',
    specification='entity_fe'  # or 'time_fe', 'twoway_fe', 'none'
)

print(f"Coefficient: {result['coefficient']:.4f}")
print(f"SE: {result['std_error']:.4f}")
print(f"t-stat: {result['t_statistic']:.4f}")
print(f"p-value: {result['p_value']:.4f}")
print(f"Significant: {result['significant_5pct']}")

# Multiple outcomes and specifications
results = analysis.run_multiple_outcomes(
    df,
    outcomes=['return_on_assets', 'Tobin_Q', 'esg_score'],
    specifications=['entity_fe', 'time_fe', 'none']
)

# Display results as table
print(results[['outcome', 'specification', 'coefficient', 'p_value']])
```

### 3. Parallel Trends Testing

```python
# Test leads and lags of treatment
pt_results = analysis.parallel_trends_test(
    df,
    outcome='return_on_assets',
    leads=3,
    lags=3
)

# Check if pre-treatment leads are zero
for period, coef in pt_results['coefficients'].items():
    pval = pt_results['p_values'][period]
    if 'lead' in period:
        status = "✓" if pval > 0.1 else "✗"
        print(f"{status} {period}: {coef:.4f} (p={pval:.4f})")
```

### 4. Robustness Checks

```python
# Placebo test (falsification)
placebo = analysis.placebo_test(df, outcome='return_on_assets')
print(f"Placebo effect: {placebo['placebo_coefficient']:.4f}")
print(f"Valid: {placebo['is_zero_at_5pct']}")  # Should be True

# Specification sensitivity
specs = analysis.specification_sensitivity(
    df,
    outcome='return_on_assets'
)
print(specs[['specification', 'coefficient', 'p_value']])

# Comprehensive diagnostics
diagnostics = analysis.run_diagnostics_battery(
    df,
    outcome='return_on_assets'
)
```

## Utilities Module Examples

### 1. Statistical Analysis

```python
from asean_green_bonds import utils

# Effect sizes
treated = df[df['green_bond_active']==1]['return_on_assets']
control = df[df['green_bond_active']==0]['return_on_assets']

cohens_d = utils.calculate_effect_size(treated, control, method='cohens_d')
print(f"Cohen's d: {cohens_d:.4f}")

# Confidence intervals
ci = utils.calculate_confidence_interval(treated, confidence=0.95)
print(f"95% CI: [{ci[0]:.4f}, {ci[1]:.4f}]")

# Summary statistics
summary = utils.create_summary_statistics(df)
print(summary.head())
```

### 2. Visualization

```python
# Propensity score overlap
fig = utils.plot_propensity_score_overlap(
    df,
    save_path='images/ps_overlap.png'
)

# Covariate balance
balance_df = analysis.assess_balance(df, features=['L1_Firm_Size'])
fig = utils.plot_covariate_balance(
    balance_df,
    save_path='images/balance.png'
)

# DiD results
fig = utils.plot_did_results(
    results,
    save_path='images/did_effects.png'
)

# Parallel trends
fig = utils.plot_parallel_trends(
    pt_results,
    save_path='images/parallel_trends.png'
)
```

### 3. Data Validation

```python
# Panel structure validation
panel_report = utils.validate_panel_structure(df)
print(f"Balanced: {panel_report['is_balanced']}")
print(f"Missing combinations: {panel_report['missing_combinations']}")

# Data quality report
report = utils.generate_data_quality_report(df)
print(report)

# Check missing data
missing = utils.check_missing_data(df)
print(f"Total missing: {missing['total_missing_pct']:.1f}%")

# Detect outliers
outliers = utils.detect_outliers(df, method='iqr')
for col, indices in outliers.items():
    print(f"{col}: {len(indices)} outliers detected")
```

## Complete Research Workflow

### Example: Full Green Bond Impact Analysis

```python
from asean_green_bonds import data, analysis, utils, config

# ============================================================
# PHASE 1: DATA PREPARATION
# ============================================================

print("Loading data...")
df = data.load_processed_data(which='engineered')
print(f"Loaded: {df.shape}")

# Data validation
print("\nValidating data...")
report = utils.generate_data_quality_report(df)
print(report)

# ============================================================
# PHASE 2: PROPENSITY SCORE MATCHING
# ============================================================

print("\nPerforming PSM...")
df['ps'] = analysis.estimate_propensity_scores(df)

support = analysis.check_common_support(df)
print(f"Treated overlap: {support['treated_overlap_pct']:.1f}%")

matched_df, stats = analysis.nearest_neighbor_matching(
    df,
    caliper=0.1,
    ratio=4
)

balance = analysis.assess_balance(matched_df)
print("Covariate balance:")
print(balance[['Feature', 'Std_Difference']])

# ============================================================
# PHASE 3: DiD ESTIMATION
# ============================================================

print("\nEstimating treatment effects...")
outcomes = config.OUTCOME_VARIABLES
results = analysis.run_multiple_outcomes(
    matched_df,
    outcomes=outcomes
)

print("\nDiD Results:")
for outcome in outcomes:
    result = results[
        (results['outcome'] == outcome) & 
        (results['specification'] == 'entity_fe')
    ].iloc[0]
    print(f"{outcome}: β={result['coefficient']:.4f}, p={result['p_value']:.4f}")

# ============================================================
# PHASE 4: ASSUMPTION TESTING
# ============================================================

print("\nTesting assumptions...")
for outcome in outcomes:
    pt = analysis.parallel_trends_test(matched_df, outcome=outcome)
    leads = [c for c in pt['coefficients'].keys() if 'lead' in c]
    lead_sig = sum(1 for lead in leads if pt['p_values'][lead] > 0.1)
    print(f"{outcome}: {lead_sig}/{len(leads)} pre-trends not significant")

# ============================================================
# PHASE 5: ROBUSTNESS CHECKS
# ============================================================

print("\nRunning robustness checks...")
for outcome in outcomes[:1]:  # First outcome as example
    diags = analysis.run_diagnostics_battery(matched_df, outcome=outcome)
    print(f"\nPlacebo test: {diags['placebo'].get('is_zero_at_5pct')}")
    print(f"LOOCV robust: {diags['loocv'].get('robust')}")

# ============================================================
# PHASE 6: VISUALIZATION
# ============================================================

print("\nCreating visualizations...")
utils.plot_propensity_score_overlap(matched_df, save_path='images/ps.png')
utils.plot_did_results(results, save_path='images/effects.png')

print("\n✅ Analysis complete!")
```

## Advanced Usage

### Custom Feature Selection Pipeline

```python
# Tailor feature selection to your needs
selected_features, report = data.compile_selected_features(
    df,
    outcome_cols=['return_on_assets'],
    control_cols=['L1_Firm_Size', 'L1_Leverage'],
    lagged_cols=['L1_return_on_assets', 'L1_esg_score'],
    selection_method='intersection'  # Strict: only highly relevant features
)
```

### Event Study Analysis

```python
event_results = analysis.run_event_study_analysis(
    df,
    event_indicator_col='green_bond_issue',
    outcome_col='stock_return',
    entity_col='ric',
    time_col='Year',
    window_days=(-5, 5)
)

print(f"Mean AR: {event_results['overall']['significance_test']['mean_ar']:.4f}")
```

### Heterogeneous Effects

```python
# Analyze differential effects by certification
hetero = analysis.heterogeneous_effects_analysis(
    df,
    outcome='return_on_assets',
    heterogeneity_var='is_certified'
)

for subgroup, result in hetero.items():
    print(f"{subgroup}: {result['coefficient']:.4f}")
```

---

**Document Version:** 1.0  
**Last Updated:** 2026-03-18
