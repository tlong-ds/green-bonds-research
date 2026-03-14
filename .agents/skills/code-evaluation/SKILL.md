---
name: Code Evaluation
description: Critical review of the econometric pipeline for the ASEAN Green Bonds project.
---

# Code Evaluation (ASEAN Green Bonds)

Perform a rigorous review of the data and modeling steps to ensure statistical validity.

## Tasks

1. **Bias Detection**:
   - Check for **Survivorship Bias** in the sample selection.
   - Verify if "Greenwashing" is addressed by differentiating between certified and self-labeled bonds.
2. **Model Robustness**:
   - Review the choice of instruments in System GMM.
   - Audit the PSM matching quality (check for "common support" region).
3. **Statistical Integrity**:
   - Ensure standard errors are **clustered at the firm level** to account for serial correlation within panel units.

## Output

Generate a detailed evaluation report highlighting potential "handicaps" in the data (e.g., inconsistent ESG disclosures in certain ASEAN markets).
