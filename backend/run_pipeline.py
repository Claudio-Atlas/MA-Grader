# run_pipeline.py

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
    Full MA1 grading pipeline designed for GUI use.

    Args:
        zip_path (str): Path to uploaded ZIP of student submissions
        course_label (str): Course label (e.g., MAT-144-501)

    Returns:
        str: Path to graded_output/<course_label> inside workspace
    """

    course_label = (course_label or "").strip()
    if not course_label:
        raise ValueError("Course label cannot be blank.")

    # -----------------------------
    # STEP 0 - Ensure workspace assets exist
    # (copies templates into Documents/MA1_Autograder/templates if missing)
    # -----------------------------
    ensure_workspace_assets()

    # -----------------------------
    # STEP 1 - Create workspace course folders
    # -----------------------------
    folder_safe, graded_path, submissions_path = generate_course_folders(course_label)

    # -----------------------------
    # STEP 2 - Import ZIP into workspace student_groups/<course>
    # -----------------------------
    import_zip_to_student_groups(zip_path, folder_safe)

    # -----------------------------
    # STEP 3 - Create grading sheets + copy submissions
    # -----------------------------
    create_grading_sheets_from_folder(folder_safe)

    # -----------------------------
    # STEP 4 - Grade all students (formulas)
    # -----------------------------
    phase1_grade_all_students(submissions_path, graded_path)

    # -----------------------------
    # STEP 5 - Export charts (to workspace temp_charts)
    # -----------------------------
    phase2_export_all_charts(submissions_path)

    # -----------------------------
    # STEP 6 - Insert charts into grading sheets
    # -----------------------------
    phase3_insert_all_charts(graded_path)

    # -----------------------------
    # STEP 7 - Cleanup temp files (workspace temp_charts)
    # -----------------------------
    temp_charts_dir = ensure_dir("temp_charts")
    phase4_cleanup_temp(temp_charts_dir)

    # -----------------------------
    # STEP 8 - Build Instructor Master
    # -----------------------------
    build_instructor_master_workbook(graded_path)

    # [OK] IMPORTANT: return a string (no trailing comma)
    return graded_path
