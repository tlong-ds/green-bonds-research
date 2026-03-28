import pandas as pd
import numpy as np
from asean_green_bonds.data.processed_loader import load_processed_data
from asean_green_bonds import config
import statsmodels.api as sm
from linearmodels.panel import PanelOLS, RandomEffects
from statsmodels.stats.diagnostic import het_breuschpagan
import warnings

warnings.filterwarnings('ignore')

# Load data
df = load_processed_data()

# Define variables
outcomes = config.OUTCOME_VARIABLES
controls = config.CONTROL_VARIABLES + config.DESCRIPTIVE_CONTROLS
main_vars = outcomes + controls

# 4.1 Descriptive Statistics
print("### TABLE 4.1: DESCRIPTIVE STATISTICS ###")
desc_full = df[main_vars].describe().T[['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']]
print("\nFULL SAMPLE:")
print(desc_full.to_markdown())

desc_treated = df[df['green_bond_active'] == 1][main_vars].describe().T[['mean', 'std']]
desc_untreated = df[df['green_bond_active'] == 0][main_vars].describe().T[['mean', 'std']]
comparison = pd.concat([desc_treated, desc_untreated], axis=1, keys=['Treated', 'Untreated'])
print("\nTREATED VS UNTREATED COMPARISON:")
print(comparison.to_markdown())

# 4.2 Correlation Analysis
print("\n### TABLE 4.2: CORRELATION MATRIX ###")
corr_matrix = df[main_vars].corr()
print(corr_matrix.to_markdown())

# 4.3 Diagnostics (using return_on_assets as representative)
print("\n### 4.3 DIAGNOSTICS (Outcome: return_on_assets) ###")

# Prepare data for linearmodels
df_reg = df.copy()
df_reg['const'] = 1
df_reg = df_reg.dropna(subset=['return_on_assets', 'green_bond_active'] + controls)
df_reg = df_reg.set_index(['org_permid', 'Year'])

Y = df_reg['return_on_assets']
X_all = df_reg[['const', 'green_bond_active'] + controls]

# Identify variables with zero within-entity variation
def get_within_variation(df, entity_col, vars):
    variation = {}
    for v in vars:
        if v == 'const':
            variation[v] = 0
            continue
        # Within variation = Var(X_it - mean(X_i))
        within_var = df.groupby(entity_col)[v].transform(lambda x: x - x.mean()).var()
        variation[v] = within_var
    return variation

within_vars = get_within_variation(df_reg.reset_index(), 'org_permid', X_all.columns)
to_drop_fe = [v for v, var in within_vars.items() if var < 1e-12 and v != 'const']

if to_drop_fe:
    print(f"\nDropping variables with zero within-firm variation for FE: {to_drop_fe}")
    X_fe = X_all.drop(columns=to_drop_fe)
else:
    X_fe = X_all

# FE Model
try:
    fe_mod = PanelOLS(Y, X_fe, entity_effects=True)
    fe_res = fe_mod.fit()
    # Check for dropped variables if the attribute exists in the results
    if hasattr(fe_res, 'dropped') and fe_res.dropped:
        print(f"Additional absorbed variables: {fe_res.dropped}")
except Exception as e:
    print(f"\nFixed Effects Model failed: {e}")
    fe_res = None

# RE Model
try:
    re_mod = RandomEffects(Y, X_all)
    re_res = re_mod.fit()
except Exception as e:
    print(f"\nRandom Effects Model failed: {e}")
    re_res = None

# Pooled OLS for LM test
pooled_mod = PanelOLS(Y, X_all)
pooled_res = pooled_mod.fit()

# Hausman Test (Approximate)
def hausman(fe, re):
    if fe is None or re is None:
        return np.nan, 0, 1.0
    # Only use non-intercept coefficients
    b = fe.params.drop('const', errors='ignore')
    B = re.params.drop('const', errors='ignore')
    
    # Align coefficients (some might be dropped in FE)
    common_idx = b.index.intersection(B.index)
    if len(common_idx) == 0:
        return np.nan, 0, 1.0
        
    b = b.loc[common_idx]
    B = B.loc[common_idx]
    
    v_b = fe.cov.loc[common_idx, common_idx]
    v_B = re.cov.loc[common_idx, common_idx]
    
    df = b.size
    diff = b - B
    cov_diff = v_b - v_B
    
    try:
        chi2 = np.dot(diff.T, np.linalg.inv(cov_diff).dot(diff))
        pval = 1 - sm.stats.distributions.chi2.cdf(chi2, df)
        return chi2, df, pval
    except:
        return np.nan, df, 1.0

if fe_res and re_res:
    res_hausman = hausman(fe_res, re_res)
    print(f"\nHausman Test: Chi2={res_hausman[0]:.4f}, df={res_hausman[1]}, p-value={res_hausman[2]:.4f}")

# F-test for FE (already in fe_res)
if fe_res:
    print(f"F-test for Fixed Effects: F={fe_res.f_pooled.stat:.4f}, p-value={fe_res.f_pooled.pval:.4f}")

# Breusch-Pagan for Heteroscedasticity
# Using residuals from pooled OLS
bp_test = het_breuschpagan(pooled_res.resids, X_all)
print(f"Breusch-Pagan Test: LM Stat={bp_test[0]:.4f}, p-value={bp_test[1]:.4f}")

# Wooldridge Test for Autocorrelation (Simple first-difference test)
# If residuals of FD regression are correlated
from linearmodels.panel import FirstDifferenceOLS
# Exclude constant as it's differenced out
X_fd = X_all.drop(columns=['const'], errors='ignore')
fd_mod = FirstDifferenceOLS(Y, X_fd)
fd_res = fd_mod.fit()
# Check AR(1) of FD residuals is usually how Wooldridge is implemented
print(f"Wooldridge Test (FD F-stat): F={fd_res.f_statistic.stat:.4f}, p-value={fd_res.f_statistic.pval:.4f}")

# Cross-Sectional Dependence (Pesaran CD)
# Average pairwise correlation of residuals
# Use FE residuals if available, otherwise Pooled OLS residuals
diag_resids = fe_res.resids if fe_res else pooled_res.resids
resids = diag_resids.reset_index()
# In linearmodels, the column name for residuals is usually the outcome name or 'residual'
res_col = [c for c in resids.columns if c not in ['org_permid', 'Year']][0]
resids_pivot = resids.pivot(index='Year', columns='org_permid', values=res_col)
corr_resids = resids_pivot.corr().values
# Filter out diagonal and NaNs
corr_vals = corr_resids[~np.eye(corr_resids.shape[0], dtype=bool)].flatten()
corr_vals = corr_vals[~np.isnan(corr_vals)]
if len(corr_vals) > 0:
    # Pesaran CD statistic: sqrt(T/(N(N-1))) * sum(sum(rho_ij))
    N = resids_pivot.shape[1]
    T = resids_pivot.shape[0]
    cd_stat = np.sqrt(T / (N * (N - 1))) * np.sum(corr_vals)
    print(f"Pesaran CD Test (Approx): Stat={cd_stat:.4f}")
else:
    print("Pesaran CD Test: Insufficient data")
