# backend/server.py
# FastAPI server that wraps the MA grading pipeline

import os
import sys
import io


def _sanitize_for_windows(text):
    """Remove/replace any characters that Windows cp1252 can't handle."""
    if not isinstance(text, str):
        text = str(text)
    # Replace any character outside ASCII printable range
    return text.encode('ascii', errors='replace').decode('ascii')


# Force UTF-8 encoding for stdout/stderr (fixes Windows charmap encoding errors)
# Note: This may not work in PyInstaller, so we also sanitize in LogCapture
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass  # PyInstaller may not have buffer attribute
import asyncio
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent))

app = FastAPI(title="MA Grader API", version="1.0.0")

# Allow CORS for Electron frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for tracking pipeline progress
pipeline_state = {
    "status": "idle",  # idle, running, completed, error
    "current_step": None,
    "progress": 0,
    "total_steps": 8,
    "logs": [],
    "error": None,
    "output_path": None,
}


class GradeRequest(BaseModel):
    zip_path: str
    course_label: str
    assignment_type: str = "MA1"  # MA1, MA2, MA3
    workspace_path: Optional[str] = None  # Custom workspace location


class ConfigRequest(BaseModel):
    workspace_path: Optional[str] = None


# Workspace path override (set per request)
_workspace_override: Optional[str] = None


def set_workspace_override(path: Optional[str]):
    """Set workspace path override for the current grading session"""
    global _workspace_override
    _workspace_override = path
    
    # Update the utilities.paths module
    try:
        from utilities.paths import set_custom_workspace
        set_custom_workspace(path)
    except Exception as e:
        print(f"Warning: Could not set custom workspace: {e}")


def get_workspace_root():
    """Get current workspace root (override or default)"""
    if _workspace_override:
        return _workspace_override
    try:
        from utilities.paths import workspace_root
        return workspace_root()
    except Exception:
        return os.getcwd()


# ============ Logging Capture ============

class LogCapture:
    """
    Captures print statements using StringIO (never touches real stdout).
    This completely avoids Windows encoding issues because StringIO is pure Python.
    """
    def __init__(self):
        self.buffer = io.StringIO()
        
    def write(self, msg):
        # Write to StringIO (never fails - it's just memory)
        self.buffer.write(msg)
        # Also add to pipeline logs (sanitized)
        if msg.strip():
            safe_msg = _sanitize_for_windows(msg.strip())
            pipeline_state["logs"].append(safe_msg)
        
    def flush(self):
        pass  # StringIO doesn't need flushing
    
    def getvalue(self):
        return self.buffer.getvalue()


# ============ API Endpoints ============

