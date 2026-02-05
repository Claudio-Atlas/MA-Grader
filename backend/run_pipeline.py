"""
run_pipeline.py — Main orchestration script for the MA1 grading pipeline

Purpose: Coordinates the complete end-to-end grading workflow for Major Assignment 1.
         This script is the primary entry point when running the grader standalone
         (without the GUI). It imports and executes all pipeline phases in sequence.

Author: Clayton Ragsdale
Dependencies: utilities.paths, writers.*, orchestrator.*
"""

from typing import Tuple

from utilities.paths import ensure_dir
from writers.ensure_workspace_assets import ensure_workspace_assets

from writers.generate_course_folders import generate_course_folders
from writers.create_grading_sheet import create_grading_sheets_from_folder
from writers.import_zip_to_student_groups import import_zip_to_student_groups

from orchestrator import (
    phase1_grade_all_students,
    phase2_export_all_charts,
    phase3_insert_all_charts,
    phase4_cleanup_temp
)

from writers.build_instructor_master_workbook import build_instructor_master_workbook


def run_pipeline(zip_path: str, course_label: str) -> str:
    """
    Execute the complete MA1 grading pipeline from start to finish.
    
    This function orchestrates all 8 steps of the grading process:
    
    1. **Workspace Setup**: Ensures templates and feedback files exist
    2. **Folder Creation**: Creates course-specific folders for organization
    3. **ZIP Import**: Extracts student submissions into the workspace
    4. **Grading Sheet Creation**: Copies template for each student
    5. **Formula Grading**: Grades Income Analysis, Unit Conversions, Currency Conversion
    6. **Chart Export**: Extracts scatter charts from student workbooks (Windows only)
    7. **Chart Insertion**: Embeds charts into grading sheets for manual review
    8. **Master Workbook**: Builds summary workbook with all student scores
    
    Args:
        zip_path: Absolute path to the ZIP file containing student submissions.
                  This should be downloaded directly from the LMS (Canvas, etc.)
        course_label: Course identifier used for folder naming (e.g., "MAT-144-501").
                      Spaces and slashes are automatically converted to underscores.
    
    Returns:
        str: Absolute path to the graded_output/<course_label> folder containing
             all grading sheets and the instructor master workbook.
    
    Raises:
        ValueError: If course_label is blank or empty
        FileNotFoundError: If zip_path doesn't exist or templates are missing
    
    Example:
        >>> graded_path = run_pipeline(
        ...     "/Users/instructor/Downloads/submissions.zip",
        ...     "MAT-144-501"
        ... )
        >>> print(f"Results saved to: {graded_path}")
        Results saved to: /Users/instructor/Documents/MA1_Autograder/graded_output/MAT-144-501
    """

    # Validate course label is not blank
    course_label = (course_label or "").strip()
    if not course_label:
        raise ValueError("Course label cannot be blank.")

    # -----------------------------
    # STEP 0 - Ensure workspace assets exist
    # Copies templates into Documents/MA1_Autograder/templates if missing
    # Also ensures feedback JSON files are present
    # -----------------------------
    ensure_workspace_assets()

    # -----------------------------
    # STEP 1 - Create workspace course folders
    # Creates: student_groups/<course>, student_submissions/<course>, graded_output/<course>
    # Returns sanitized folder name and paths for subsequent steps
    # -----------------------------
    folder_safe, graded_path, submissions_path = generate_course_folders(course_label)

    # -----------------------------
    # STEP 2 - Import ZIP into workspace student_groups/<course>
    # Extracts the downloaded ZIP and organizes student folders
    # Handles nested ZIP structure from various LMS exports
    # -----------------------------
    import_zip_to_student_groups(zip_path, folder_safe)

    # -----------------------------
    # STEP 3 - Create grading sheets + copy submissions
    # For each student folder:
    #   - Copies their submission to student_submissions/<course>/First_Last_MA1.xlsx
    #   - Copies grading template to graded_output/<course>/First_Last_MA1_Grade.xlsx
    # -----------------------------
    create_grading_sheets_from_folder(folder_safe)

    # -----------------------------
    # STEP 4 - Grade all students (formulas)
    # Evaluates all formula-based criteria:
    #   - Income Analysis: SLOPE, INTERCEPT, predictions
    #   - Unit Conversions: Conversion ratios, final formulas
    #   - Currency Conversion: Country selection, exchange rates, budget calculations
    # Writes scores and feedback to each grading sheet
    # -----------------------------
    phase1_grade_all_students(submissions_path, graded_path)

    # -----------------------------
    # STEP 5 - Export charts (to workspace temp_charts)
    # Extracts XY scatter charts from Income Analysis tab (Windows only)
    # On macOS, this step is skipped (charts must be reviewed manually)
    # Charts are saved as PNG files in temp_charts folder
    # -----------------------------
    phase2_export_all_charts(submissions_path)

    # -----------------------------
    # STEP 6 - Insert charts into grading sheets
    # Embeds the exported PNG charts into each student's grading sheet
    # Charts are placed at cell J4 on the Grading Sheet tab
    # Allows instructors to review charts without opening student workbooks
    # -----------------------------
    phase3_insert_all_charts(graded_path)

    # -----------------------------
    # STEP 7 - Cleanup temp files (workspace temp_charts)
    # Deletes the temporary chart images after they've been embedded
    # Keeps the workspace clean and reduces disk usage
    # -----------------------------
    temp_charts_dir = ensure_dir("temp_charts")
    phase4_cleanup_temp(temp_charts_dir)

    # -----------------------------
    # STEP 8 - Build Instructor Master
    # Creates INSTRUCTOR_MASTER.xlsx in the graded_output folder
    # Contains summary sheet with:
    #   - Student names with hyperlinks to individual grading sheets
    #   - Auto-graded totals pulled from each grading sheet
    #   - Manual adjustment column for chart grading
    #   - Final calculated totals
    # -----------------------------
    build_instructor_master_workbook(graded_path)

    # Return the path to the graded output folder
    # IMPORTANT: Return a plain string (no trailing comma) for proper API response
    return graded_path
