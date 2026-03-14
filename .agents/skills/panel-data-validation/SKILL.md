---
name: Panel Data Validation
description: Structural validation of the ASEAN firm-year panel dataset (2015-2025).
---

# Panel Data Validation (ASEAN Green Bonds)

Validate the integrity of the firm-year panel data before econometric estimation.

## Tasks

1. **Panel Structure**:
   - Set the index to `RIC` (or `ISIN`) and `Year`.
   - Identify if the panel is balanced or unbalanced. Report the average T (number of years) per firm.
2. **Descriptive Statistics (Table 1)**:
   - Generate a table for: `ROA (%)`, `Tobin's Q`, `Firm Size`, `Leverage Ratio`, `Asset Turnover`, `Liquidity`, and `ESG Score`.
   - Include: Mean, Median, Std Dev, Min, and Max.
3. **Check Sample Scope**:
   - Verify that financial institutions are **excluded** (Sector Exclusion criteria).
   - Ensure firms have continuous data across the observational window (2015-2025).
4. **Treatment Verification**:
   - Count the number of unique Green Bond issuers across for each ASEAN country (Indonesia, Malaysia, Philippines, Singapore, Thailand, Vietnam).

## Output

Produce Table 1 (Descriptive Statistics) and a summary of the exclusion criteria results in a markdown report.
