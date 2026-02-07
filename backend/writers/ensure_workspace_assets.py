import os
import shutil

from utilities.paths import ensure_dir, ws_path

def ensure_workspace_assets():
    """
    Ensures required assets exist in the workspace (Documents/MA1_Autograder).
    If missing, copies them from the app folder (project/exe directory).
    
    Handles templates and feedback files for MA1 and MA3.
    """

    # Workspace folders
    ensure_dir("templates")
    ensure_dir("feedback")

    # Source paths (relative to project folder or exe folder)
    # This file is in writers/, so project root = one level up
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    src_templates_dir = os.path.join(project_root, "templates")
    src_feedback_dir = os.path.join(project_root, "feedback")

    # ===== TEMPLATES =====
    templates_to_copy = [
        "Grading_Sheet_Template.xlsx",      # MA1
        "Template_Master.xlsx",              # MA1 Master
        "MA3_Grading_Sheet_Template.xlsx",  # MA3
    ]
    
    for template_name in templates_to_copy:
        ws_template = ws_path("templates", template_name)
        src_template = os.path.join(src_templates_dir, template_name)
        
        if not os.path.exists(ws_template):
            if os.path.exists(src_template):
                shutil.copyfile(src_template, ws_template)
            elif template_name == "Grading_Sheet_Template.xlsx":
                # Only error on required template
                raise FileNotFoundError(
                    f"Missing {template_name}.\n"
                    f"Expected either:\n"
                    f" - {ws_template}\n"
                    f" - {src_template}"
                )
    
    # ===== FEEDBACK JSON FILES =====
    feedback_files = [
        "income_analysis.json",
        "unit_conversions.json", 
        "currency_conversion.json",
        "ma3_analysis.json",
        "ma3_visualization.json",
    ]
    
    for feedback_name in feedback_files:
        ws_feedback = ws_path("feedback", feedback_name)
        src_feedback = os.path.join(src_feedback_dir, feedback_name)
        
        if not os.path.exists(ws_feedback):
            if os.path.exists(src_feedback):
                shutil.copyfile(src_feedback, ws_feedback)

    return {
        "grading_template": ws_path("templates", "Grading_Sheet_Template.xlsx"),
        "master_template": ws_path("templates", "Template_Master.xlsx"),
        "ma3_template": ws_path("templates", "MA3_Grading_Sheet_Template.xlsx"),
    }
