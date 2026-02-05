# writers/generate_course_folders.py

from utilities.logger import get_logger
from utilities.paths import ensure_dir


def generate_course_folders(course_label: str):
    """
    Creates/ensures the course-specific folders exist INSIDE the user's workspace:

        Documents/MA1_Autograder/
            student_groups/COURSE_LABEL
            student_submissions/COURSE_LABEL
            graded_output/COURSE_LABEL

    Returns:
        (folder_safe_label, graded_path, submissions_path)
    """
    logger = get_logger()

    folder_safe_label = course_label.replace(" ", "_").replace("/", "_")

    # Ensure all 3 course folders exist in the workspace
    groups_path = ensure_dir("student_groups", folder_safe_label)
    graded_path = ensure_dir("graded_output", folder_safe_label)
    submissions_path = ensure_dir("student_submissions", folder_safe_label)

    logger.info(f"Workspace folders ready for: {course_label}")
    logger.debug(f"   - Student groups:   {groups_path}")
    logger.debug(f"   - Student files:    {submissions_path}")
    logger.debug(f"   - Graded output:    {graded_path}")

    return folder_safe_label, graded_path, submissions_path
