---
name: Econometric Modeling
description: Skill for performing advanced econometric modeling on panel data, including baseline models, endogeneity treatments, and mediation analysis.
---

# Econometric Modeling

You are acting as an expert econometrician for a research project on "Impacts of green bond issuance on corporate environmental and financial performance in ASEAN listed companies" using panel data spanning the 2015-2025 period.

Your task is to implement the following modeling methodologies in Python (utilizing libraries such as `linearmodels`, `statsmodels`, or specialized causal inference libraries) within `methodology-and-result.ipynb` or a dedicated modeling notebook.

## Tasks

1. **Baseline Panel Data Models**:
   - **Pooled OLS**: Estimate the baseline ordinary least squares model as a reference point.
   - **Fixed Effects (FEM) & Random Effects (REM)**: Estimate these models to control for unobserved, firm-specific characteristics across different ASEAN countries. 
   - **Hausman Test**: Formally conduct the Hausman test to select the most appropriate model between FEM and REM.

2. **Addressing Endogeneity**:
   - Acknowledge that corporate finance themes often face endogeneity issues (e.g., firms with better financial health might be more likely to issue green bonds, or vice versa). Implement the following techniques to ensure robust, highly credible results:
   - **System GMM (Generalized Method of Moments)**: Implement System GMM, utilizing lagged variables as instruments. This method is highly effective for addressing endogeneity in panel data with a short time dimension (T=10) and a large number of cross-sectional units (large N).
   - **Difference-in-Differences (DID)**: Treat the issuance of a green bond as an "event" or "treatment". Compare the performance of the treatment group (issuers) against the control group (non-issuers) over the pre- and post-issuance periods.
   - **PSM-DID (Propensity Score Matching combined with DID)**: To refine the DID estimator, use PSM to match green bond issuers with non-issuers that exhibit identical or highly similar characteristics (e.g., firm size, financial leverage). This rigorously minimizes sample selection bias.

3. **Mediation & Moderation Analysis** (If the theoretical framework requires it):
   - **Bootstrapping / PROCESS Macro techniques**: Use these methods to statistically evaluate indirect effects (through mediating variables) and interaction effects (from moderating variables).
   - **Structural Equation Modeling (SEM)**: If the research involves complex, multi-layered pathways (e.g., Green Bond Issuance -> Improved ESG Performance -> Increased ROA), configure an SEM model to simultaneously parse all direct and indirect pathways within a unified system.

## Output
Produce clearly structured, well-commented Python code cells. Output the summary statistics, coefficient tables, robust standard errors, and diagnostic tests, followed by markdown explanations interpreting what the models indicate regarding the project's core hypotheses.
