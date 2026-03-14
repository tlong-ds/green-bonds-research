---
name: Data Visualization
description: Causal and trend visualizations for ASEAN Green Bonds research.
---

# Data Visualization (ASEAN Green Bonds)

Create publication-quality visualizations to explore trends and causal relationships in the Green Bonds dataset.

## Tasks

1. **Parallel Trends Check**:
   - Plot average `ROA` and `Tobin's Q` over time for issuers vs. non-issuers. The pre-issuance period should show roughly parallel trajectories.
2. **Regional Heterogeneity (H4)**:
   - Create multi-panel plots (facet by `Country`) showing the growth of green bond issuance volumes and average firm performance.
3. **Distribution of "Greenium"**:
   - Visualize the distribution of yield spreads (or proxies) for certified vs. self-labeled green bonds to highlight "greenwashing" risks.
4. **Correlation Heatmap**:
   - Use a specialized color palette to show relationships between financial performance, ESG scores, and the DiD estimator.

## Output

Save all charts to `visualization.ipynb`. Ensure high resolution and professional academic formatting (e.g., using `seaborn` with `style='whitegrid'`).