@app.get("/")
async def root():
    return {"status": "ok", "service": "MA Grader API"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/state")
async def get_state():
    """Get current pipeline state"""
    return pipeline_state


@app.post("/reset")
async def reset_state():
    """Reset pipeline state"""
    pipeline_state.update({
        "status": "idle",
        "current_step": None,
        "progress": 0,
        "logs": [],
        "error": None,
        "output_path": None,
    })
    return {"status": "reset"}


@app.post("/grade")
async def start_grading(request: GradeRequest, background_tasks: BackgroundTasks):
    """Start the grading pipeline"""
    
    if pipeline_state["status"] == "running":
        raise HTTPException(status_code=409, detail="Pipeline already running")
    
    # Validate inputs
    if not os.path.exists(request.zip_path):
        raise HTTPException(status_code=400, detail=f"ZIP file not found: {request.zip_path}")
    
    if not request.course_label.strip():
        raise HTTPException(status_code=400, detail="Course label is required")
    
    # Set workspace override if provided
    if request.workspace_path:
        if not os.path.isdir(request.workspace_path):
            raise HTTPException(status_code=400, detail=f"Workspace folder not found: {request.workspace_path}")
        set_workspace_override(request.workspace_path)
    else:
        set_workspace_override(None)
    
    # Reset state
    pipeline_state.update({
        "status": "running",
        "current_step": "initializing",
        "progress": 0,
        "logs": [],
        "error": None,
        "output_path": None,
    })
    
    # Run pipeline in background
    background_tasks.add_task(run_pipeline_task, request.zip_path, request.course_label)
    
    return {"status": "started", "message": "Pipeline started"}


async def run_pipeline_task(zip_path: str, course_label: str):
    """Background task that runs the grading pipeline"""
    
    # Capture stdout
    log_capture = LogCapture()
    old_stdout = sys.stdout
    sys.stdout = log_capture
    
    try:
        # Import here to avoid circular imports
        from run_pipeline import run_pipeline
        from writers.ensure_workspace_assets import ensure_workspace_assets
        from writers.generate_course_folders import generate_course_folders
        from writers.import_zip_to_student_groups import import_zip_to_student_groups
        from writers.create_grading_sheet import create_grading_sheets_from_folder
        from orchestrator import (
            phase1_grade_all_students,
            phase2_export_all_charts,
            phase3_insert_all_charts,
            phase4_cleanup_temp
        )
        from writers.build_instructor_master_workbook import build_instructor_master_workbook
        from utilities.paths import ensure_dir
        
        # Step 1: Ensure workspace assets
        pipeline_state["current_step"] = "Preparing workspace assets..."
        pipeline_state["progress"] = 1
        ensure_workspace_assets()
        
        # Step 2: Create course folders
        pipeline_state["current_step"] = "Creating course folders..."
        pipeline_state["progress"] = 2
        folder_safe, graded_path, submissions_path = generate_course_folders(course_label)
        
        # Step 3: Import ZIP
        pipeline_state["current_step"] = "Importing student submissions..."
        pipeline_state["progress"] = 3
        import_zip_to_student_groups(zip_path, folder_safe)
        
        # Step 4: Create grading sheets
        pipeline_state["current_step"] = "Creating grading sheets..."
        pipeline_state["progress"] = 4
        create_grading_sheets_from_folder(folder_safe)
        
        # Step 5: Grade all students
        pipeline_state["current_step"] = "Grading formulas..."
        pipeline_state["progress"] = 5
        phase1_grade_all_students(submissions_path, graded_path)
        
        # Step 6: Export charts
        pipeline_state["current_step"] = "Exporting charts..."
        pipeline_state["progress"] = 6
        phase2_export_all_charts(submissions_path)
        
        # Step 7: Insert charts
        pipeline_state["current_step"] = "Inserting charts into grading sheets..."
        pipeline_state["progress"] = 7
        phase3_insert_all_charts(graded_path)
        
        # Step 8: Cleanup and build master
        pipeline_state["current_step"] = "Building instructor master workbook..."
        pipeline_state["progress"] = 8
        temp_charts_dir = ensure_dir("temp_charts")
        phase4_cleanup_temp(temp_charts_dir)
        build_instructor_master_workbook(graded_path)
        
        # Done!
        pipeline_state["status"] = "completed"
        pipeline_state["current_step"] = "Complete!"
        pipeline_state["output_path"] = graded_path
        print(f"\n[SUCCESS] Grading complete! Output: {graded_path}")
        
    except Exception as e:
        pipeline_state["status"] = "error"
        pipeline_state["current_step"] = "Error"
        # Sanitize error message to prevent encoding issues
        error_msg = _sanitize_for_windows(str(e))
        # Add diagnostic info for encoding errors
        if "encode" in str(e).lower() or "codec" in str(e).lower():
            error_msg += " [Hint: Check student files for emoji/special characters]"
        pipeline_state["error"] = error_msg
        print(f"\n[ERROR] {error_msg}")
        
    finally:
        sys.stdout = old_stdout


@app.get("/folders/output")
async def get_output_folder():
    """Get the output folder path"""
    if pipeline_state["output_path"]:
        return {"path": pipeline_state["output_path"]}
    raise HTTPException(status_code=404, detail="No output folder yet")


@app.post("/folders/open")
async def open_folder(path: str):
    """Open a folder in the system file browser"""
    import subprocess
    import platform
    
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Path not found: {path}")
    
    system = platform.system()
    if system == "Darwin":
        subprocess.run(["open", path])
    elif system == "Windows":
        subprocess.run(["explorer", path])
    else:
        subprocess.run(["xdg-open", path])
    
    return {"status": "opened", "path": path}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8765)
