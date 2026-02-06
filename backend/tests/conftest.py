"""
conftest.py — Shared pytest fixtures for MA Grader tests

This module provides mock worksheet fixtures and helper functions for
creating test data. All grading tests can import these fixtures to
simulate Excel workbook interactions without requiring actual files.
"""

import pytest
from unittest.mock import MagicMock, PropertyMock
from datetime import datetime, date, timedelta


class MockCell:
    """Mock Excel cell with value and number_format properties."""
    
    def __init__(self, value=None):
        self._value = value
        self._number_format = "General"
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, val):
        self._value = val
    
    @property
    def number_format(self):
        return self._number_format
    
    @number_format.setter
    def number_format(self, fmt):
        self._number_format = fmt


class MockWorksheet:
    """
    Mock openpyxl Worksheet that stores cell values in a dictionary.
    
    Usage:
        ws = MockWorksheet()
        ws["A1"] = "Hello"
        ws["B1"].value = 42
        print(ws["A1"].value)  # "Hello"
    """
    
    def __init__(self):
        self._cells = {}
    
    def __getitem__(self, cell_ref: str) -> MockCell:
        if cell_ref not in self._cells:
            self._cells[cell_ref] = MockCell()
        return self._cells[cell_ref]
    
    def __setitem__(self, cell_ref: str, value):
        if cell_ref not in self._cells:
            self._cells[cell_ref] = MockCell()
        self._cells[cell_ref].value = value
    
    def set_cells(self, cell_dict: dict):
        """Convenience method to set multiple cells at once."""
        for cell_ref, value in cell_dict.items():
            self[cell_ref] = value


@pytest.fixture
def mock_worksheet():
    """Provide a fresh MockWorksheet instance."""
    return MockWorksheet()


@pytest.fixture
def currency_conversion_worksheet():
    """
    Provide a MockWorksheet pre-populated with valid Currency Conversion data.
    
    This represents a "perfect" submission for testing full-score scenarios.
    """
    ws = MockWorksheet()
    
    # Row 15: Name letters (for student "John Doe")
    ws["C15"] = "J"
    ws["D15"] = "O"
    ws["E15"] = "D"
    ws["F15"] = "O"
    
    # Row 16: Countries (Jamaica, Oman, Denmark, Oman)
    ws["C16"] = "Jamaica"
    ws["D16"] = "Oman"
    ws["E16"] = "Denmark"
    ws["F16"] = "Oman"
    
    # Row 17: Recent dates
    today = datetime.today()
    ws["C17"] = today
    ws["D17"] = today - timedelta(days=5)
    ws["E17"] = today - timedelta(days=10)
    ws["F17"] = today - timedelta(days=15)
    
    # Row 18: Currency codes
    ws["C18"] = "JMD"
    ws["D18"] = "OMR"
    ws["E18"] = "DKK"
    ws["F18"] = "OMR"
    
    # Row 19: Exchange rates (formulas)
    ws["C19"] = "=B4*1.5"
    ws["D19"] = "=B4*0.38"
    ws["E19"] = "=B4*6.8"
    ws["F19"] = "=B4*0.38"
    
    # Row 20: Budget conversion formulas
    ws["C20"] = "=B4*C19"
    ws["D20"] = "=B4*D19"
    ws["E20"] = "=B4*E19"
    ws["F20"] = "=B4*F19"
    
    # Row 21: USD conversion back formulas
    ws["C21"] = "=D4/C19"
    ws["D21"] = "=D4/D19"
    ws["E21"] = "=D4/E19"
    ws["F21"] = "=D4/F19"
    
    return ws


@pytest.fixture
def income_analysis_worksheet():
    """
    Provide a MockWorksheet pre-populated with valid Income Analysis data.
    
    This represents a "perfect" submission for testing full-score scenarios.
    """
    ws = MockWorksheet()
    
    # Row 1: Name
    ws["B1"] = "John Doe"
    
    # Slope and Intercept formulas
    ws["B30"] = "=SLOPE(B19:B26,A19:A26)"
    ws["B31"] = "=INTERCEPT(B19:B26,A19:A26)"
    
    # Predictions (E19:E35)
    for row in range(19, 36):
        ws[f"E{row}"] = f"=B30*D{row}+B31"
        ws[f"D{row}"] = row - 18  # Years of experience (1-17)
    
    return ws


@pytest.fixture
def unit_conversions_worksheet():
    """
    Provide a MockWorksheet pre-populated with valid Unit Conversions data.
    
    This represents a "perfect" submission for testing full-score scenarios.
    """
    ws = MockWorksheet()
    
    # Row 26: mcg/mg and ml/tsp conversions
    ws["C26"] = 100  # Starting value
    ws["F26"] = "=L14/I14"  # mcg/mg ratio
    ws["G26"] = "mcg/mg"
    ws["I26"] = "=L17/I17"  # ml/tsp ratio
    ws["J26"] = "ml/tsp"
    ws["O26"] = "=C26*F26*I26"  # Final formula
    ws["P26"] = "mcg/tsp"  # Final unit
    
    # Row 27: gal/l and h/d conversions
    ws["C27"] = 50
    ws["F27"] = "=L15/I15"
    ws["G27"] = "gal/l"
    ws["I27"] = "=L16/I16"
    ws["J27"] = "h/d"
    ws["O27"] = "=C27*F27*I27"
    ws["P27"] = "gal/d"
    
    # Row 28: kg/lb and in/cm (3 ratios)
    ws["C28"] = 75
    ws["F28"] = "=L18/I18"
    ws["G28"] = "kg/lb"
    ws["I28"] = "=L19/I19"
    ws["J28"] = "in/ft"
    ws["L28"] = "=L20/I20"
    ws["M28"] = "cm/in"
    ws["O28"] = "=C28*F28*I28*L28"
    ws["P28"] = "cm/lb"
    
    # Row 29: ft/mi, yr/d, d/h (3 ratios)
    ws["C29"] = 200
    ws["F29"] = "=L21/I21"
    ws["G29"] = "ft/mi"
    ws["I29"] = "=L22/I22"
    ws["J29"] = "yr/d"
    ws["L29"] = "=L23/I23"
    ws["M29"] = "d/h"
    ws["O29"] = "=C29*F29*I29*L29"
    ws["P29"] = "ft/h"
    
    # Temperature conversions
    ws["A40"] = 98.6  # Fahrenheit input
    ws["C40"] = "=(5/9)*(A40-32)"  # F to C formula
    ws["C41"] = 37  # Celsius input
    ws["A41"] = "=(9/5)*C41+32"  # C to F formula
    
    return ws


# ============================================================
# Helper fixtures for date testing
# ============================================================

@pytest.fixture
def today():
    """Return today's date."""
    return datetime.today().date()


@pytest.fixture
def recent_date():
    """Return a date within 21 days of today."""
    return datetime.today() - timedelta(days=10)


@pytest.fixture
def old_date():
    """Return a date more than 21 days ago."""
    return datetime.today() - timedelta(days=30)
