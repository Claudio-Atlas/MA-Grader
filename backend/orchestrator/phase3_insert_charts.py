# orchestrator/phase3_insert_charts.py

from utilities.logger import get_logger
from utilities.paths import ensure_dir


def phase3_insert_all_charts(graded_output_path: str) -> None:
    """
    Inserts previously exported charts into final grading sheets.
    Only inserts into THIS COURSE folder.
    
    Args:
        graded_output_path: Path to the graded output folder for this course
    """
    from writers.insert_saved_images_into_grading_sheets import insert_images_into_grading_sheets

    logger = get_logger()
    logger.info("")
    logger.info("=" * 60)
    logger.info("PHASE 3 - Inserting charts into grading sheets...")
    logger.info("=" * 60)

    temp_dir = ensure_dir("temp_charts")
    logger.debug(f"Reading charts from: {temp_dir}")
    logger.debug(f"Inserting into: {graded_output_path}")

    insert_images_into_grading_sheets(
        temp_chart_dir=temp_dir,
        graded_output_dir=graded_output_path
    )
    
    logger.info("Phase 3 complete")
