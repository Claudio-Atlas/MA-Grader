import os
import shutil

from utilities.paths import ensure_dir, ws_path

def ensure_workspace_assets():
    """
    Ensures required assets exist in the workspace (Documents/MA1_Autograder).
    If missing, copies them from the app folder (project/exe directory).
    """

    # Workspace folders
    ensure_dir("templates")
    ensure_dir("feedback")

    # Workspace target paths
    ws_grading_template = ws_path("templates", "Grading_Sheet_Template.xlsx")
    ws_master_template  = ws_path("templates", "Template_Master.xlsx")

    # Source paths (relative to project folder or exe folder)
    # This file is in writers/, so project root = one level up
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    src_templates_dir = os.path.join(project_root, "templates")

    src_grading_template = os.path.join(src_templates_dir, "Grading_Sheet_Template.xlsx")
    src_master_template  = os.path.join(src_templates_dir, "Template_Master.xlsx")

    # Copy if missing in workspace
    if not os.path.exists(ws_grading_template):
        if not os.path.exists(src_grading_template):
            raise FileNotFoundError(
                f"Missing Grading_Sheet_Template.xlsx.\n"
                f"Expected either:\n"
                f" - {ws_grading_template}\n"
                f" - {src_grading_template}"
            )
        shutil.copyfile(src_grading_template, ws_grading_template)

    if not os.path.exists(ws_master_template):
        if os.path.exists(src_master_template):
            shutil.copyfile(src_master_template, ws_master_template)

    return {
        "grading_template": ws_grading_template,
        "master_template": ws_master_template
    }
