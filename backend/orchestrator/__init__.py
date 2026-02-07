"""
orchestrator — Pipeline phase coordination for the MA Grader

Purpose: This package contains the main phases of the grading pipeline.
         Each phase handles a specific part of the workflow, from grading
         formulas to exporting/inserting charts and cleanup.

Author: Clayton Ragsdale
Dependencies: openpyxl, graders.*, writers.*, utilities.*

Pipeline Phases (MA1):
    - Phase 1 (grade_all): Grades all formula-based criteria for each student
    - Phase 2 (export_charts): Exports scatter charts from student workbooks
    - Phase 3 (insert_charts): Inserts charts into grading sheets
    - Phase 4 (cleanup): Removes temporary files

Pipeline Phases (MA3):
    - Phase 1 (grade_all_ma3): Grades Analysis and Visualization tabs
    - Phase 2-4: Same as MA1 (chart handling)
"""

from .phase1_grade_all import phase1_grade_all_students
from .phase1_grade_all_ma3 import phase1_grade_all_students_ma3
from .phase2_export_charts import phase2_export_all_charts
from .phase3_insert_charts import phase3_insert_all_charts
from .phase4_cleanup import phase4_cleanup_temp

__all__ = [
    "phase1_grade_all_students",
    "phase1_grade_all_students_ma3",
    "phase2_export_all_charts",
    "phase3_insert_all_charts",
    "phase4_cleanup_temp"
]
