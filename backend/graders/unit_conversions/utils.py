# graders/unit_conversions/utils.py

"""
Thin wrapper layer that exposes shared normalization utilities
to all Unit Conversions row checkers.
This allows us to keep grading modules self-contained
while using the shared normalizer functions from utilities/.
"""

from utilities.normalizers import (
    normalize_formula,
    normalize_unit_text,
    normalize_time_unit,
    normalize_temp_formula
)

def norm_formula(val):
    """Wrapper for shared normalize_formula."""
    return normalize_formula(val)

def norm_unit(val):
    """Wrapper for shared normalize_unit_text."""
    return normalize_unit_text(val)

def norm_time_unit(val):
    """Wrapper for shared normalize_time_unit."""
    return normalize_time_unit(val)

def norm_temp_formula(val):
    """Wrapper for shared normalize_temp_formula."""
    return normalize_temp_formula(val)
