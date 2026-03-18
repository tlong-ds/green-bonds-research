# Installation & Setup Guide

## Quick Start

### 1. Prerequisites

- Python 3.8+
- pip or conda
- Git (for cloning repository)

### 2. Installation Methods

#### Option A: Install from Repository (Development)

```bash
# Clone the repository
git clone https://github.com/yourusername/asean-green-bonds.git
cd asean-green-bonds

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
```

#### Option B: Install from PyPI (When Published)

```bash
pip install asean-green-bonds
```

### 3. Verify Installation

```bash
python3 -c "import asean_green_bonds; print('✅ Installation successful!')"
```

## Data Setup

### 1. Data File Location

Place raw data files in the `data/` directory:

```
data/
├── panel_data.csv                      # Financial metrics panel
├── esg_panel_data.csv                  # ESG scores
├── green-bonds.csv                     # Green bond issuances
├── series_data.csv                     # Industry classification (GIC)
└── market_data/
    ├── vn-market.csv                   # Vietnam firms
    ├── tl-market.csv                   # Thailand firms
    ├── ml-market.csv                   # Malaysia firms
    ├── sing-market.csv                 # Singapore firms
    ├── pp-market.csv                   # Philippines firms
    ├── indo-market.csv                 # Indonesia firms
    └── other-market.csv                # Other markets
```

### 2. Configure Data Paths

Edit `asean_green_bonds/config.py` to set your data directories:

```python
from pathlib import Path

# Set paths
DATA_DIR = Path('/path/to/your/data')
PROCESSED_DATA_DIR = Path('/path/to/processed')
```

### 3. Process Raw Data

```bash
# Run the data preparation notebook
jupyter notebook notebooks/01_data_preparation.ipynb
```

This creates processed datasets in `processed_data/`:
- `cleaned_panel_data.csv`
- `final_engineered_panel_data.csv`
- `selected_features_panel_data.csv`

## Running Notebooks

### 1. Start Jupyter

```bash
jupyter notebook
```

### 2. Run in Order

1. **01_data_preparation.ipynb** - Load and process raw data
2. **02_feature_selection.ipynb** - Select key variables
3. **03_methodology_and_results.ipynb** - Main analysis and results

Each notebook uses the `asean_green_bonds` package functions.

## Running Tests

### 1. Install Test Dependencies

```bash
pip install pytest pytest-cov
```

### 2. Run All Tests

```bash
# All tests
pytest tests/

# With verbose output
pytest tests/ -v

# With coverage report
pytest tests/ --cov=asean_green_bonds --cov-report=html
```

### 3. Run Specific Tests

```bash
# Single module
pytest tests/test_data.py

# Single class
pytest tests/test_data.py::TestDataProcessing

# Single test
pytest tests/test_data.py::TestDataProcessing::test_filter_asean_firms
```

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'asean_green_bonds'`

**Solution:** Install in development mode:
```bash
pip install -e .
```

### Issue: Data files not found

**Solution:** Verify file paths in `config.py` match your data location:
```python
print(config.DATA_DIR)  # Check configured path
import os
os.listdir(config.DATA_DIR)  # List files
```

### Issue: yfinance FX conversion fails

**Solution:** The package gracefully skips FX conversion if yfinance is unavailable. Currency conversion is optional.

```bash
# Install yfinance
pip install yfinance
```

### Issue: Tests skipped with "Data files not found"

**Solution:** This is expected if raw data is not available. Some tests require actual data files. Unit tests on synthetic data should pass.

## Development Setup

### 1. Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

Includes:
- pytest (testing)
- pytest-cov (coverage)
- black (code formatting)
- flake8 (linting)
- sphinx (documentation)

### 2. Code Style

```bash
# Format code
black asean_green_bonds/ tests/

# Check linting
flake8 asean_green_bonds/ tests/
```

### 3. Build Documentation

```bash
cd docs/
make html
open _build/html/index.html
```

## Environment Variables

Optional environment variables for advanced configuration:

```bash
# Logging level
export ASEAN_LOG_LEVEL=DEBUG

# Data directory override
export ASEAN_DATA_DIR=/path/to/data

# Processed data directory
export ASEAN_PROCESSED_DIR=/path/to/processed
```

## System Requirements

### Minimum
- Python 3.8
- 2 GB RAM
- 500 MB disk space

### Recommended
- Python 3.10+
- 8+ GB RAM (for large panel operations)
- 2 GB disk space (for processed data)

## Docker Setup (Optional)

### 1. Build Image

```bash
docker build -t asean-green-bonds .
```

### 2. Run Container

```bash
docker run -it -v $(pwd)/data:/app/data asean-green-bonds jupyter notebook --ip=0.0.0.0
```

## Next Steps

1. ✅ Install package
2. ✅ Set up data files
3. ✅ Run 01_data_preparation.ipynb
4. ✅ Run 02_feature_selection.ipynb
5. ✅ Run 03_methodology_and_results.ipynb
6. 📊 View results in `images/` directory

## Support

For issues or questions:
1. Check existing GitHub issues
2. Review error messages carefully
3. Consult `docs/TROUBLESHOOTING.md`
4. Open new GitHub issue with:
   - Python version (`python --version`)
   - Error message
   - Steps to reproduce

---

**Document Version:** 1.0  
**Last Updated:** 2026-03-18
