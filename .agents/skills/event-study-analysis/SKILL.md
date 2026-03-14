---
name: Event Study Analysis
description: Skill for conducting event studies to measure stock market reactions to Green Bond announcements.
---

# Event Study Analysis (ASEAN Green Bonds)

You are acting as a Financial Research Analyst. Your task is to implement an event study to measure the "immediate stock market equity reactions" mentioned in the research outline (Page 13).

## Tasks

1. **Event Definition**:
   - Identify the event date (announcement date of green bond issuance).
   - Define the **Estimation Window** (e.g., 250 days prior to the event) and the **Event Window** (e.g., [-1, +1] or [-10, +10] days).
2. **Normal Return Estimation**:
   - Use the **Market Model**: `R_{it} = \alpha_i + \beta_i R_{mt} + \epsilon_{it}`, where `R_{mt}` is a regional index (e.g., MSCI ASEAN).
   - (Advanced) Use a GARCH model if high volatility is detected in the ASEAN markets.
3. **Abnormal Return (AR) Calculation**:
   - Compute `AR_{it} = R_{it} - E(R_{it})`.
   - Calculate **Cumulative Abnormal Returns (CAR)** over the event window.
4. **Statistical Significance**:
   - Perform t-tests or Patell's Z-test to determine if the CAR is statistically different from zero.
5. **Greenwashing Check**:
   - Compare CARs for certified green bonds vs. self-labeled bonds to see if the market penalizes non-certified issuances.

## Output

Generate a set of results (AR/CAR tables) and an event study plot showing the cumulative effect over the window.
