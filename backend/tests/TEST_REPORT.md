# MA Grader Test Suite Report

**Last Updated:** 2025-02-07  
**Test Framework:** pytest 8.4.2

## Summary

| Metric | Value |
|--------|-------|
| **Total Tests** | 257 |
| **Passed** | 257 (100%) |
| **Failed** | 0 |
| **Coverage** | 55% (overall) |

## Test Files

### 1. `test_normalizers.py` (26 tests)
Tests for `utilities/normalizers.py` - shared normalization functions.

| Test Class | Tests | Description |
|------------|-------|-------------|
| TestNormalizeFormula | 10 | Excel formula normalization (remove $, spaces, uppercase) |
| TestNormalizeUnitText | 9 | Unit label normalization (lowercase, time unit substitutions) |
| TestNormalizeTimeUnit | 6 | Time-specific unit normalization (hr→h, day→d, year→yr) |
| TestNormalizeTempFormula | 7 | Temperature formula normalization |
| TestEdgeCases | 5 | Edge cases (numeric/boolean input, special chars) |

### 2. `test_currency_conversion.py` (31 tests)
Tests for `graders/currency_conversion/` - Currency Conversion tab grading (36 points).

| Test Class | Tests | Description |
|------------|-------|-------------|
| TestSplitStudentName | 8 | Name parsing helper (space/underscore separated) |
| TestRow15NameLetters | 7 | Name letter validation (C15:F15, 2 pts) |
| TestRow17DateEntries | 8 | Date recency validation (C17:F17, 2 pts, ≤21 days) |
| TestRow18CurrencyCodes | 8 | Currency code validation (C18:F18, 4 pts) |

### 3. `test_income_analysis.py` (27 tests)
Tests for `graders/income_analysis/` - Income Analysis tab grading (15 points).

| Test Class | Tests | Description |
|------------|-------|-------------|
| TestCheckNamePresent | 6 | Name presence check (B1, 1 pt) |
| TestCheckSlopeIntercept | 10 | SLOPE/INTERCEPT formula validation (B30/B31, 6 pts) |
| TestHasRequiredRefs | 7 | Helper function for B30/B31 reference checking |
| TestHasYearsRef | 4 | Helper function for D column reference checking |
| TestCheckPredictions | 7 | Prediction formula validation (E19:E35, 6 pts) |
| TestGradeIncomeAnalysis | 4 | Main orchestrator integration tests |

### 4. `test_unit_conversions.py` (58 tests)
Tests for `graders/unit_conversions/` - Unit Conversions tab grading (46 points).

| Test Class | Tests | Description |
|------------|-------|-------------|
| TestNormFormula | 3 | Formula normalization wrapper |
| TestNormUnit | 3 | Unit normalization wrapper |
| TestRow26Grading | 10 | Row 26 (mcg/mg, ml/tsp) conversion grading |
| TestTemperatureConversions | 11 | Temperature formula grading (C40, A41, 4 pts) |
| TestUnitConversionsTabOrchestrator | 6 | Main orchestrator integration tests |
| TestEdgeCases | 4 | Edge cases (spaces, absolute refs, numeric values) |

### 5. `test_edge_cases.py` (26 tests) ✨ NEW
Tests for edge cases and error handling across all modules.

| Test Class | Tests | Description |
|------------|-------|-------------|
| TestEmptySubmissions | 3 | Empty cell handling for all tabs |
| TestUnicodeHandling | 5 | Unicode/emoji/accent character handling |
| TestPartialWork | 5 | Partially completed submissions |
| TestCommonMistakes | 4 | Common student errors (reversed formulas, etc.) |
| TestBoundaryConditions | 3 | Boundary value testing (21-day limit, etc.) |
| TestDataTypeHandling | 4 | Integer/float/boolean in cells |
| TestLongInputs | 2 | Very long strings/formulas |

### 6. `test_validate_submission.py` (13 tests) ✨ NEW
Tests for `utilities/validate_submission.py` - sheet validation.

| Test Class | Tests | Description |
|------------|-------|-------------|
| TestValidateRequiredSheets | 8 | Required sheet presence checking |
| TestGetSheetSafe | 5 | Safe sheet retrieval |
| TestLogMissingSheets | 2 | Logging helper |
| TestRequiredSheetsConstant | 3 | REQUIRED_SHEETS constant |

### 7. `test_server.py` (14 tests) ✨ NEW
Tests for `server.py` - FastAPI API endpoints.

| Test Class | Tests | Description |
|------------|-------|-------------|
| TestSanitizeForWindows | 5 | Windows encoding safety |
| TestLogCapture | 4 | Log capture for frontend |
| TestWorkspaceManagement | 2 | Workspace path handling |
| TestAPIEndpoints | 3 | Pipeline state management |
| TestGradeRequest | 2 | Request model validation |
| TestConfigRequest | 2 | Configuration model |

### 8. `test_orchestrator.py` (15 tests) ✨ NEW
Tests for `orchestrator/` - pipeline orchestration.

