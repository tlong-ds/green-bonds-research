# CHAPTER V. CONCLUSIONS AND IMPLICATIONS

## 5.1. General Conclusions

This study examined whether green bond issuance generates measurable financial and environmental benefits for listed companies across six ASEAN member states between 2020 and 2025. The empirical evidence, derived from a rigorous three-stage identification strategy integrating Propensity Score Matching, Difference-in-Differences estimation, and System GMM robustness checks, yields three overarching conclusions that bear directly on the research questions and hypotheses established in Chapters 1 and 2.

### 5.1.1. Research Question 1: Internal Profitability (ROA)

**Does green bond issuance lead to a statistically significant improvement in the internal profitability of ASEAN listed firms, as measured by Return on Assets (ROA)?**

**Conclusion**: **No.**

The study finds **no causal evidence** that green bond issuance improves accounting-based profitability. Across all five DiD specifications (Entity FE, Time FE, TWFE, Entity FE + Trend, Pooled OLS), the treatment effect on ROA is statistically indistinguishable from zero. The preferred Two-Way Fixed Effects (TWFE) estimate yields $\beta = -0.006$ ($p = 0.756$), while the more conservative System GMM estimate is $\beta = -0.002$ ($p = 0.822$). Cohort-specific analysis (Callaway & Sant'Anna, 2021) corroborates this null finding: the aggregated Average Treatment Effect on the Treated (ATT) across cohorts is $\beta = -0.014$ ($p = 0.315$), with zero pre-trend violations among testable cohorts (2022–2024).

This null result is robust to alternative specifications, subsample restrictions, and dynamic panel estimation, indicating that the absence of a profitability effect is not an artifact of model misspecification or uncontrolled confounding. The finding directly contradicts **Hypothesis H2a** (positive impact on accounting performance) and suggests that within the 6-year observation window, green bond issuance in ASEAN does not translate into superior asset utilization or operational cost savings.

**Interpretation**: Green bond issuance may impose **short-run compliance costs** (e.g., reporting infrastructure, third-party verification, green project management) that offset any operational efficiency gains. Alternatively, the benefits of green investments may materialize over longer horizons than the 6-year panel captures. The evidence is consistent with green bonds functioning as a **credibility signal** to stakeholders rather than an operational transformation catalyst in the ASEAN context.

### 5.1.2. Research Question 2: Market Valuation (Tobin's Q)

**How does the market value of a firm, represented by Tobin's Q, respond to the signaling effect of green bond issuance over time?**

**Conclusion**: **Weak and specification-sensitive evidence of a positive market premium, not robust to entity fixed effects.**

Under Time Fixed Effects specification, green bond issuance is associated with a marginally significant positive coefficient ($\beta = 0.341$, $p = 0.080$†), suggesting a potential market premium. However, this effect **disappears** when entity fixed effects are included. The preferred TWFE specification yields $\beta = 0.494$ ($p = 0.207$), directionally positive but statistically insignificant. System GMM produces a smaller and insignificant estimate ($\beta = 0.063$, $p = 0.715$).

**Interpretation**: The positive association under Time FE likely reflects **selection on firm quality**: firms that issue green bonds are systematically different from non-issuers in ways that correlate with higher market valuation (e.g., superior governance, strategic foresight, stakeholder engagement). Once these time-invariant firm characteristics are controlled for via entity fixed effects, the "green premium" largely dissipates.

This pattern provides **weak and conditional support** for **Hypothesis H2b** (positive impact on market valuation). While the market may assign a modest valuation premium to green bond issuers in the short run—consistent with signaling theory (Flammer, 2021)—this premium is not robustly identified once firm-level heterogeneity is accounted for. The evidence suggests that any market reaction to green bond issuance is driven primarily by the **selection of high-quality firms into green finance** rather than a causal revaluation triggered by the issuance event itself.

### 5.1.3. Research Question 3: Environmental Outcomes — Material Improvement or Greenwashing?

**To what extent do environmental outcomes improve following bond issuance, and does the empirical evidence support a hypothesis of "material improvement" or a "greenwashing" narrative?**

**Conclusion**: **Evidence supports a structural greenwashing pattern characterized by near-universal certification but negligible verified environmental improvement.**

The study's authenticity scoring framework, applied to 333 ASEAN green bonds, reveals a striking contradiction:
- **98.5% of bonds** carry third-party certification (CBI or ICMA)
- **Only 3.9% of bonds** demonstrate verifiable ESG improvement post-issuance

This decoupling between procedural compliance (certification) and substantive environmental outcomes (ESG divergence, emissions reduction) is the defining characteristic of **systemic greenwashing** (Khan & Vismara, 2025).

**ESG Score Analysis**: DiD estimates for ESG scores are positive but statistically insignificant across all specifications. The TWFE estimate is $\beta = 0.037$ ($p = 0.604$), while System GMM yields $\beta = 0.004$ ($p = 0.803$). Cohort-specific analysis produces an aggregated ATT of $\beta = 0.059$ ($p = 0.292$). Positive effects observed under Time FE ($\beta = 0.187$, $p < 0.001$) are **spurious**, driven by sector-wide ESG reporting trends rather than issuer-specific treatment effects.

**Emissions Intensity Analysis**: The treatment effect on log emissions intensity is directionally negative across all methods (DiD: $\beta = -0.057$, $p = 0.734$; GMM: $\beta = -0.058$, $p = 0.651$), **consistent with a reduction in carbon intensity** following green bond issuance. However, the effects are **not statistically significant** in any specification, preventing a definitive conclusion. The point estimates suggest a potential 5.6–5.8% reduction in emissions intensity, but this effect cannot be distinguished from noise given the sample size and short post-issuance window.

**Hypothesis H1 (Environmental Performance)**: The evidence provides **partial but inconclusive support**. While directional consistency across DiD and GMM for emissions intensity is encouraging, the absence of statistical significance prevents rejection of the null hypothesis of no effect. The greenwashing analysis reveals that **certification does not guarantee impact**, and the majority of ASEAN green bonds (96.1%) fail to demonstrate verifiable environmental improvement.

**Interpretation**: Green bond certification in ASEAN functions primarily as a **credentialing mechanism** that facilitates access to ESG-mandated capital pools and enhances reputational positioning. The current certification architecture—focused on use-of-proceeds verification rather than outcome accountability—enables a market equilibrium in which procedural compliance substitutes for substantive environmental transformation. Until certification standards incorporate **mandatory post-issuance emissions reporting** and **performance-based verification**, the expansion of ASEAN green bond volumes will not reliably translate into measurable environmental benefits.

### 5.1.4. Research Question 4: Statistical Stability and Persistence

**Are the observed impacts of green bonds persistent and statistically stable when accounting for dynamic endogeneity and unobservable entity-fixed effects?**

**Conclusion**: **Yes. The null findings are robust across all estimation strategies and diagnostic tests.**

The study implemented multiple robustness checks to assess the stability of results:

1. **Cross-Method Consistency**: DiD (TWFE) and System GMM yield directionally consistent estimates for all four primary outcomes (ROA, Tobin's Q, ESG Score, Emissions Intensity). None achieve statistical significance in either framework.

2. **Specification Robustness**: Results are stable across five DiD specifications. Effects that appear significant under Time FE or Pooled OLS (e.g., ESG score, Tobin's Q) disappear upon inclusion of entity fixed effects, confirming that these associations reflect selection bias rather than causal effects.

3. **Parallel Trends Validity**: Among cohorts with sufficient pre-treatment data (2022–2024), parallel trends tests reveal **zero pre-trend violations** for ROA. This supports the credibility of DiD identification for the testable subset of treated firms.

4. **GMM Validity Diagnostics**: All System GMM estimates pass Arellano-Bond AR(2) tests (insignificant, validating instrument exogeneity) and Hansen overidentification tests (not rejected, consistent with valid instruments).

5. **Cohort-Specific Heterogeneity**: Callaway & Sant'Anna (2021) decomposition confirms that null findings are not driven by treatment effect heterogeneity across cohorts. Aggregated ATTs are insignificant for all outcomes.

**Conclusion**: The absence of detectable treatment effects is not an artifact of methodological limitations, short-run noise, or dynamic panel bias. The null findings are **statistically robust and persistent** across identification strategies, supporting the conclusion that green bond issuance in ASEAN, as currently structured, does not causally improve financial or environmental performance within observable horizons.

---

## 5.2. Implications and Recommendations

### 5.2.1. Theoretical Implications

This study makes three contributions to the sustainable finance literature:

**1. Selection vs. Treatment Effects in Green Finance**  
The finding that positive associations between green bond issuance and corporate performance (e.g., ESG scores, market valuation) disappear once entity fixed effects are introduced provides strong evidence that prior cross-sectional studies may have **overstated causal effects** by conflating selection and treatment. Firms that issue green bonds are not randomly selected; they are systematically larger, more levered, and have stronger baseline ESG performance. Failure to account for this selection via fixed effects or matching inflates treatment effect estimates.

**Implication for Future Research**: Panel methods with entity fixed effects or within-firm variation should be the methodological standard for evaluating green finance interventions. Cross-sectional comparisons are insufficient for causal inference.

**2. Certification ≠ Impact**  
The near-perfect certification rate (98.5%) coexisting with minimal verified improvement (3.9%) challenges the implicit assumption in much of the green bond literature that **certification serves as a credible proxy for environmental impact**. This study demonstrates that use-of-proceeds certification (CBI/ICMA) validates process compliance but does not ensure outcome delivery.

**Implication for Theory**: Signaling theory (Flammer, 2021) must distinguish between **credibility signals** (certification, frameworks) and **performance signals** (verifiable emissions reductions). The ASEAN evidence suggests that the former can exist without the latter, undermining the theoretical link between green credentials and operational transformation.

**3. Institutional Context Moderates Green Bond Effectiveness**  
The null findings for ASEAN contrast with positive effects documented in developed markets (Flammer, 2021; Tang & Zhang, 2020). This divergence underscores the importance of **institutional preconditions** for green bond effectiveness:
- Enforcement of environmental regulations
- Mandatory emissions disclosure and public reporting
- Investor sophistication and demand for impact verification
- Penalties for greenwashing

**Implication for Theory**: The effectiveness of green bonds is not universal but **contingent on institutional quality**. Theoretical models should incorporate institutional variables (regulatory stringency, disclosure mandates, enforcement capacity) as moderators of green finance impacts.

### 5.2.2. Policy Implications for ASEAN Regulators

The central policy implication is clear: **ASEAN green bond standards must transition from process-based to outcome-based certification**.

**Recommendation 1: Mandate Post-Issuance Impact Reporting**  
Require all green bond issuers to publish annual impact reports documenting:
- Direct GHG emissions (Scope 1, 2) and emissions intensity
- Energy consumption from renewable vs. non-renewable sources
- Quantifiable environmental KPIs aligned with project categories (e.g., MW of renewable energy capacity installed, tons of waste diverted from landfills, hectares of land restored)

**Rationale**: Procedural verification of proceeds allocation is necessary but insufficient. Without outcome accountability, certification becomes a **reputational good** decoupled from environmental delivery.

**Recommendation 2: Establish Public Green Bond Impact Registry**  
Create a centralized, publicly accessible database compiling post-issuance environmental performance data for all ASEAN green bonds.

**Benefits**:
- **Transparency**: Enables investors, researchers, and civil society to assess actual impact
- **Market Discipline**: Creates competitive pressure on issuers to demonstrate genuine performance
- **Data Infrastructure**: Facilitates future empirical research and meta-analyses of green bond effectiveness

**Recommendation 3: Introduce Tiered Certification Standards**  
Recognize that firm heterogeneity (size, resources, sector) creates differential capacity for environmental transformation. A tiered approach could:
- **Tier 1 (Outcome-Verified)**: Certification contingent on achieving quantified emissions reduction targets
- **Tier 2 (Process-Verified)**: Current use-of-proceeds certification for smaller issuers
- **Tier 3 (Framework-Only)**: Disclosure of green bond framework without third-party verification

**Rationale**: A uniform standard imposes disproportionate costs on smaller firms and risks creating a two-tier market where only large firms can credibly issue green bonds. Tiering aligns disclosure and verification requirements with issuer capacity.

### 5.2.3. Managerial Implications for Corporate Issuers

**Implication 1: Green Bonds as Long-Run Organizational Investments**  
Managers should reframe green bond issuance from a **cost-of-capital optimization** to a **long-run investment in sustainability infrastructure**. The evidence indicates that short-run profitability effects are null or negative (compliance cost drag), but this does not imply green bonds are value-destroying.

**Strategic Recommendation**: Embed green bond issuance within a broader ESG transformation strategy that includes:
- **Specific, quantifiable environmental targets** (e.g., 20% reduction in Scope 1+2 emissions by 2030)
- **Executive accountability mechanisms** (e.g., linking executive compensation to ESG KPIs)
- **Operational governance structures** (e.g., board-level sustainability committees with veto power over high-emission capital expenditures)

**Evidence from Japan** (Bai, 2025): Japanese firms that combine green bond issuance with binding environmental targets achieve significant emissions reductions; those that issue bonds without targets do not. **Lesson**: Certification alone is insufficient; operational commitment is the mechanism through which green bonds generate impact.

**Implication 2: Differentiation via Verified Impact**  
In a market where 98.5% of bonds are certified, certification no longer differentiates issuers. **Competitive advantage** will accrue to firms that can credibly demonstrate **verified environmental improvement**.

**Recommendation**: Voluntarily adopt **impact-linked reporting** that goes beyond minimum disclosure requirements:
- Publish Scope 1, 2, and 3 emissions annually
- Commission third-party verification of environmental outcomes (e.g., carbon intensity reductions)
- Make impact data publicly accessible (e.g., via sustainability reports, investor presentations)

**Market Signal**: Firms that transparently report verified impact will attract capital from sophisticated ESG investors who price the difference between certified-only and certified-and-verified bonds.

### 5.2.4. Investor Implications

**Implication for ESG-Mandated Investors**:  
A certification rate of 98.5% alongside a verified improvement rate of 3.9% means that **the certification label is not a reliable proxy for impact**. Investors relying solely on CBI or ICMA certification risk allocating capital to bonds that satisfy procedural requirements without delivering environmental outcomes.

**Recommendation**: Supplement use-of-proceeds verification with **post-issuance performance requirements** as a condition of continued investment or preferential pricing:
- Require annual emissions reporting for all green bond holdings
- Implement **impact-linked covenants**: e.g., if emissions intensity does not decline by X% within Y years, issuer must repurchase bonds at par or pay a penalty coupon
- Demand access to project-level impact data (e.g., energy generation from financed solar projects)

**Market Mechanism**: If capital markets begin to price the difference between certified-but-unverified and certified-and-verified issuances—e.g., via lower yields for bonds with binding impact commitments—issuers will face a direct financial incentive to close the certification-impact gap.

### 5.2.5. Recommendations for Companies in Vietnam

Vietnam faces a distinctive combination of **climate urgency** (ranked among the world's most climate-vulnerable economies; COP26 Net Zero 2050 signatory) and **institutional immaturity** (nascent disclosure infrastructure, limited investor sophistication, weak enforcement of environmental regulations). The study's findings generate three concrete priorities for Vietnamese issuers:

**Priority 1: Build Organizational Capacity Before Entering the Market**  
The heterogeneity analysis (Section 4.5.4) demonstrates that **smaller, less-prepared issuers risk generating a negative market signal** from premature green bond issuance. For Vietnamese companies, the pre-issuance period should be treated as an **investment phase**:

- Establish **dedicated sustainability governance** at the board level (e.g., ESG committee with independent expertise)
- Implement **comprehensive GHG accounting** across Scopes 1 and 2 (ISO 14064 standard)
- Develop an **internal green bond framework** with specific, quantifiable environmental targets
- Build **reporting infrastructure** to demonstrate progress over time (annual impact reports, third-party assurance)

**Rationale**: This groundwork is not a compliance formality; it is the organizational foundation from which genuine performance benefits can emerge. Issuing green bonds without this infrastructure risks reputational damage and fails to capture the strategic benefits of green finance.

**Priority 2: Adopt Sector-Specific, Binding Environmental Targets**  
Vietnamese listed companies are concentrated in sectors with high environmental materiality:
- **Real Estate Developers**: Commit to internationally recognized green building certifications (LEED Gold/Platinum, EDGE) with quantified energy and water efficiency targets
- **Manufacturing Firms**: Establish absolute Scope 1 and 2 GHG reduction commitments verified annually by accredited third parties (e.g., 15% reduction by 2030 from 2020 baseline)
- **Banks Issuing Green Bonds for On-Lending**: Implement impact-linked reporting that tracks end-use environmental outcomes at the project level (e.g., MW of renewable energy capacity financed, tons of CO2 avoided), not just eligibility verification at origination

**Make Targets Binding**: Embed targets in:
- **Contractual covenants** (e.g., failure to meet targets triggers repurchase obligation)
- **Public disclosure obligations** (annual sustainability reports with third-party assurance)
- **Executive compensation linkages** (ESG KPIs as 20–30% of variable pay)

**Priority 3: Engage Actively in Building National Monitoring Architecture**  
The structural greenwashing pattern documented in this study cannot be resolved by individual firms acting unilaterally; it requires a **national monitoring infrastructure** that does not yet exist in Vietnam.

**Recommendation**: Large state-owned enterprises and prominent private conglomerates that issue green bonds should advocate for—and participate in designing—a **National Green Bond Impact Registry**:
- Publicly accessible platform compiling post-issuance environmental performance data for all Vietnamese issuers
- Standardized reporting templates aligned with international standards (GRI, TCFD)
- Annual publication of aggregate statistics (e.g., total GHG emissions avoided, renewable energy capacity financed)

**Benefits**:
- **Rewards genuine performers** with enhanced credibility and market differentiation
- **Creates competitive pressure** on less rigorous issuers
- **Generates data infrastructure** for investors, regulators, and researchers to evaluate market effectiveness
- **Positions Vietnam as a regional leader** in green finance transparency

---

## 5.3. Research Limitations and Suggestions for Future Research

### 5.3.1. Research Limitations

Four limitations are particularly consequential for interpreting the findings of this study.

**1. Treatment Sparsity**  
Only 20 of 3,964 entities (0.50%) issued green bonds during the observation window, representing 81 treated firm-year observations out of 23,284 (0.35%). This reflects the nascent stage of ASEAN green finance markets rather than a sampling choice, but the practical consequence is **limited statistical power**: effects of modest but economically meaningful magnitude may exist but remain undetectable given the available treated sample.

**Implications**:
- Point estimates should be interpreted with caution; wide confidence intervals prevent precise effect estimation
- Null findings do not definitively rule out small positive effects (e.g., a 1–2 percentage point ROA improvement over 10 years)
- As ASEAN green bond markets mature and more firms accumulate post-treatment observations, future studies will have greater power to detect effects

**2. Short Post-Issuance Horizon**  
The six-year panel (2020–2025) is insufficient to observe the long-run financial and environmental effects predicted by the Resource-Based View and Stakeholder Theory. Organizational capability accumulation, reputational dividend realization, and emissions trajectory changes from capital reallocation all operate over **multi-year or multi-decade horizons** (Barney, 1991; Freeman, 1984).

**Implications**:
- The null findings should be understood as **short-to-medium-run conclusions**, not permanent structural assessments
- Green bonds may generate value that manifests beyond the 6-year window (e.g., enhanced resilience to climate regulation, reduced stranded asset risk, improved stakeholder trust)
- A follow-up study in 2030 with 10+ years of post-issuance data may detect effects that are invisible in this study's time frame

**3. Absence of Bond-Level Yield and Proceeds Data**  
The study cannot directly analyze the **financing cost channel**—whether green bond issuers access capital at lower rates than conventional issuers (the "greenium" hypothesis). Nor can it track how proceeds are deployed to specific project categories (renewable energy, green buildings, clean transport).

**Data Gaps**:
- **Implied Cost of Debt** (interest expense / total debt) has only 0.7% coverage (169/23,284 observations; 6 treated observations)
- **Bond-level yield spreads** are unavailable in LSEG database for most ASEAN issuances
- **Use-of-proceeds allocation** is reported in prospectuses but not systematically digitized

**Implications**:
- The greenium hypothesis (H2c: reduced cost of debt) cannot be robustly tested
- Future research with access to Bloomberg fixed-income data or hand-collected prospectus data could fill this gap

**4. ESG Data Coverage Constraints**  
Refinitiv ASSET4 ESG scores are available for only 17.8% of observations, heavily skewed toward larger, internationally visible firms. The ESG outcome analysis therefore captures **large-firm behavior** and cannot be straightforwardly generalized to the broader ASEAN corporate population.

**Implications**:
- ESG results are subject to **sample selection bias**: treated firms with ESG data may differ systematically from treated firms without
- The direct emissions intensity analysis (81.1% coverage) partially compensates for this bias but is itself incomplete
- Mandatory ESG disclosure regulations (e.g., ISSB standards, EU CSRD) will improve data coverage in future cohorts

### 5.3.2. Suggestions for Future Research

Four research directions would most directly extend this study's contributions.

**Direction 1: Longer-Horizon Panel Analysis**  
Re-estimate the core models in 2030 using a 10–15 year panel (2020–2035). This would:
- Capture long-run effects on ROA, market valuation, and emissions that may not manifest in the short run
- Enable analysis of **bond maturity cycles**: Do effects differ for firms post-bond-maturity vs. during the bond's active life?
- Increase statistical power as more ASEAN firms issue green bonds in subsequent years

**Direction 2: Bond-Level Greenium Analysis**  
Acquire bond-level yield data from Bloomberg or Refinitiv Fixed Income to test:
- **Primary market greenium**: Do green bonds price at lower yields than comparable conventional bonds at issuance?
- **Secondary market premium**: Do green bonds trade at a yield discount (price premium) in secondary markets?
- **Persistence**: Does the greenium erode over time as the green bond market matures?

**Data Requirements**: Bond-level ISIN, issue date, maturity, coupon, yield-to-maturity, comparable conventional bond yields

**Direction 3: Project-Level Impact Attribution**  
Conduct a mixed-methods study combining:
- **Quantitative**: Firm-level panel analysis (as in this study)
- **Qualitative**: Case studies of 10–15 ASEAN green bond issuers with hand-collected data on:
  - Specific projects financed (e.g., 100 MW solar farm, LEED-certified office building)
  - Project-level environmental outcomes (e.g., MWh of renewable energy generated, tons of CO2 avoided)
  - Organizational changes post-issuance (e.g., creation of sustainability roles, board-level ESG integration)

**Research Question**: What organizational and project characteristics predict the gap between certified issuance and verified impact?

**Direction 4: Cross-Country Comparative Analysis**  
Extend the analysis to include developed markets (e.g., EU, Japan) as benchmarks:
- **Research Question**: Do green bond effects differ systematically between developed and emerging markets?
- **Hypothesized Moderators**: Regulatory stringency, investor sophistication, enforcement capacity, mandatory disclosure rules
- **Method**: Interaction terms between treatment and institutional quality indices (e.g., World Bank Governance Indicators, Climate Policy Uncertainty Index)

**Expected Insight**: Identify institutional preconditions under which green bonds generate measurable financial and environmental benefits, enabling evidence-based policy recommendations for ASEAN regulators.

---

## 5.4. Final Remarks

This study provides the first comprehensive causal evaluation of green bond impacts in the ASEAN region, employing state-of-the-art econometric methods to distinguish selection effects from treatment effects. The findings challenge the implicit assumption that green bond certification guarantees environmental or financial benefits. In the ASEAN context—characterized by nascent green finance markets, weak enforcement of environmental regulations, and limited mandatory disclosure—green bonds currently function as **credibility signals** that facilitate access to ESG capital pools but do not reliably translate into operational transformation.

The policy implication is urgent: **ASEAN green bond standards must evolve from process-based to outcome-based certification**. Without mandatory post-issuance impact reporting, public registries, and investor-driven accountability mechanisms, the rapid expansion of ASEAN green bond issuance risks widening—rather than closing—the gap between environmental rhetoric and environmental reality.

For corporate managers, the message is equally clear: green bonds are not a substitute for substantive environmental strategy. Firms that combine green bond issuance with **binding environmental targets**, **operational governance changes**, and **transparent impact reporting** will build the organizational capabilities that the Resource-Based View predicts will eventually translate into durable competitive advantage. Those that rely on certification alone will not.

The future effectiveness of green bonds in ASEAN—and emerging markets more broadly—depends not on the volume of issuance but on the **credibility of impact**. This study provides the empirical baseline against which future progress can be measured.

---

*[End of Chapter V]*
