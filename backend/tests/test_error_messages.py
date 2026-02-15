# tests/test_error_messages.py
"""
Tests for user-friendly error message system.

Ensures that technical exceptions are properly converted to
instructor-friendly messages with actionable guidance.
"""

import pytest
from utilities.errors import (
    ErrorCategory,
    GradingError,
    GradingResult,
    classify_error,
    format_error_summary,
    parse_file_not_found,
    parse_key_error,
    parse_zip_error,
    parse_encoding_error,
    parse_value_error,
    parse_permission_error,
)


class TestGradingError:
    """Tests for GradingError dataclass."""
    
    def test_create_grading_error(self):
        """Should create a GradingError with all fields."""
        error = GradingError(
            category=ErrorCategory.STUDENT_ISSUE,
            problem="Missing submission file",
            action="Check if student submitted",
            student_name="John Smith",
            technical="FileNotFoundError: /path/to/file.xlsx"
        )
        
        assert error.category == ErrorCategory.STUDENT_ISSUE
        assert error.problem == "Missing submission file"
        assert error.student_name == "John Smith"
    
    def test_to_dict(self):
        """Should convert to JSON-serializable dict."""
        error = GradingError(
            category=ErrorCategory.BLOCKING,
            problem="ZIP corrupted",
            action="Re-download from Canvas",
            student_name=None,
            technical="BadZipFile"
        )
        
        result = error.to_dict()
        
        assert result["category"] == "blocking"
        assert result["problem"] == "ZIP corrupted"
        assert result["action"] == "Re-download from Canvas"
        assert result["student_name"] is None
    
    def test_str_with_student_name(self):
        """Should include student name in string representation."""
        error = GradingError(
            category=ErrorCategory.STUDENT_ISSUE,
            problem="Wrong file format",
            action="Ask for .xlsx",
            student_name="Jane Doe"
        )
        
        assert str(error) == "Jane Doe: Wrong file format"
    
    def test_str_without_student_name(self):
        """Should work without student name."""
        error = GradingError(
            category=ErrorCategory.BLOCKING,
            problem="Template missing",
            action="Re-download template"
        )
        
        assert str(error) == "Template missing"


class TestGradingResult:
    """Tests for GradingResult tracker."""
    
    def test_empty_result(self):
        """Should start with zero counts."""
        result = GradingResult()
        
        assert result.success_count == 0
        assert len(result.issues) == 0
    
    def test_add_success(self):
        """Should increment success count."""
        result = GradingResult()
        result.add_success()
        result.add_success()
        
        assert result.success_count == 2
    
    def test_add_issue(self):
        """Should track issues."""
        result = GradingResult()
        error = GradingError(
            category=ErrorCategory.STUDENT_ISSUE,
            problem="Test problem",
            action="Test action",
            student_name="Student A"
        )
        result.add_issue(error)
        
        assert len(result.issues) == 1
        assert result.issues[0].student_name == "Student A"
    
    def test_has_blocking_errors(self):
        """Should detect blocking errors."""
        result = GradingResult()
        
        # No errors yet
        assert not result.has_blocking_errors()
        
        # Add student issue (not blocking)
        result.add_issue(GradingError(
            category=ErrorCategory.STUDENT_ISSUE,
            problem="Student issue",
            action="Fix it"
        ))
        assert not result.has_blocking_errors()
        
        # Add blocking error
        result.add_issue(GradingError(
            category=ErrorCategory.BLOCKING,
            problem="Blocking issue",
            action="Stop"
        ))
        assert result.has_blocking_errors()
    
    def test_get_summary(self):
        """Should generate summary dict."""
        result = GradingResult()
        result.add_success()
        result.add_success()
        result.add_issue(GradingError(
            category=ErrorCategory.STUDENT_ISSUE,
            problem="Missing sheet",
            action="Check submission",
            student_name="Student A"
        ))
        
        summary = result.get_summary()
        
        assert summary["success_count"] == 2
        assert summary["issue_count"] == 1
        assert len(summary["student_issues"]) == 1
        assert len(summary["blocking_errors"]) == 0


