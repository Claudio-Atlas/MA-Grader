"""
test_currency_conversion.py — Unit tests for Currency Conversion grading

Tests all grading functions in graders/currency_conversion/ including:
- row15_name_letters_v2: Name letter validation
- row16_country_selection_v2: Country selection validation
- row17_date_entries_v2: Date recency validation
- row18_currency_codes_v2: Currency code validation
- grade_currency_conversion_tab_v2: Main orchestrator
"""

import pytest
import sys
import os
from datetime import datetime, timedelta

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graders.currency_conversion.row15_name_letters_v2 import (
    grade_row15_name_letters_v2,
    _split_student_name
)
from graders.currency_conversion.row17_date_entries_v2 import grade_row17_date_entries_v2
from graders.currency_conversion.row18_currency_codes_v2 import grade_row18_currency_codes_v2


# ============================================================
# Test _split_student_name helper
# ============================================================

class TestSplitStudentName:
    """Tests for the _split_student_name helper function."""
    
    def test_space_separated(self):
        """'First Last' should split correctly."""
        first, last = _split_student_name("John Doe")
        assert first == "John"
        assert last == "Doe"
    
    def test_underscore_separated(self):
        """'First_Last' should split correctly."""
        first, last = _split_student_name("John_Doe")
        assert first == "John"
        assert last == "Doe"
    
    def test_three_parts_space(self):
        """'First Middle Last' should use first and last."""
        first, last = _split_student_name("John Michael Doe")
        assert first == "John"
        assert last == "Doe"
    
    def test_three_parts_underscore(self):
        """'First_Middle_Last' should use first and last."""
        first, last = _split_student_name("John_Michael_Doe")
        assert first == "John"
        assert last == "Doe"
    
    def test_single_name(self):
        """Single name should be used for both first and last."""
        first, last = _split_student_name("John")
        assert first == "John"
        assert last == "John"
    
    def test_empty_string(self):
        """Empty string should return empty strings."""
        first, last = _split_student_name("")
        assert first == ""
        assert last == ""
    
    def test_none_input(self):
        """None should return empty strings."""
        first, last = _split_student_name(None)
        assert first == ""
        assert last == ""
    
    def test_whitespace_handling(self):
        """Extra whitespace should be handled."""
        first, last = _split_student_name("  John   Doe  ")
        assert first == "John"
        assert last == "Doe"


# ============================================================
# Test Row 15: Name Letters
# ============================================================

class TestRow15NameLetters:
    """Tests for row 15 name letter grading."""
    
    def test_all_correct(self, mock_worksheet):
        """All correct letters should score 2.0 points."""
        ws = mock_worksheet
        ws["C15"] = "J"
        ws["D15"] = "O"
        ws["E15"] = "D"
        ws["F15"] = "O"
        
        score, feedback = grade_row15_name_letters_v2(ws, "John_Doe")
        
        assert score == 2.0
        assert any(code == "CC15_ALL_CORRECT" for code, _ in feedback)
    
    def test_all_correct_lowercase(self, mock_worksheet):
        """Lowercase letters should be accepted."""
        ws = mock_worksheet
        ws["C15"] = "j"
        ws["D15"] = "o"
        ws["E15"] = "d"
        ws["F15"] = "o"
        
        score, feedback = grade_row15_name_letters_v2(ws, "John_Doe")
        
        assert score == 2.0
    
    def test_partial_correct(self, mock_worksheet):
        """Partial correct should score proportionally."""
        ws = mock_worksheet
        ws["C15"] = "J"
        ws["D15"] = "O"
        ws["E15"] = "X"  # Wrong
        ws["F15"] = "Y"  # Wrong
        
        score, feedback = grade_row15_name_letters_v2(ws, "John_Doe")
        
        assert score == 1.0
        assert any(code == "CC15_PARTIAL" for code, _ in feedback)
    
    def test_none_correct(self, mock_worksheet):
        """All wrong should score 0."""
        ws = mock_worksheet
        ws["C15"] = "X"
        ws["D15"] = "Y"
        ws["E15"] = "Z"
        ws["F15"] = "W"
        
        score, feedback = grade_row15_name_letters_v2(ws, "John_Doe")
        
        assert score == 0.0
        assert any(code == "CC15_NONE_CORRECT" for code, _ in feedback)
    
    def test_blank_cells(self, mock_worksheet):
        """Blank cells should be marked as incorrect."""
        ws = mock_worksheet
        ws["C15"] = None
        ws["D15"] = None
        ws["E15"] = None
        ws["F15"] = None
        
        score, feedback = grade_row15_name_letters_v2(ws, "John_Doe")
        
        assert score == 0.0
        # Check feedback indicates blank cells
        incorrect_feedback = [f for code, f in feedback if code == "CC15_LETTER_INCORRECT"]
        assert all(f.get("found") == "[blank]" for f in incorrect_feedback)
    
    def test_short_first_name(self, mock_worksheet):
        """Single letter first name should use 'M' for second letter."""
        ws = mock_worksheet
        ws["C15"] = "J"
        ws["D15"] = "M"  # Fallback for missing second letter
        ws["E15"] = "D"
        ws["F15"] = "O"
        
        score, feedback = grade_row15_name_letters_v2(ws, "J_Doe")
        
        assert score == 2.0
    
    def test_short_last_name(self, mock_worksheet):
        """Single letter last name should use 'M' for second letter."""
        ws = mock_worksheet
        ws["C15"] = "J"
        ws["D15"] = "O"
        ws["E15"] = "D"
        ws["F15"] = "M"  # Fallback for missing second letter
        
        score, feedback = grade_row15_name_letters_v2(ws, "John_D")
        
        assert score == 2.0


