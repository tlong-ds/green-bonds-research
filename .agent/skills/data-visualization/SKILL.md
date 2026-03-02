---
name: Data Visualization
description: Skill for generating insightful visualizations for panel data analysis, exploring trends, distributions, and relationships.
---

# Data Visualization

You are acting as an expert Data Scientist and Data Visualizer for the econometrics research project "Impacts of green bond issuance on corporate environmental and financial performance in ASEAN listed companies".

Your task is to create clear, publication-quality visualizations to understand the dataset's characteristics, time-series trends, and potential causal relationships.

## Tasks
1. **Trend Analysis (Time-Series)**:
   - Create line plots showing the average trajectory of core financial variables (e.g., `return_on_assets`, `return_on_equity_total`, `total_assets`) and ESG metrics (`emissions_intensity`) across the years (2015-2025). 
   - Aggregate these trends at the ASEAN level and also breakdown by `country`.
2. **Distribution & Outlier Analysis**:
   - Generate boxplots or violin plots for key continuous variables before and after winsorization to visualize the distribution and extent of outliers.
   - Compare the distribution of financial and environmental metrics across different countries using grouped bar charts or density plots.
3. **Treatment vs. Control Comparison (DID visual pre-check)**:
   - If green bond issuance indicators are available, plot parallel trend graphs comparing the average performance of issuers (treatment) versus non-issuers (control) over time. This provides visual intuition before running the formal DID models.
4. **Correlation Visualization**:
   - Produce a visually appealing correlation heatmap (using `seaborn`) to explore multicollinearity among independent variables and the relationship between continuous dependent and independent variables.

## Output Requirements
All your code, markdown analysis, and generated charts should be outputted and saved in a new Jupyter Notebook named `visualization.ipynb` located in the root directory. Do NOT modify `data-processing.ipynb` for these tasks. Use libraries like `matplotlib`, `seaborn`, or `plotly` to ensure the visualizations are crisp and highly informative.
