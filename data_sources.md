# Data Sources

`data/cbi_certified_bonds.csv`
Rows: 841. Columns: 12.
Columns: `Issuer / Applicant`, `Issue date`, `Size (in issuance currency)`, `Size (USD equivalent)`, `Term`, `Issuer Country`, `Sector Criteria`, `Approved Verifier`, `Verifier Report`, `Status`, `Certification type`, `Description`.
Notes: All green bonds certified by the Climate Bonds Initiative (CBI).

`data/gdp_inflation.csv`
Rows: 17. Columns: 14.
Columns: `Country Name`, `Country Code`, `Series Name`, `Series Code`, `2015 [YR2015]`, `2016 [YR2016]`, `2017 [YR2017]`, `2018 [YR2018]`, `2019 [YR2019]`, `2020 [YR2020]`, `2021 [YR2021]`, `2022 [YR2022]`, `2023 [YR2023]`, `2024 [YR2024]`, `2025 [YR2025]`
Notes: GDP and inflation series by country and year.

`data/esg_data.csv`
Rows: 168,146. Columns: 17.
Columns: `company`, `ticker`, `country`, `Year`, `emissions_intensity`, `environmental_investment`, `esg_score`, `estimated_total_carbon_footprint`, `internal_carbon_pricing`, `total_energy_consumed`, `renewable_energy_use`, `scope_1_2_emissions`, `co2_equivalent_emissions`, `environmental_innovation`, `internal_carbon_price_per_tonne`, `environmental_pillar_data`, `environmental_resource_metric`.
Notes: Core ESG data.

`data/financial_data.csv`
Rows: 25,806. Columns: 22.
Columns: `company`, `ticker`, `country`, `Year`, `capital_expenditures`, `cash`, `current_assets_total`, `current_liabilities_total`, `earnings_bef_interest_tax`, `employees`, `interest_expense_total`, `long_term_debt`, `market_capitalization`, `net_cash_flow_operating_actv`, `net_sales_or_revenues`, `operating_income`, `return_on_assets`, `return_on_equity_total`, `total_assets`, `total_capital`, `total_debt`, `total_liabilities`.
Notes: Core financial data.

`data/market_data.csv`
Rows: 24,830. Columns: 8.
Columns: `company`, `ticker`, `country`, `Year`, `ask_price`, `bid_price`, `market_value`, `tri`.
Notes: Core market data.

`data/static_data.csv`
Rows: 5,006. Columns: 4.
Columns: `ticker`, `country`, `industry_group_code`, `founding_year`.
Notes: Core static firm data.

`data/green_bonds_authenticated.csv`
Rows: 333. Columns: 64.
Columns: `Deal PermID`, `Package Identifier`, `Master Deal Type Code`, `All New Issues Manager Roles Code`, `Manager's Role Code`, `Dates: Issue Date`, `Issuer/Borrower Name Full`, `Issuer/Borrower PermID`, `Issue Type`, `Transaction Status`, `Issuer/Borrower Nation`, `New Issues Current Filing Date`, `Offer Price (Uniform)`, `Proceeds Amount Incl Overallotment Sold All Markets`, `Proceeds Amount This Market`, `Issuer/Borrower Stock Exchange Name`, `Security Type All Markets`, `Offering Technique`, `New Issues Fees: Gross Spread as Pct of Principal Amount This Market`, `Domicile Nation Sub Region`, `Domicile Nation Region`, `Issuer/Borrower TRBC Business Sector`, `Issuer/Borrower TRBC Economic Sector`, `Lead Left Bookrunner`, `Managers Tier 1 & Tier 2 `, `ECM Flag`, `Primary Use Of Proceeds`, `Issuer/Borrower Nation Region`, `Master Deal Type`, `All New Issues Manager Roles`, `Manager's Role`, `is_authentic`, `esg_improvement`, `esg_pvalue`, `n_pre_obs`, `n_post_obs`, `data_quality`, `is_cbi_certified`, `is_icma_certified`, `icma_confidence`, `issuer_nation`, `issuer_sector`, `issuer_type`, `issuer_track_record`, `has_green_framework`, `esg_component`, `cert_component`, `issuer_component`, `authenticity_score`, `authenticity_category`, `esg_score_pre_issuance`, `esg_score_issuance_year`, `esg_score_post_issuance`, `environmental_investment`, `has_esg_data`, `esg_data_source`, `esg_matching_company`, `esg_coverage_years`, `is_certified`, `issuer_nation_issuer`, `issuer_sector_issuer`, `issuer_type_issuer`, `issuer_track_record_issuer`, `has_green_framework_issuer`.
Notes: Incomplete green bonds data. All normalized columns are faulty; use other attributes only.
