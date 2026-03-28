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
outcomes = ['return_on_assets', 'Tobin_Q', 'esg_score', 'ln_emissions_intensity']
controls = ['L1_Firm_Size', 'L1_Leverage', 'L1_Asset_Turnover', 'L1_Capital_Intensity', 'L1_Cash_Ratio']
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
X = df_reg[['const', 'green_bond_active'] + controls]

# FE Model
fe_mod = PanelOLS(Y, X, entity_effects=True)
fe_res = fe_mod.fit()

# RE Model
re_mod = RandomEffects(Y, X)
re_res = re_mod.fit()

# Pooled OLS for LM test
pooled_mod = PanelOLS(Y, X)
pooled_res = pooled_mod.fit()

# Hausman Test (Approximate)
def hausman(fe, re):
    # Only use non-intercept coefficients
    b = fe.params.drop('const', errors='ignore')
    B = re.params.drop('const', errors='ignore')
    v_b = fe.cov.drop('const', axis=0, errors='ignore').drop('const', axis=1, errors='ignore')
    v_B = re.cov.drop('const', axis=0, errors='ignore').drop('const', axis=1, errors='ignore')
    
    # Check for empty coefficients (can happen if treatment absorbed)
    if b.empty:
        return np.nan, 0, 1.0
        
    df = b.size
    diff = b - B
    cov_diff = v_b - v_B
    
    try:
        chi2 = np.dot(diff.T, np.linalg.inv(cov_diff).dot(diff))
        pval = 1 - sm.stats.distributions.chi2.cdf(chi2, df)
        return chi2, df, pval
    except:
        return np.nan, df, 1.0

res_hausman = hausman(fe_res, re_res)
print(f"\nHausman Test: Chi2={res_hausman[0]:.4f}, df={res_hausman[1]}, p-value={res_hausman[2]:.4f}")

# F-test for FE (already in fe_res)
print(f"F-test for Fixed Effects: F={fe_res.f_pooled.stat:.4f}, p-value={fe_res.f_pooled.pval:.4f}")

# Breusch-Pagan for Heteroscedasticity
# Using residuals from pooled OLS
bp_test = het_breuschpagan(pooled_res.resids, X)
print(f"Breusch-Pagan Test: LM Stat={bp_test[0]:.4f}, p-value={bp_test[1]:.4f}")

# Wooldridge Test for Autocorrelation (Simple first-difference test)
# If residuals of FD regression are correlated
from linearmodels.panel import FirstDifferenceOLS
fd_mod = FirstDifferenceOLS(Y, X.drop(columns=['const']))
fd_res = fd_mod.fit()
# Check AR(1) of FD residuals is usually how Wooldridge is implemented
print(f"Wooldridge Test (FD F-stat): F={fd_res.f_statistic.stat:.4f}, p-value={fd_res.f_statistic.pval:.4f}")

# Cross-Sectional Dependence (Pesaran CD)
# Average pairwise correlation of residuals
resids = fe_res.resids.reset_index()
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
