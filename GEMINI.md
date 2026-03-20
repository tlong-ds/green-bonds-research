# ASEAN Green Bonds: Project Context & Guidelines

This document provides essential context and instructions for AI agents working on the `asean-green-bonds` project.

## Project Overview

**ASEAN Green Bonds** is a production-grade Python package designed for the econometric analysis of green bond issuance and its environmental impact in ASEAN markets (2015-2025). The project transforms research-oriented Jupyter notebooks into a robust, modular, and testable codebase.

### Key Technologies
- **Language:** Python 3.8+
- **Data Processing:** `pandas`, `numpy`
- **Econometrics:** `statsmodels`, `linearmodels` (Panel OLS, FE)
- **Machine Learning:** `scikit-learn` (Propensity Score Matching)
- **Visualization:** `matplotlib`, `seaborn`
- **Testing:** `pytest`, `pytest-cov`

### Architecture
The project follows a modular "Lego blocks" architecture:
- `asean_green_bonds/data/`: Data loading (`loader.py`), transformation (`processing.py`), and feature engineering (`feature_selection.py`, `feature_engineering.py`).
- `asean_green_bonds/analysis/`: Core econometric methods including Propensity Score Matching (`propensity_score.py`), Difference-in-Differences (`difference_in_diff.py`), Event Studies (`event_study.py`), and Robustness Diagnostics (`diagnostics.py`).
- `asean_green_bonds/utils/`: Statistical helpers (`stats.py`), visualization tools (`visualization.py`), and data validation (`validation.py`).
- `asean_green_bonds/config.py`: Centralized configuration for paths, variable names, and model parameters.

## Building and Running

### Installation
```bash
# Install in editable mode with development dependencies
pip install -e ".[dev]"
```

### Running Analysis
The project includes refactored Jupyter notebooks in the `notebooks/` directory that demonstrate the end-to-end workflow:
1. `01_data_preparation.ipynb`
2. `02_feature_selection.ipynb`
3. `03_methodology_and_results.ipynb`

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=asean_green_bonds --cov-report=term-missing

# Run specific test module
pytest tests/test_analysis.py
```

### Linting and Formatting
```bash
# Format code with Black
black asean_green_bonds tests

# Check style with Flake8
flake8 asean_green_bonds tests

# Type checking with Mypy
mypy asean_green_bonds
```

## Development Conventions

### Coding Standards
- **Type Hints:** All functions MUST have complete type hints for parameters and return values.
- **Docstrings:** All public functions MUST include descriptive docstrings (Google or NumPy style).
- **Configuration:** Avoid hardcoding paths or column names. Use `asean_green_bonds/config.py`.
- **Naming:** Follow standard econometric naming conventions (e.g., `L1_` prefix for 1-year lagged variables).

### Testing Practices
- **Fixtures:** Use the fixtures defined in `tests/conftest.py` for consistent test data.
- **Mocking:** Mock external data dependencies in unit tests to ensure they remain isolated and fast.
- **Coverage:** Maintain high test coverage, especially for core econometric logic in the `analysis/` module.

### Workflow Integration
When adding new functionality:
1. Implement the core logic in the appropriate submodule (`data/`, `analysis/`, or `utils/`).
2. Update `asean_green_bonds/__init__.py` if the function should be part of the public API.
3. Add corresponding unit tests in the `tests/` directory.
4. Verify the change by running the full test suite and linting tools.

## Key Files
- `asean_green_bonds/config.py`: The single source of truth for project-wide constants.
- `ARCHITECTURE_ASSESSMENT.md`: Detailed analysis of the package structure and recommendations.
- `PROJECT_SUMMARY.md`: High-level overview of project achievements and research findings.
- `requirements.txt`: Pinned dependencies for the analysis environment.
- `setup.py`: Package metadata and installation configuration.
