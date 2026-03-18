# Troubleshooting Guide - Notebook Execution Issues

**Last Updated**: 2026-03-18

---

## Common Issues and Solutions

### Issue 1: "exog does not have full column rank" in Cell 11

**Symptom**:
```
Error estimating return_on_assets: exog does not have full column rank. 
If you wish to proceed with model estimation irrespective of th...
```

**Root Causes**:
1. **Perfect Multicollinearity**: Using two variables that sum to zero (like `did_certified` + `did_non_certified`)
2. **All-zero Regressor**: A variable with no variation across observations
3. **Missing Data**: Variables not properly loaded before regression

**Solutions**:

#### Solution A: Reload the Notebook (Recommended)
```bash
# Close Jupyter and reopen the notebook
jupyter notebook notebooks/methodology-and-result.ipynb

# Then restart the kernel (Kernel > Restart) before running cells
```

**Why**: Jupyter caches code in memory. Reloading ensures you have the latest fixed code.

#### Solution B: Restart Kernel Without Reloading
```
Kernel > Restart Kernel and Clear Outputs
```

Then run cells from the top in order.

#### Solution C: Manual Check
If using an older version of the notebook, manually verify Cell 11 has:

**CORRECT** ✅:
```python
models_to_run = [
    {
        'name': 'Main Effect (All Green Bonds)',
        'treatment': 'did',  # Single variable only
        'desc': 'H1: ...'
    }
]
```

**WRONG** ❌:
```python
models_to_run = [
    {
        'name': 'Certified vs Non-Certified Bonds',
        'treatment': ['did_certified', 'did_non_certified'],  # Both = collinear!
        'desc': 'H3: ...'
    }
]
```

#### Solution D: Use Error Recovery (Automatic)
Cell 11 now includes automatic error recovery:
- Detects if treatment variables form a list
- Automatically uses first variable only
- Provides informative error message if column rank error occurs

---

### Issue 2: KeyError: 'did' not in index

**Symptom**:
```
KeyError: "['did'] not in index"
```

**Root Cause**: Cell 9 (VIF) runs before Cell 3 (where DiD is created)

**Solution**: Run cells in order
```
1. Cell 1: Load data
2. Cell 3: Create DiD variables  ← MUST RUN FIRST
3. Cell 9: VIF calculation
4. Cell 11: DiD regression
```

Or use: **Kernel > Run All Cells** (runs all cells in sequence automatically)

---

### Issue 3: ModuleNotFoundError: No module named 'fix_critical_issues'

**Symptom**:
```
ModuleNotFoundError: No module named 'fix_critical_issues'
```

**Root Cause**: Notebooks execute from `notebooks/` directory, parent directory modules not found

**Solution**: Cell 1 already includes:
```python
import sys
sys.path.insert(0, '..')
```

Just make sure Cell 1 runs before other diagnostic cells (7, 12, 17).

---

### Issue 4: TypeError: unsupported format string passed to tuple.__format__

**Symptom**:
```
TypeError: unsupported format string passed to tuple.__format__
```

**Root Cause**: Moulton factor function returned tuple instead of scalar

**Solution**: Already fixed! Function now returns scalar.

If issue persists:
- Restart kernel
- Reload notebook from disk

---

## Prevention Guide

### Before Running Cells

1. **Check Jupyter is Fresh**
   - Close all notebooks
   - Close Jupyter server
   - Reopen notebook

2. **Restart Kernel**
   - Kernel > Restart Kernel
   - Kernel > Clear All Outputs

3. **Load Latest Version**
   - Pull latest code: `git pull`
   - Reload notebook: `F5` or `Ctrl+R`

### While Running Cells

1. **Run All or Run Sequentially**
   - Better: **Kernel > Run All** (runs 1→20)
   - Alternative: Select Cell 1, then Shift+Click Cell N, then **Cell > Run Selected**

2. **Never Skip Cell 1**
   - Cell 1 imports modules
   - Cell 1 sets up sys.path
   - All other cells depend on it

3. **Never Run Cell 11 Before Cell 3**
   - Cell 3 creates `did` variable
   - Cell 11 needs `did` variable
   - Dependency: Cell 3 → Cell 9 → Cell 11

---

## Testing Checklist

After applying any fixes, verify:

- [ ] Cell 1 runs without errors (imports + data load)
- [ ] Cell 3 runs without errors (DiD creation)
- [ ] Cell 9 runs without errors (VIF passes, no KeyError)
- [ ] Cell 11 runs without errors (3 outcomes estimated)
- [ ] Cell 12 runs without errors (Moulton factor calculated)
- [ ] Cell 17 runs without errors (hypothesis tests completed)

---

## Getting Help

| Issue | Documentation | Next Step |
|-------|---------------|-----------|
| Multicollinearity | MULTICOLLINEARITY_FIX.md | Check treatment specification |
| Data Loading | DATA_LOADING_FIX_SUMMARY.md | Verify is_issuer creation |
| Working Directory | PATH_FIXES_SUMMARY.md | Check sys.path in Cell 1 |
| Execution Order | NOTEBOOK_EXECUTION_GUIDE.md | Run cells sequentially |
| Moulton Factor | MOULTON_FACTOR_FIX.md | Restart kernel |

---

## Quick Recovery Steps

If notebook errors occur:

1. **Stop**: Don't run more cells
2. **Save**: Save notebook state (Ctrl+S)
3. **Kernel > Restart Kernel and Clear Outputs**
4. **Run > Run All Cells**
5. **Check**: Verify all cells pass

---

## Advanced: Manual Notebook Refresh

If all else fails:

```bash
# Backup current notebook
cp notebooks/methodology-and-result.ipynb notebooks/methodology-and-result.ipynb.backup

# Get latest version from git
git checkout notebooks/methodology-and-result.ipynb

# Reopen notebook in Jupyter
jupyter notebook notebooks/methodology-and-result.ipynb
```

---

**Status**: Guide up-to-date as of 2026-03-18
