# writers/create_grading_sheets_from_folder.py

import os
import re
import shutil

from utilities.logger import get_logger
from utilities.paths import ensure_dir, ws_path


def _clean_name_parts_from_folder(folder_name: str):
    """
    Convert folder name like:
      Jonathan_(Jonathan)_Chavez Chaparro_21222530
    into clean:
      first_name='Jonathan', last_name='Chavez Chaparro'

    Rules:
      - split by "_"
      - drop trailing numeric ID tokens
      - drop tokens that are ONLY parenthetical duplicates like "(Jonathan)"
      - remove parentheses characters from remaining tokens
      - collapse consecutive duplicates (Jonathan Jonathan)
      - first = first token
      - last = remaining tokens joined with "_" (keeps multi-part last names)
    """
    parts = [p.strip() for p in str(folder_name).split("_") if p.strip()]

    # Remove pure numeric tokens (student ID)
    parts = [p for p in parts if not p.isdigit()]

    cleaned = []
    for p in parts:
        # Skip pure parenthetical token like "(Jonathan)"
        if re.fullmatch(r"\(.*\)", p):
            continue

        # Remove parentheses characters if embedded
        p = re.sub(r"[()]", "", p).strip()
        if not p:
            continue

        # Skip consecutive duplicate tokens (case-insensitive)
        if cleaned and cleaned[-1].lower() == p.lower():
            continue

        cleaned.append(p)

    if not cleaned:
        return "Unknown", "Unknown"

    first = cleaned[0]
    last = "_".join(cleaned[1:]) if len(cleaned) > 1 else "Unknown"
    return first, last


def create_grading_sheets_from_folder(course_label: str, assignment_type: str = "MA1"):
    """
    Creates (INSIDE WORKSPACE):
        - A clean copy of each student's submission inside:
              student_submissions/<course_label>/First_Last_{assignment_type}.xlsx
        - A grading sheet copy for each student inside:
              graded_output/<course_label>/First_Last_{assignment_type}_Grade.xlsx

    Source of raw folders (INSIDE WORKSPACE):
        student_groups/<course_label>/<student_folder>/

    Args:
        course_label: Course identifier (e.g., "MAT-144-501")
        assignment_type: Type of assignment - "MA1" or "MA3"

    Returns:
        (graded_output_path, submissions_path)
        OR None if the course has no students.
    """
    logger = get_logger()

    # Select template based on assignment type
    if assignment_type == "MA3":
        template_name = "MA3_Grading_Sheet_Template.xlsx"
    else:
        template_name = "Grading_Sheet_Template.xlsx"
    
    template_path = ws_path("templates", template_name)

    # [OK] Course folders inside workspace
    student_groups_path = ensure_dir("student_groups", course_label)
    graded_output_path = ensure_dir("graded_output", course_label)
    submissions_path = ensure_dir("student_submissions", course_label)

    # ---- Validate template exists ----
    if not os.path.exists(template_path):
        raise FileNotFoundError(
            f"[ERROR] Grading sheet template not found at:\n{template_path}\n\n"
            f"Place it in Documents/MA1_Autograder/templates/Grading_Sheet_Template.xlsx"
        )

    # ---- Validate student groups folder ----
    if not os.path.exists(student_groups_path):
        logger.error(f"Source folder not found: {student_groups_path}")
        return None

    # ---- Get raw student folders ----
    student_folders = [
        f for f in os.listdir(student_groups_path)
        if os.path.isdir(os.path.join(student_groups_path, f))
    ]

    if not student_folders:
        logger.warning(f"No student folders found inside: {student_groups_path}")
        return None

    logger.info(f"Creating grading sheets for {len(student_folders)} students")

    prepared_count = 0
    error_count = 0

    # ---- Process each student ----
    for folder_name in student_folders:
        try:
            first_name, last_name = _clean_name_parts_from_folder(folder_name)
            readable_name = f"{first_name}_{last_name}"

            submission_filename = f"{readable_name}_{assignment_type}.xlsx"
            grading_filename = f"{readable_name}_{assignment_type}_Grade.xlsx"

            folder_path = os.path.join(student_groups_path, folder_name)

            excel_files = [f for f in os.listdir(folder_path) if f.endswith(".xlsx")]
            if not excel_files:
                logger.warning(f"No Excel file found inside: {folder_name}")
                continue

            original_submission = os.path.join(folder_path, excel_files[0])
            submission_dest = os.path.join(submissions_path, submission_filename)

            # ---- Copy submission ----
            shutil.copyfile(original_submission, submission_dest)

            # ---- Copy grading template ----
            grading_dest = os.path.join(graded_output_path, grading_filename)
            shutil.copyfile(template_path, grading_dest)

            logger.debug(f"Prepared: {readable_name}")
            prepared_count += 1

        except Exception as e:
            logger.error(f"Error processing folder '{folder_name}': {e}")
            error_count += 1

    logger.info(f"Created {prepared_count} grading sheets ({error_count} errors)")

    return graded_output_path, submissions_path
