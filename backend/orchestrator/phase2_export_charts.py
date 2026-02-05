# orchestrator/phase2_export_charts.py

import os
from typing import Dict, Any, Optional

from utilities.logger import get_logger
from utilities.paths import ensure_dir
from writers.export_chart_to_image import export_chart_to_image


def phase2_export_all_charts(
    submissions_path: str,
    pipeline_state: Optional[Dict[str, Any]] = None
) -> None:
    """
    Exports scatterplot charts for every student submission.
    Safe per-student: one failure won't stop the entire pipeline.

    Exports into workspace: Documents/MA1_Autograder/temp_charts/
    
    Args:
        submissions_path: Path to folder containing student submission files
        pipeline_state: Optional dict for cancellation checking (from server.py)
    """
    logger = get_logger()
    logger.info("")
    logger.info("=" * 60)
    logger.info("PHASE 2 - Exporting scatterplot charts...")
    logger.info("=" * 60)

    temp_dir = ensure_dir("temp_charts")
    logger.debug(f"Chart export directory: {temp_dir}")

    student_files = [f for f in os.listdir(submissions_path) if f.endswith(".xlsx")]
    total_students = len(student_files)
    logger.info(f"Found {total_students} submissions for chart export")

    exported_count = 0
    skipped_count = 0
    error_count = 0

    for idx, filename in enumerate(student_files, 1):
        # Check for cancellation request
        if pipeline_state and pipeline_state.get("cancel_requested"):
            logger.warning(f"Pipeline cancelled by user after exporting {exported_count} charts")
            break

        full_path = os.path.join(submissions_path, filename)
        student_name = filename.replace("_MA1.xlsx", "")

        logger.debug(f"[{idx}/{total_students}] Exporting chart for: {student_name}")

        try:
            result = export_chart_to_image(full_path, image_output_dir=temp_dir)
            if result:
                exported_count += 1
            else:
                skipped_count += 1
        except Exception as e:
            logger.warning(f"  Chart export failed for {filename}: {e}")
            error_count += 1

    # Summary
    logger.info("")
    logger.info("-" * 40)
    logger.info(f"Phase 2 Summary: {exported_count} exported, {skipped_count} skipped, {error_count} errors")
    logger.info("-" * 40)