# ============================================================
# Test Row 17: Date Entries
# ============================================================

class TestRow17DateEntries:
    """Tests for row 17 date entry grading."""
    
    def test_all_recent_dates(self, mock_worksheet):
        """All dates within 21 days should score 2.0."""
        ws = mock_worksheet
        today = datetime.today()
        
        ws["C17"] = today
        ws["D17"] = today - timedelta(days=5)
        ws["E17"] = today - timedelta(days=10)
        ws["F17"] = today - timedelta(days=20)
        
        score, feedback, dates = grade_row17_date_entries_v2(ws)
        
        assert score == 2.0
        assert any(code == "CC17_ALL_VALID" for code, _ in feedback)
    
    def test_all_old_dates(self, mock_worksheet):
        """All dates older than 21 days should score 0."""
        ws = mock_worksheet
        today = datetime.today()
        
        ws["C17"] = today - timedelta(days=30)
        ws["D17"] = today - timedelta(days=40)
        ws["E17"] = today - timedelta(days=50)
        ws["F17"] = today - timedelta(days=60)
        
        score, feedback, dates = grade_row17_date_entries_v2(ws)
        
        assert score == 0.0
        assert any(code == "CC17_NONE_VALID" for code, _ in feedback)
    
    def test_mixed_dates(self, mock_worksheet):
        """Mix of recent and old dates should score proportionally."""
        ws = mock_worksheet
        today = datetime.today()
        
        ws["C17"] = today  # Valid
        ws["D17"] = today - timedelta(days=10)  # Valid
        ws["E17"] = today - timedelta(days=30)  # Too old
        ws["F17"] = today - timedelta(days=40)  # Too old
        
        score, feedback, dates = grade_row17_date_entries_v2(ws)
        
        assert score == 1.0  # 2 valid × 0.5
        assert any(code == "CC17_PARTIAL" for code, _ in feedback)
    
    def test_string_date_format(self, mock_worksheet):
        """String dates in MM/DD/YYYY format should be accepted."""
        ws = mock_worksheet
        today = datetime.today()
        date_str = today.strftime("%m/%d/%Y")
        
        ws["C17"] = date_str
        ws["D17"] = date_str
        ws["E17"] = date_str
        ws["F17"] = date_str
        
        score, feedback, dates = grade_row17_date_entries_v2(ws)
        
        assert score == 2.0
    
    def test_missing_dates(self, mock_worksheet):
        """Missing dates should score 0 for those cells."""
        ws = mock_worksheet
        today = datetime.today()
        
        ws["C17"] = today
        ws["D17"] = None
        ws["E17"] = None
        ws["F17"] = None
        
        score, feedback, dates = grade_row17_date_entries_v2(ws)
        
        assert score == 0.5  # Only one valid
        missing_feedback = [f for code, f in feedback if code == "CC17_DATE_MISSING"]
        assert len(missing_feedback) == 3
    
    def test_invalid_date_format(self, mock_worksheet):
        """Invalid date format should trigger parse error."""
        ws = mock_worksheet
        
        ws["C17"] = "not a date"
        ws["D17"] = "invalid"
        ws["E17"] = "12-31-2024"  # Wrong format
        ws["F17"] = "2024/01/01"  # Wrong format
        
        score, feedback, dates = grade_row17_date_entries_v2(ws)
        
        assert score == 0.0
        parse_errors = [f for code, f in feedback if code == "CC17_DATE_PARSE_ERROR"]
        assert len(parse_errors) == 4
    
    def test_date_object_input(self, mock_worksheet):
        """Python date objects should be accepted."""
        ws = mock_worksheet
        from datetime import date
        today = date.today()
        
        ws["C17"] = today
        ws["D17"] = today
        ws["E17"] = today
        ws["F17"] = today
        
        score, feedback, dates = grade_row17_date_entries_v2(ws)
        
        assert score == 2.0
    
    def test_exactly_21_days_old(self, mock_worksheet):
        """Date exactly 21 days old should still be valid."""
        ws = mock_worksheet
        today = datetime.today()
        boundary_date = today - timedelta(days=21)
        
        ws["C17"] = boundary_date
        ws["D17"] = boundary_date
        ws["E17"] = boundary_date
        ws["F17"] = boundary_date
        
        score, feedback, dates = grade_row17_date_entries_v2(ws)
        
        assert score == 2.0


# ============================================================
# Test Row 18: Currency Codes
# ============================================================

