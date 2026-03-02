import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv('processed_data/final_data.csv')

# Let's see if we can impute total_assets based on other financial variables
# We need to make sure we don't impute across years blindly, or we might introduce lookahead bias.
# For KNN, we'll impute cross-sectionally by year, or using a set of highly correlated variables.

print("Original shape:", df.shape)
print("Missing TA:", df['total_assets'].isna().sum())

# Only keep rows where we have at least SOME financial info
# For example, if a firm has market_capitalization, net_sales, etc., we can impute TA.
financial_cols = ['market_capitalization', 'net_sales_or_revenues', 'cash', 'total_assets']
df_fin = df[financial_cols].copy()

print("Firms with all financial cols missing:", df_fin.isna().all(axis=1).sum())

# KNN Imputation
imputer = KNNImputer(n_neighbors=5)
# Note: KNN Imputer takes a long time on large datasets. Let's run a small sample to test.
sample = df_fin.head(1000)
imputed = imputer.fit_transform(sample)
print("Imputed sample shape:", imputed.shape)

