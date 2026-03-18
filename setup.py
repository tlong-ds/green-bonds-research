#!/usr/bin/env python
"""Setup script for asean-green-bonds package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read version from version.py
version_file = this_directory / "asean_green_bonds" / "version.py"
version_dict = {}
exec(version_file.read_text(), version_dict)
version = version_dict["__version__"]

# Read requirements from requirements.txt
requirements_file = this_directory / "requirements.txt"
requirements = [
    line.strip()
    for line in requirements_file.read_text().split("\n")
    if line.strip() and not line.startswith("#")
]

setup(
    name="asean-green-bonds",
    version=version,
    author="Research Team",
    author_email="your-email@example.com",
    description="Econometric analysis of green bond issuance in ASEAN markets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/asean-green-bonds",
    packages=find_packages(exclude=["tests", "notebooks", "docs", "images"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=3.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
        "visualization": [
            "matplotlib>=3.5",
            "seaborn>=0.11",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "green bonds",
        "ASEAN",
        "econometrics",
        "difference-in-differences",
        "propensity score matching",
        "ESG",
        "environmental sustainability",
    ],
    project_urls={
        "Documentation": "https://github.com/tlong-ds/asean-green-bonds/tree/main/docs",
        "Source": "https://github.com/tlong-ds/asean-green-bonds",
        "Tracker": "https://github.com/tlong-ds/asean-green-bonds/issues",
    },
)
