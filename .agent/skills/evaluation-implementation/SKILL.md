---
name: Evaluation Implementation
description: Skill for reviewing an evaluation report and methodically fixing code issues in the data processing pipeline based on the report's findings.
---

# Evaluation Implementation

You are an expert Data Engineer and Python Developer. Your task is to review a provided evaluation report (specifically addressing `data-processing.ipynb` or related pipeline scripts) and systematically implement the recommended fixes to the codebase.

## Instructions

1.  **Review the Report:** Carefully read the provided evaluation report (like `evaluation_report.md`) to comprehensively understand the identified issues, warnings, and prioritized action items. Pay special attention to critical issues that impact data integrity or econometric validity.
2.  **Locate the Code:** Identify which files contain the code that needs to be fixed. This could be Jupyter Notebooks (e.g., `notebooks/data-processing.ipynb`), data extraction scripts (e.g., `data-preparation.py`), or scripts that generate notebook cells (e.g., `add_cleaning_cells.py`, `add_engineering_cells.py`).
3.  **Plan the Fixes:** Formulate a step-by-step plan to implement the prioritized action items. Address the critical issues first, such as:
    *   **Currency Conversion Logic:** Ensure ratios (like ROA, ROE, margins, emissions intensity) are EXCLUDED from currency conversion.
    *   **Winsorization Ordering:** Ensure winsorization happens AFTER currency conversion, so values are in a common currency before outlier trimming.
    *   **Merge Logic:** Correct many-to-many merges (e.g., `isin` to `ric` mappings) to avoid row inflation and invalid data pairing. Deduplicate correctly.
    *   **Dummy Encoding:** Fix `pd.get_dummies` usage on columns with 'Y'/'N'/NaN to ensure NaNs aren't incorrectly mapped as 'N'.
    *   **Missing Data Handling:** Review aggressive filtering rules (like dropping all rows where `total_assets` is NaN after ffill) to minimize survivorship bias and unnecessary data loss.
    *   **Data Types:** Ensure early conversion of numerical columns before aggregation or imputation logic.
4.  **Implement the Fixes:**
    *   Use appropriate file editing tools to modify the code accurately.
    *   Ensure that any pandas code modifications adhere to best practices for data alignment and broadcasting.
    *   If editing a Jupyter Notebook, ensure you maintain the strict dictionary/JSON structure of the `.ipynb` file.
5.  **Verify Changes:** Double-check your modifications to ensure they directly resolve the root causes detailed in the evaluation report without introducing new syntax or logical errors.
6.  **Report Progress:** Provide a summary of the fixes implemented to the user, mapping each code change back to the corresponding issue in the evaluation report.
