# Copilot Instructions for `refinitiv-search`

## Build, test, and lint commands

Use the project environment first (team convention is `ref_env`).

```bash
conda activate ref_env
pip install -e ".[dev]"
```

There is no dedicated build script; this repository is packaged via `setup.py` and validated mainly through `pytest`.

Run tests:

```bash
# Full suite
pytest tests/

# Single file
pytest tests/test_analysis.py -v

# Single test
pytest tests/test_analysis.py::TestPropensityScore::test_estimate_propensity_scores -v
```

Lint/type tools are defined in dev extras:

```bash
black --check asean_green_bonds tests
flake8 asean_green_bonds tests
mypy asean_green_bonds
```

## High-level architecture

The repository has two connected layers:

1. **Data extraction/prep scripts at repo root**
   - `prepare_data.py` transforms `data2802.xlsx` into canonical CSVs in `data/` (`panel_data.csv`, `esg_panel_data.csv`, `series_data.csv`).
   - `greenbonds.py` retrieves LSEG fields in batches and writes `data/green_bonds_lseg_full.csv`.

2. **Reusable package in `asean_green_bonds/`**
   - `config.py` is the central contract for file paths, variable lists, treatment windows, and default covariates.
   - `data/loader.py` loads canonical CSV inputs defined in `config.py`.
   - `data/processing.py` performs merges (financial + ESG + market + green bonds), then creates treatment-state variables (`green_bond_issue`, cumulative `green_bond_active`, `certified_bond_active`) and feature engineering utilities.
   - `analysis/` contains econometric estimators: propensity score modeling, DiD (`PanelOLS`-based FE specs), diagnostics, and event studies.
   - `utils/` contains validation, statistical utilities, and plotting wrappers used by notebooks/tests.

Testing in `tests/` is organized by module (`test_data.py`, `test_analysis.py`, `test_utils.py`, `test_authenticity.py`) and uses synthetic fixtures in `tests/conftest.py` to mirror expected column schemas.

## Key conventions in this codebase

- **Panel identity convention:** core panel ops assume firm/year keys `ric` + `Year`, and most regressions expect index order `(ric, Year)`.
- **Identifier normalization:** `org_permid` is frequently coerced to numeric then standardized to string before joins; preserve this when adding merges.
- **Treatment naming contract:** analysis defaults rely on `green_bond_active` as treatment; issuance-year indicator is `green_bond_issue`.
- **Theory-first modeling:** `data/feature_selection.py` explicitly treats auto-selection as **diagnostic only**, not a substitute for theory-driven causal specification.
- **Non-throwing estimator pattern:** some analysis functions (notably DiD) return result dictionaries with an `'error'` key instead of raising; callers/tests may depend on this shape.
- **Data path contract:** loaders read from `config.RAW_DATA_FILES`/`PROCESSED_DATA_FILES`; avoid hardcoding alternative paths in new package code.
