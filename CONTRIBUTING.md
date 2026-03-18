# Contributing Guide

## Welcome! 👋

Thank you for your interest in contributing to the ASEAN Green Bonds research project. This guide will help you get started.

## Code of Conduct

Be respectful, inclusive, and professional. All contributors are expected to uphold our community standards.

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/yourusername/asean-green-bonds.git
cd asean-green-bonds
```

### 2. Set Up Development Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### 3. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

## Development Workflow

### Writing Code

1. **Follow Style Guidelines**
   ```bash
   # Format code with black
   black asean_green_bonds/ tests/
   
   # Check with flake8
   flake8 asean_green_bonds/ tests/
   ```

2. **Add Type Hints**
   ```python
   from typing import Optional, List
   
   def my_function(param: str, count: int = 10) -> List[str]:
       """Brief description.
       
       Parameters
       ----------
       param : str
           Description.
       count : int, default 10
           Description.
           
       Returns
       -------
       List[str]
           Description.
       """
       pass
   ```

3. **Write Docstrings**
   - Use NumPy-style docstrings
   - Include Parameters, Returns, Raises sections
   - Include example usage for complex functions

### Writing Tests

Every new feature should include tests:

```python
# tests/test_my_feature.py
import pytest
from asean_green_bonds import my_module

class TestMyFeature:
    def test_basic_functionality(self, sample_dataframe):
        """Test basic operation."""
        result = my_module.my_function(sample_dataframe)
        assert result is not None
        
    def test_error_handling(self):
        """Test error conditions."""
        with pytest.raises(ValueError):
            my_module.my_function(None)
```

Run tests:
```bash
pytest tests/ -v
pytest tests/test_my_feature.py -v
pytest tests/ --cov=asean_green_bonds
```

### Documenting Changes

Update relevant documentation:

- **docs/ARCHITECTURE.md** - If adding new modules or functions
- **docs/USAGE.md** - If adding new public functionality
- **CHANGELOG.md** - Document your changes (create if needed)

## Pull Request Process

### 1. Before Submitting

- [ ] Tests pass: `pytest tests/`
- [ ] Code formatted: `black asean_green_bonds/`
- [ ] Linting clean: `flake8 asean_green_bonds/`
- [ ] Documentation updated
- [ ] Docstrings complete
- [ ] Type hints added

### 2. Create Pull Request

1. Push to your fork
2. Create PR with clear title and description
3. Link related issues
4. Include:
   - What changes were made
   - Why these changes were needed
   - How to test the changes

### 3. PR Template

```markdown
## Description
Brief description of changes.

## Related Issue
Closes #123

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring

## How Has This Been Tested?
Describe testing approach.

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Code formatted
```

## Directory Structure

When adding new modules, follow this structure:

```
asean_green_bonds/
├── __init__.py              # Export public functions
├── new_module.py            # New module
│   ├── public_function()    # Export in __init__.py
│   └── _private_function()  # Internal only
└── tests/
    └── test_new_module.py   # Comprehensive tests
```

## Commit Messages

Write clear, descriptive commit messages:

```
Add feature: Brief description (50 chars max)

More detailed explanation of changes (72 chars per line)
- Bullet point for each major change
- Why was this change needed?
- Any important context

Closes #123
Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

## Code Review

- Reviews are constructive and focused on code quality
- Respond to comments within 48 hours
- Ask for clarification on feedback
- Iterate until approval

## Reporting Issues

### Bug Report Template

```markdown
## Description
Clear description of the bug.

## Steps to Reproduce
1. Step 1
2. Step 2
3. Result

## Expected Behavior
What should happen.

## Actual Behavior
What actually happens.

## Environment
- Python version: 3.x
- OS: macOS/Linux/Windows
- Package version: 0.x.x
```

### Feature Request Template

```markdown
## Description
Clear description of the feature.

## Motivation
Why is this needed?

## Proposed Solution
How should it work?

## Alternative Approaches
Any alternatives considered?
```

## Areas for Contribution

### High Priority
- [ ] Additional econometric methods (IV/2SLS)
- [ ] Cross-validation improvements
- [ ] Alternative matching algorithms
- [ ] Visualization enhancements
- [ ] Performance optimizations

### Documentation
- [ ] Tutorials and examples
- [ ] FAQ updates
- [ ] Video walkthroughs
- [ ] Translation to other languages

### Testing
- [ ] Edge case coverage
- [ ] Performance testing
- [ ] Integration tests
- [ ] Platform-specific tests

### Research Extensions
- [ ] Alternative outcomes
- [ ] Subgroup analyses
- [ ] Country-specific studies
- [ ] Sector-level analysis

## Questions or Need Help?

- **Documentation**: Check docs/ folder
- **Issues**: Search GitHub issues first
- **Discussions**: Start a GitHub discussion
- **Email**: Reach out to maintainers

## Acknowledgments

Contributors will be recognized in:
- CONTRIBUTORS.md
- GitHub contributor graph
- Research paper acknowledgments (if applicable)

## License

By contributing, you agree your code will be licensed under the MIT License.

---

**Thank you for making this project better!** 🚀
