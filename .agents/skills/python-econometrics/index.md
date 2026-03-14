---
name: python-econometrics
description: Run IV, DiD, and RDD analyses in Python with proper diagnostics
workflow_stage: analysis
compatibility:
  - claude-code
  - cursor
  - codex
  - gemini-cli
author: Awesome Econ AI Community
version: 1.0.0
tags:
  - Python
  - econometrics
  - causal-inference
  - fixest
  - regression
---

# Python Econometrics

## Purpose

This skill helps economists run rigorous econometric analyses in Python, including Instrumental Variables (IV), Difference-in-Differences (DiD), and Regression Discontinuity Design (RDD). It generates publication-ready code with proper diagnostics and robust standard errors.

## When to Use

- Running causal inference analyses
- Estimating treatment effects with panel data
- Creating publication-ready regression tables
- Implementing modern econometric methods (two-way fixed effects, event studies)

## Instructions

### Step 1: Understand the Research Design

Before generating code, ask the user:
1. What is your identification strategy? (IV, DiD, RDD, or simple regression)
2. What is the unit of observation? (individual, firm, country-year, etc.)
3. What fixed effects do you need? (entity, time, two-way)
4. How should standard errors be clustered?

### Step 2: Generate Analysis Code

Based on the research design, generate R code that:

1. **Uses the `fixest` package** - Modern, fast, and feature-rich for panel data
2. **Includes proper diagnostics:**
   - For IV: First-stage F-statistics, weak instrument tests
   - For DiD: Parallel trends visualization, event study plots
   - For RDD: Bandwidth selection, density tests
3. **Uses robust/clustered standard errors** appropriate for the data structure
4. **Creates publication-ready output** using `modelsummary` or `etable`

### Step 3: Structure the Output

Always include:
```r
# 1. Setup and packages
# 2. Data loading and preparation
# 3. Descriptive statistics
# 4. Main specification
# 5. Robustness checks
# 6. Visualization
# 7. Export results
```

### Step 4: Add Documentation

Include comments explaining:
- Why each specification choice was made
- Interpretation of key coefficients
- Limitations and assumptions

## Example Prompts

- "Run a DiD analysis with state and year fixed effects, clustering at the state level"
- "Estimate the effect of X on Y using Z as an instrument"
- "Create an event study plot showing treatment effects by year"
- "Run a sharp RDD with optimal bandwidth selection"

## Example Output

```python
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from linearmodels import PanelOLS

# Load and prepare data
df = pd.read_csv("data.csv").set_index(['firm_id', 'year'])

# Two-way fixed effects DiD
mod = PanelOLS.from_formula('outcome ~ treatment + EntityEffects + TimeEffects', data=df)
results = mod.fit(cov_type='clustered', cluster_entity=True)

# View results summary
print(results.summary)
```

## Best Practices

1. **Always cluster standard errors** at the level of treatment assignment
2. **Run pre-trend tests** for DiD designs
3. **Report first-stage F-statistics** for IV (should be > 10)
4. **Use `feols` over `lm`** for panel data (faster and more features)
5. **Document all specification choices** in your code comments

## Common Pitfalls

- ❌ Not clustering standard errors at the right level
- ❌ Ignoring weak instruments in IV estimation
- ❌ Using TWFE with staggered treatment timing (use `did` or `sunab()` instead)
- ❌ Not reporting robustness checks

## References

- [fixest documentation](https://lrberge.github.io/fixest/)
- [Cunningham (2021) Causal Inference: The Mixtape](https://mixtape.scunning.com/)
- [Angrist & Pischke (2009) Mostly Harmless Econometrics](https://www.mostlyharmlesseconometrics.com/)

## Changelog

### v1.0.0
- Initial release with IV, DiD, RDD support
