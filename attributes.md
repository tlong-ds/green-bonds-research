# LSEG Datastream — Attribute Reference Guide

> **Usage:** Time Series attributes are pulled using a Time Series request in the Datastream Excel Add-in. Series (static) attributes must be pulled using a Static Request and merged as fixed columns into the panel.

---

## Legend

| Badge | Source | Description |
|---|---|---|
| `Worldscope` | WC codes | Financial statement fundamentals (annual) |
| `Datastream` | Short codes | Market and price data (daily/annual) |
| `ESG/ASSET4` | EN/TR codes | Environmental and social data |
| `CG/ASSET4` | CG codes | Corporate governance data |
| `Series only` | WC codes | Static identifiers — use Static Request, not Time Series |

---

## 1. Time Series — Financial Fundamentals (Worldscope)

| Code | Name | Description |
|---|---|---|
| `WC02999` | Total Assets | Sum of all current and non-current assets |
| `WC02201` | Current Assets – Total | Cash, receivables, inventories and other assets due within 1 year |
| `WC04601` | Capital Expenditure (CAPEX) | Funds used to acquire or upgrade physical assets |
| `WC08326` | Return on Assets (ROA) % | Net income / total assets × 100 |
| `WC08301` | Return on Equity (ROE) % | Net income / common equity × 100 |
| `WC07011` | Number of Employees | Total full-time equivalent employees |
| `WC04860` | Free Cash Flow | Funds from operations (operating cash flow proxy) |
| `WC03255` | Total Debt | All interest-bearing and capitalised lease obligations (short + long term) |
| `WC03351` | Total Liabilities | All short and long term obligations |
| `WC03101` | Current Liabilities – Total | Obligations due within 1 year |
| `WC01250` | Operating Income (EBIT proxy) | Sales minus total operating expenses |
| `WC01001` | Net Sales / Revenues | Gross sales less discounts, returns, and allowances |
| `WC03251` | Long-Term Debt | Non-current interest-bearing obligations |
| `WC08001` | Market Capitalisation (annual) | Year-end price × shares outstanding. **Unit: thousands.** Use with caution alongside `MV` |
| `WC03998` | Capital Employed | Total capital employed in the business |
| `WC18191` | EBIT | Earnings before interest and taxes |
| `WC01075` | Interest Expense on Debt | Total interest expense charged to income statement |
| `WC02003` | Cash | Cash only (excludes short-term investments; use `WC02001` for cash + ST investments) |

> **Unit note:** `WC08001` is in **thousands**. Divide by 1,000 to convert to millions before merging with `MV`.

---

## 2. Time Series — Market & Price Data (Datastream)

| Code | Name | Description |
|---|---|---|
| `RI` | Return Index (Total Return) | Theoretical growth in share value assuming dividends reinvested. Compute annual stock return as `(RI_t − RI_t-1) / RI_t-1` |
| `PA` | Price (adjusted) | Official closing price, adjusted for capital changes. Default datatype for equities |
| `PB` | Price to Book Value | Market value of equity / book value of equity (MTBV) |
| `MV` | Market Value | Share price × shares in issue. **Unit: millions.** Updated on capital changes. Use for daily/live data; use `WC08001` for annual snapshot |

---

## 3. Time Series — ESG / Environmental (ASSET4 / Refinitiv ESG)

| Code | Name | Description |
|---|---|---|
| `TRESGS` | ESG Score (overall) | Overall company ESG score based on self-reported E, S and G pillar data. Scale: 0–100 |
| `ENERDP013` | Total Energy Consumed | Total direct and indirect energy consumption reported by the company (GJ or MWh) |
| `ENERDP014` | Renewable Energy Use | Share or total of energy from renewable sources |
| `ENERDP768` | Carbon / GHG Intensity | GHG emissions per unit of output (carbon intensity metric) |
| `ENERO132V` | Scope 1 + 2 GHG Emissions | Total direct (Scope 1) and indirect energy (Scope 2) greenhouse gas emissions (tonnes CO₂e) ⚠ May return NA for companies with limited ESG reporting |
| `ENERO24V` | CO₂ Equivalent Emissions | Total CO₂-equivalent emissions (may overlap with `ENERO132V` depending on scope definition) |
| `ENPIDP023` | Environmental Innovation | Data point measuring environmental innovation initiatives or patents (Porter Hypothesis proxy) |

> **Coverage warning:** Some `ENERO*` and `ENERDP*` codes return NA even for major companies. Test each code on 5–10 companies before running the full panel pull. Fallback for emissions: `ENERDP023` (Total CO₂ Emissions direct) has wider coverage.

---

## 4. Time Series — Corporate Governance (CG / ASSET4)

| Code | Name | Description |
|---|---|---|
| `CGBSDP060` | Board Size | Total number of directors on the board |
| `CGBSDP0012` | Board Independence % | Percentage of independent/non-executive directors (Policy Board Independence) |
| `CGBSO09V` | CEO–Chairman Separation | Binary flag. ⚠ **Recode after download:** `CEO_Duality = 1 − CGBSO09V` so that 1 = CEO also chairs the board (standard Agency Theory coding) |

---

## 5. Series (Static Request Only — Company Identifiers)

> Pull these with a **Static Request** in the Excel Add-in, then merge as fixed columns into your panel on the company identifier.

| Code | Name | Description |
|---|---|---|
| `WC06010` | Country of Incorporation | 2-letter ISO country code. Use for ASEAN country filter in panel |
| `WC18272` | Industry / Sector Classification | Worldscope industry group code. Use for industry fixed effects in regression |

---

## Quick Pull Checklist

### Refinitiv / LSEG Datastream (Excel Add-in)

**Time Series request** — set frequency to **Yearly**, date range **2015–2024:**

```
WC02999, WC02201, WC04601, WC08326, WC08301, WC07011, WC04860,
WC03255, WC03351, WC03101, WC01250, WC01001, WC03251, 
WC08001, WC03998, WC18191, WC01075, WC02003,

TRESGS, ENERDP013, ENERDP014, ENERDP768, ENERO132V, ENERO24V, ENPIDP023,

RI, PA, PB, MV
```

**Static request** — pull once and merge by company:

```
WC06010, WC18272

CGBSDP060, CGBSDP0012, CGBSO09V
```

### World Bank (for macroeconomic controls)

| Indicator Code | Name |
|---|---|
| `NY.GDP.MKTP.KD.ZG` | GDP Growth Rate (% annual) |
| `FP.CPI.TOTL.ZG` | Inflation Rate / CPI (% annual) |

Download from: [https://databank.worldbank.org](https://databank.worldbank.org) → World Development Indicators → select 6 ASEAN countries → years 2015–2024 → Export CSV. Merge into panel on `(Country, Year)`.

---

*Reference compiled for ASEAN green bond panel study, 2015–2024. Sources: LSEG Datastream Worldscope, LSEG ASSET4 ESG, World Bank WDI.*