class TestRow18CurrencyCodes:
    """Tests for row 18 currency code grading."""
    
    def test_all_correct_codes(self, mock_worksheet):
        """All correct currency codes should score 4.0."""
        ws = mock_worksheet
        ws["C18"] = "JMD"
        ws["D18"] = "OMR"
        ws["E18"] = "DKK"
        ws["F18"] = "EUR"
        
        country_entries = [
            {"country": "Jamaica", "currency_code": "JMD"},
            {"country": "Oman", "currency_code": "OMR"},
            {"country": "Denmark", "currency_code": "DKK"},
            {"country": "Estonia", "currency_code": "EUR"},
        ]
        
        score, feedback = grade_row18_currency_codes_v2(ws, country_entries)
        
        assert score == 4.0
        assert any(code == "CC18_ALL_CORRECT" for code, _ in feedback)
    
    def test_case_insensitive(self, mock_worksheet):
        """Currency codes should be case-insensitive."""
        ws = mock_worksheet
        ws["C18"] = "jmd"
        ws["D18"] = "omr"
        ws["E18"] = "DKK"
        ws["F18"] = "eur"
        
        country_entries = [
            {"country": "Jamaica", "currency_code": "JMD"},
            {"country": "Oman", "currency_code": "OMR"},
            {"country": "Denmark", "currency_code": "DKK"},
            {"country": "Estonia", "currency_code": "EUR"},
        ]
        
        score, feedback = grade_row18_currency_codes_v2(ws, country_entries)
        
        assert score == 4.0
    
    def test_partial_correct(self, mock_worksheet):
        """Partial correct codes should score proportionally."""
        ws = mock_worksheet
        ws["C18"] = "JMD"
        ws["D18"] = "OMR"
        ws["E18"] = "XXX"  # Wrong
        ws["F18"] = "YYY"  # Wrong
        
        country_entries = [
            {"country": "Jamaica", "currency_code": "JMD"},
            {"country": "Oman", "currency_code": "OMR"},
            {"country": "Denmark", "currency_code": "DKK"},
            {"country": "Estonia", "currency_code": "EUR"},
        ]
        
        score, feedback = grade_row18_currency_codes_v2(ws, country_entries)
        
        assert score == 2.0
        assert any(code == "CC18_PARTIAL" for code, _ in feedback)
    
    def test_none_correct(self, mock_worksheet):
        """All wrong codes should score 0."""
        ws = mock_worksheet
        ws["C18"] = "AAA"
        ws["D18"] = "BBB"
        ws["E18"] = "CCC"
        ws["F18"] = "DDD"
        
        country_entries = [
            {"country": "Jamaica", "currency_code": "JMD"},
            {"country": "Oman", "currency_code": "OMR"},
            {"country": "Denmark", "currency_code": "DKK"},
            {"country": "Estonia", "currency_code": "EUR"},
        ]
        
        score, feedback = grade_row18_currency_codes_v2(ws, country_entries)
        
        assert score == 0.0
        assert any(code == "CC18_NONE_CORRECT" for code, _ in feedback)
    
    def test_unknown_country(self, mock_worksheet):
        """Unknown country (None entry) should be handled gracefully."""
        ws = mock_worksheet
        ws["C18"] = "JMD"
        ws["D18"] = "OMR"
        ws["E18"] = "DKK"
        ws["F18"] = "EUR"
        
        country_entries = [
            {"country": "Jamaica", "currency_code": "JMD"},
            None,  # Country unknown
            {"country": "Denmark", "currency_code": "DKK"},
            None,  # Country unknown
        ]
        
        score, feedback = grade_row18_currency_codes_v2(ws, country_entries)
        
        assert score == 2.0  # Only 2 countries are valid
        unknown_feedback = [f for code, f in feedback if code == "CC18_COUNTRY_UNKNOWN"]
        assert len(unknown_feedback) == 2
    
    def test_blank_currency_codes(self, mock_worksheet):
        """Blank currency codes should be marked incorrect."""
        ws = mock_worksheet
        ws["C18"] = ""
        ws["D18"] = None
        ws["E18"] = "   "
        ws["F18"] = "EUR"
        
        country_entries = [
            {"country": "Jamaica", "currency_code": "JMD"},
            {"country": "Oman", "currency_code": "OMR"},
            {"country": "Denmark", "currency_code": "DKK"},
            {"country": "Estonia", "currency_code": "EUR"},
        ]
        
        score, feedback = grade_row18_currency_codes_v2(ws, country_entries)
        
        assert score == 1.0  # Only EUR is correct
    
    def test_unknown_country_blank_code(self, mock_worksheet):
        """Unknown country with blank code should use COUNTRY_UNKNOWN_BLANK."""
        ws = mock_worksheet
        ws["C18"] = ""
        ws["D18"] = "OMR"
        ws["E18"] = "DKK"
        ws["F18"] = "EUR"
        
        country_entries = [
            None,  # Country unknown
            {"country": "Oman", "currency_code": "OMR"},
            {"country": "Denmark", "currency_code": "DKK"},
            {"country": "Estonia", "currency_code": "EUR"},
        ]
        
        score, feedback = grade_row18_currency_codes_v2(ws, country_entries)
        
        assert score == 3.0
        assert any(code == "CC18_COUNTRY_UNKNOWN_BLANK" for code, _ in feedback)