| Test Class | Tests | Description |
|------------|-------|-------------|
| TestPhase4Cleanup | 3 | Temp file cleanup |
| TestGradeSingle | 2 | Single file grading |
| TestPhase2ExportCharts | 2 | Chart export |
| TestPhase3InsertCharts | 2 | Chart insertion |
| TestPhase1GradeAll | 3 | Batch grading |
| TestOrchestratorImports | 6 | Module import verification |

### 9. `test_writers.py` (25 tests) ✨ NEW
Tests for `writers/` - output generation.

| Test Class | Tests | Description |
|------------|-------|-------------|
| TestCleanNamePartsFromFolder | 9 | Folder name parsing |
| TestWriteIncomeAnalysisScores | 2 | Score writing |
| TestCreateGradingSheetsFromFolder | 2 | Grading sheet creation |
| TestWriterModuleImports | 8 | Module import verification |
| TestUnitConversionsWriter | 1 | Unit conversions output |
| TestCurrencyConversionWriter | 1 | Currency conversion output |

### 10. `test_integration.py` (22 tests) ✨ NEW
Integration tests using real Excel files.

| Test Class | Tests | Description |
|------------|-------|-------------|
| TestRealFileGrading | 4 | Grading with actual student files |
| TestEdgeCasesWithMockFiles | 3 | Mock file edge cases |
| TestCorruptedFileHandling | 3 | Invalid/corrupt file handling |
| TestZIPProcessing | 2 | ZIP extraction testing |

## Coverage Report

```
Name                                                  Stmts   Miss  Cover
-------------------------------------------------------------------------
graders/income_analysis/check_name_present.py            8      0   100%
graders/income_analysis/check_slope_intercept.py        44      0   100%
graders/income_analysis/grade_income_analysis.py        23      0   100%
graders/unit_conversions/row26_checker_v2.py            59      0   100%
graders/unit_conversions/unit_conversions_checker_v2.py 24      0   100%
graders/currency_conversion/row17_date_entries_v2.py    36      0   100%
graders/currency_conversion/row18_currency_codes_v2.py  26      0   100%
utilities/validate_submission.py                        34      0   100%
utilities/normalizers.py                                41      1    98%
-------------------------------------------------------------------------
TOTAL                                                 1774    795    55%
```

## Grading Coverage

### Income Analysis (15 points)
- ✅ Name presence (1 pt)
- ✅ Slope/Intercept formulas (6 pts)
- ✅ Slope/Intercept formatting (1 pt)
- ✅ Predictions formulas (6 pts)
- ✅ Predictions formatting (1 pt)
- ⚠️ Scatterplot (manual grading, not auto-tested)

### Unit Conversions (46 points)
- ✅ Row 26: mcg/mg, ml/tsp conversions
- ✅ Row 27-29: Other unit conversions
- ✅ Temperature conversions (4 pts)
- ✅ Unit labels, formulas, final calculations

### Currency Conversion (36 points)
- ✅ Row 15: Name letters (2 pts)
- ✅ Row 17: Date entries (2 pts) 
- ✅ Row 18: Currency codes (4 pts)
- ⚠️ Row 16: Country selection (needs real country list)
- ⚠️ Rows 19-21: Exchange rates and formulas (needs API mocking)

## Running Tests

```bash
# Navigate to backend directory
cd ~/Desktop/MA-Grader/backend

# Activate virtual environment
source venv/bin/activate

# Install test dependencies
pip install -r tests/requirements-test.txt

# Run all tests
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ --cov=graders --cov=utilities --cov-report=html

# Run specific test file
python -m pytest tests/test_currency_conversion.py -v

# Run specific test class
python -m pytest tests/test_income_analysis.py::TestCheckSlopeIntercept -v

# Run tests matching pattern
python -m pytest tests/ -k "empty" -v

# Run only integration tests
python -m pytest tests/test_integration.py -v
```

## Test Fixtures

The test suite uses mock worksheet fixtures (`conftest.py`) that simulate openpyxl worksheet behavior:

- `mock_worksheet`: Empty worksheet for custom setup
- `currency_conversion_worksheet`: Pre-populated with valid Currency Conversion data
- `income_analysis_worksheet`: Pre-populated with valid Income Analysis data
- `unit_conversions_worksheet`: Pre-populated with valid Unit Conversions data
- `today`, `recent_date`, `old_date`: Date fixtures for testing

## Future Improvements

1. ✅ **DONE:** Add edge case tests for empty/partial submissions
2. ✅ **DONE:** Add integration tests with real Excel files
3. ✅ **DONE:** Add tests for server.py endpoints
4. ✅ **DONE:** Add tests for writer modules
5. ✅ **DONE:** Add tests for orchestrator modules
6. 📋 **TODO:** Add API mocking for currency conversion exchange rates
7. 📋 **TODO:** Increase coverage to 70%+
8. 📋 **TODO:** Add performance tests for large batch grading
9. 📋 **TODO:** Add property-based testing with Hypothesis
