---
name: ESG Sentiment Analysis
description: Skill for analyzing the sentiment and "greenwashing" signals in corporate disclosures.
---

# ESG Sentiment Analysis (ASEAN Green Bonds)

You are acting as an NLP Specialist in sustainable finance. Your goal is to extract signals from unstructured text data (prospectuses, reports) to complement the quantitative analysis.

## Tasks

1. **Content Extraction**:
   - Parse PDF prospectuses for "Use of Proceeds" and "Environmental Targets".
2. **Sentiment Scoring**:
   - Use a finance-specific sentiment lexicon (e.g., Loughran-McDonald) or a transformer model (e.g., FinBERT) to score the commitment level in disclosures.
3. **Greenwashing Detection**:
   - Identify "boilerplate" language or vague environmental claims.
   - Cross-reference textual claims with quantitative GHG emission trajectories from the dataset.
4. **Moderator Analysis**:
   - Create a "Sentiment Score" variable to be used as a moderator in the DiD regression (`DiD * Sentiment`).

## Output

Add a notebook (`text-analysis.ipynb`) that extracts these scores and merges them back into the main panel dataset.