class TestClassifyError:
    """Tests for error classification."""
    
    def test_file_not_found_submission(self):
        """Should classify missing submission file."""
        error = FileNotFoundError("Submission file not found: /path/student.xlsx")
        result = classify_error(error, student_name="John Smith")
        
        assert result.category == ErrorCategory.STUDENT_ISSUE
        assert "Missing submission" in result.problem
        assert result.student_name == "John Smith"
    
    def test_file_not_found_template(self):
        """Should classify missing template as blocking."""
        error = FileNotFoundError("Grading template not found")
        result = classify_error(error)
        
        assert result.category == ErrorCategory.BLOCKING
        assert "template" in result.problem.lower()
    
    def test_key_error_grading_sheet(self):
        """Should classify missing Grading Sheet tab."""
        error = KeyError("The 'Grading Sheet' tab was not found")
        result = classify_error(error)
        
        assert result.category == ErrorCategory.BLOCKING
        assert "Grading Sheet" in result.problem
    
    def test_key_error_student_sheet(self):
        """Should classify missing student sheet."""
        error = KeyError("Income Analysis")
        result = classify_error(error, student_name="Jane Doe")
        
        assert result.category == ErrorCategory.STUDENT_ISSUE
        assert result.student_name == "Jane Doe"
    
    def test_encoding_error(self):
        """Should classify encoding errors."""
        error = UnicodeDecodeError("charmap", b"", 0, 1, "character maps to <undefined>")
        result = classify_error(error, student_name="Student X")
        
        assert result.category == ErrorCategory.STUDENT_ISSUE
        assert "special characters" in result.problem.lower()
        assert result.student_name == "Student X"
    
    def test_value_error_empty(self):
        """Should classify empty cell errors."""
        error = ValueError("No data found in range")
        result = classify_error(error, student_name="Student Y")
        
        assert result.category == ErrorCategory.STUDENT_ISSUE
    
    def test_permission_error_password(self):
        """Should classify password-protected files."""
        error = PermissionError("File is password protected")
        result = classify_error(error, student_name="Student Z")
        
        assert result.category == ErrorCategory.STUDENT_ISSUE
        assert "password" in result.problem.lower()
    
    def test_unknown_error(self):
        """Should handle unknown errors gracefully."""
        error = RuntimeError("Something unexpected happened")
        result = classify_error(error)
        
        assert result.category == ErrorCategory.BLOCKING
        assert "Unexpected" in result.problem


class TestParseZipError:
    """Tests for ZIP error parsing."""
    
    def test_bad_zip_file(self):
        """Should handle BadZipFile."""
        # Create a mock BadZipFile-like error
        class BadZipFile(Exception):
            pass
        
        error = BadZipFile("File is not a zip file")
        result = parse_zip_error(error)
        
        assert result.category == ErrorCategory.BLOCKING
        assert "valid ZIP" in result.problem
    
    def test_path_traversal(self):
        """Should handle security errors."""
        error = ValueError("Path traversal detected")
        result = parse_zip_error(error)
        
        assert result.category == ErrorCategory.BLOCKING
        assert "security" in result.problem.lower()


class TestFormatErrorSummary:
    """Tests for summary formatting."""
    
    def test_format_success_only(self):
        """Should format successful grading."""
        result = GradingResult()
        result.add_success()
        result.add_success()
        result.add_success()
        
        summary = format_error_summary(result)
        
        assert "3 students graded successfully" in summary
    
    def test_format_with_issues(self):
        """Should include issues in summary."""
        result = GradingResult()
        result.add_success()
        result.add_issue(GradingError(
            category=ErrorCategory.STUDENT_ISSUE,
            problem="Missing file",
            action="Check submission",
            student_name="John"
        ))
        
        summary = format_error_summary(result)
        
        assert "1 students graded" in summary
        assert "1 student issue" in summary
        assert "John" in summary
    
    def test_format_with_blocking(self):
        """Should highlight blocking errors."""
        result = GradingResult()
        result.add_issue(GradingError(
            category=ErrorCategory.BLOCKING,
            problem="ZIP corrupted",
            action="Re-download"
        ))
        
        summary = format_error_summary(result)
        
        assert "blocking error" in summary
        assert "ZIP corrupted" in summary
