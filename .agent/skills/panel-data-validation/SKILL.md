---
name: Panel Data Validation
description: Skill for structurally validating the firm-year panel dataset.
---

# Panel Data Validation

As an expert econometrician and data scientist, you must validate the integrity of the firm-year panel data structure before it is passed into linear or fixed effects models.

## Tasks
1. **Set Multi-Index**: Use pandas to set the DataFrame index to `['isin', 'Year']` or `['ric', 'Year']` to explicitly structure it as panel data.
2. **Check Unbalanced Panel**: Identify if the panel is severely unbalanced. Report the average number of observation years per firm and the overall temporal range. Dropping observations might be necessary if a firm has too few contiguous years.
3. **Descriptive Statistics**: Generate a summary table displaying count, mean, standard deviation, min, max, skewness, and kurtosis to inspect the distributional properties of the panel after formatting. This is the "Table 1" required in most econometric papers.
4. **Correlation Matrix**: Produce a correlation matrix (Pearson/Spearman) of the primary variables to check for multicollinearity issues prior to regression analysis.

## Output
Produce markdown and code cells in `data-processing.ipynb` summarizing the structural integrity and basic statistical properties of the panel dataset.
