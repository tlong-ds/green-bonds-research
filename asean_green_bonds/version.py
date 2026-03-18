"""
Version information for ASEAN Green Bonds package.
"""

__version__ = "0.1.0"
__version_date__ = "2025-03-18"

def get_version():
    """Return version string."""
    return __version__

def get_version_info():
    """Return detailed version information."""
    return {
        "version": __version__,
        "date": __version_date__,
        "stage": "alpha",
    }
