"""
server.py — FastAPI server for the MA Grader desktop application

Purpose: Provides a REST API that wraps the MA1 grading pipeline, enabling the
         Electron frontend to initiate grading jobs, track progress, and retrieve
         results. Handles background task execution and cross-platform compatibility.

Author: Clayton Ragsdale
Dependencies: FastAPI, uvicorn, openpyxl, pydantic
"""

import os
import sys
import io
from typing import Optional, Dict, Any, List


def _sanitize_for_windows(text: str) -> str:
    """
    Remove or replace any characters that Windows cp1252 can't handle.
    
    Windows console encoding (cp1252) doesn't support many Unicode characters.
    This function ensures log messages and error strings don't crash the app
    when printed on Windows systems.
    
    Args:
        text: Any string that may contain Unicode characters
        
    Returns:
        str: ASCII-safe string with unsupported chars replaced by '?'
    """
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
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# ============ FastAPI Application Setup ============

app = FastAPI(title="MA Grader API", version="1.0.0")

# Allow CORS for Electron frontend
# Using "*" allows any origin since this is a local desktop app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ Global Pipeline State ============

# Tracks the current state of the grading pipeline
# This is a simple in-memory store since only one grading job runs at a time
pipeline_state: Dict[str, Any] = {
    "status": "idle",        # idle, running, completed, error
    "cancel_requested": False,  # Flag for user-initiated cancellation
    "current_step": None,    # Human-readable description of current step
    "progress": 0,           # Current step number (1-8)
    "total_steps": 8,        # Total number of pipeline steps
    "logs": [],              # List of log messages for the frontend
    "error": None,           # Error message if status is "error"
    "output_path": None,     # Path to graded output folder when complete
}


# ============ Request/Response Models ============

class GradeRequest(BaseModel):
    """
    Request model for starting a grading job.
    
    Attributes:
        zip_path: Absolute path to the ZIP file containing student submissions
        course_label: Course identifier (e.g., "MAT-144-501")
        assignment_type: Type of assignment - MA1, MA2, or MA3 (currently only MA1 supported)
        workspace_path: Optional custom workspace location for output files
    """
    zip_path: str
    course_label: str
    assignment_type: str = "MA1"
    workspace_path: Optional[str] = None


class ConfigRequest(BaseModel):
    """
    Request model for configuration settings.
    
    Attributes:
        workspace_path: Optional custom workspace folder path
    """
    workspace_path: Optional[str] = None


# ============ Workspace Management ============

# Custom workspace path override (set per grading session)
_workspace_override: Optional[str] = None


def set_workspace_override(path: Optional[str]) -> None:
    """
    Set a custom workspace path override for the current grading session.
    
    This allows users to specify where grading output should be saved,
    rather than using the default ~/Documents/MA1_Autograder location.
    
    Args:
        path: Absolute path to the workspace folder, or None to use default
    """
    global _workspace_override
    _workspace_override = path
    
    # Update the utilities.paths module so all file operations use the new path
    try:
        from utilities.paths import set_custom_workspace
        set_custom_workspace(path)
    except Exception as e:
        # Use print here since logger may not be set up yet
        pipeline_state["logs"].append(f"[WARN] Could not set custom workspace: {e}")


def get_workspace_root() -> str:
    """
    Get the current workspace root directory.
    
    Returns the custom workspace if set, otherwise returns the default
    workspace path from utilities.paths.
    
    Returns:
        str: Absolute path to the workspace root directory
    """
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
    Captures print statements using StringIO for thread-safe log collection.
    
    This class redirects stdout to capture all print statements during pipeline
    execution. Using StringIO (pure Python) completely avoids Windows encoding
    issues because it's just memory - no OS-level encoding happens.
    
    The captured logs are stored in pipeline_state["logs"] for the frontend
    to display progress information.
    
    Attributes:
        buffer: StringIO instance for capturing output
    """
    
    def __init__(self) -> None:
        """Initialize the log capture with an empty StringIO buffer."""
        self.buffer = io.StringIO()
        
    def write(self, msg: str) -> None:
        """
        Write a message to the buffer and pipeline logs.
        
        Args:
            msg: The message to capture (from print statements)
        """
        # Write to StringIO (never fails - it's just memory)
        self.buffer.write(msg)
        # Also add to pipeline logs (sanitized for Windows compatibility)
        if msg.strip():
            safe_msg = _sanitize_for_windows(msg.strip())
            pipeline_state["logs"].append(safe_msg)
        
    def flush(self) -> None:
        """Flush the buffer (no-op for StringIO)."""
        pass
    
    def getvalue(self) -> str:
        """
        Get all captured output as a single string.
        
        Returns:
            str: All captured output concatenated together
        """
        return self.buffer.getvalue()


# ============ API Endpoints ============

@app.get("/")
async def root() -> Dict[str, str]:
    """
    Health check endpoint - verifies the API server is running.
    
    Returns:
        Dict with status "ok" and service name
    """
    return {"status": "ok", "service": "MA Grader API"}


@app.get("/health")
async def health() -> Dict[str, str]:
    """
    Alternative health check endpoint.
    
    Returns:
        Dict with status "healthy"
    """
    return {"status": "healthy"}


@app.get("/state")
async def get_state() -> Dict[str, Any]:
    """
    Get the current pipeline execution state.
    
    This endpoint is polled by the frontend to display progress during
    grading operations.
    
    Returns:
        Dict containing:
        - status: Current pipeline status (idle/running/completed/error)
        - current_step: Description of the current step
        - progress: Step number (1-8)
        - total_steps: Total number of steps (8)
        - logs: List of log messages
        - error: Error message if failed
        - output_path: Path to output folder when complete
    """
    return pipeline_state


@app.post("/reset")
async def reset_state() -> Dict[str, str]:
    """
    Reset the pipeline state to initial idle state.
    
    Called by the frontend before starting a new grading job to ensure
    clean state.
    
    Returns:
        Dict with status "reset"
    """
    pipeline_state.update({
        "status": "idle",
        "cancel_requested": False,
        "current_step": None,
        "progress": 0,
        "logs": [],
        "error": None,
        "output_path": None,
    })
    return {"status": "reset"}


@app.post("/cancel")
async def cancel_pipeline() -> Dict[str, str]:
    """
    Request cancellation of the currently running pipeline.
    
    Sets the cancel_requested flag which is checked by the grading loops.
    The pipeline will stop at the next safe point (after finishing the
    current student being graded).
    
    Returns:
        Dict with status "cancel_requested" or "not_running"
    """
    if pipeline_state["status"] != "running":
        return {"status": "not_running", "message": "No pipeline is currently running"}
    
    pipeline_state["cancel_requested"] = True
    pipeline_state["logs"].append("[CANCEL] Cancellation requested - stopping after current student...")
    return {"status": "cancel_requested", "message": "Pipeline will stop after current student"}


@app.post("/grade")
async def start_grading(
    request: GradeRequest,
    background_tasks: BackgroundTasks
) -> Dict[str, str]:
    """
    Start the grading pipeline as a background task.
    
    Validates the request, sets up the workspace, and initiates the
    8-step grading pipeline in a background task so the API remains
    responsive for status polling.
    
    Args:
        request: GradeRequest with zip_path, course_label, and optional settings
        background_tasks: FastAPI BackgroundTasks for async execution
    
    Returns:
        Dict with status "started" and confirmation message
    
    Raises:
        HTTPException 409: If a pipeline is already running
        HTTPException 400: If zip_path doesn't exist or course_label is empty
    """
    # Prevent concurrent pipeline runs
    if pipeline_state["status"] == "running":
        raise HTTPException(status_code=409, detail="Pipeline already running")
    
    # Validate that the ZIP file exists
    if not os.path.exists(request.zip_path):
        raise HTTPException(status_code=400, detail=f"ZIP file not found: {request.zip_path}")
    
    # Validate course label is not empty
    if not request.course_label.strip():
        raise HTTPException(status_code=400, detail="Course label is required")
    
    # Set workspace override if provided
    if request.workspace_path:
        if not os.path.isdir(request.workspace_path):
            raise HTTPException(status_code=400, detail=f"Workspace folder not found: {request.workspace_path}")
        set_workspace_override(request.workspace_path)
    else:
        set_workspace_override(None)
    
    # Reset state for new grading job
    pipeline_state.update({
        "status": "running",
        "cancel_requested": False,  # Reset cancellation flag
        "current_step": "initializing",
        "progress": 0,
        "logs": [],
        "error": None,
        "output_path": None,
    })
    
    # Run pipeline in background so API remains responsive
    background_tasks.add_task(run_pipeline_task, request.zip_path, request.course_label)
    
    return {"status": "started", "message": "Pipeline started"}


async def run_pipeline_task(zip_path: str, course_label: str) -> None:
    """
    Execute the full 8-step grading pipeline as a background task.
    
    This function runs all grading steps sequentially, updating the
    pipeline_state as it progresses. Each step's output is captured
    and made available to the frontend for progress display.
    
    Pipeline Steps:
        1. Ensure workspace assets (templates, feedback files)
        2. Create course folders (student_groups, graded_output, etc.)
        3. Import ZIP file into student_groups folder
        4. Create grading sheets from template for each student
        5. Grade all students (formulas, not charts)
        6. Export charts from student workbooks (Windows only)
        7. Insert charts into grading sheets
        8. Build instructor master workbook with summary
    
    Args:
        zip_path: Absolute path to the student submissions ZIP file
        course_label: Course identifier (e.g., "MAT-144-501")
    """
    # Capture stdout to collect all print statements for the frontend
    log_capture = LogCapture()
    old_stdout = sys.stdout
    sys.stdout = log_capture
    
    try:
        # Import pipeline modules here to avoid circular imports
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
        
        # Step 1: Ensure workspace assets exist (templates, feedback JSON)
        pipeline_state["current_step"] = "Preparing workspace assets..."
        pipeline_state["progress"] = 1
        ensure_workspace_assets()
        
        # Step 2: Create course-specific folders in workspace
        pipeline_state["current_step"] = "Creating course folders..."
        pipeline_state["progress"] = 2
        folder_safe, graded_path, submissions_path = generate_course_folders(course_label)
        
        # Step 3: Extract and organize student submissions from ZIP
        pipeline_state["current_step"] = "Importing student submissions..."
        pipeline_state["progress"] = 3
        import_zip_to_student_groups(zip_path, folder_safe)
        
        # Step 4: Create individual grading sheets from template
        pipeline_state["current_step"] = "Creating grading sheets..."
        pipeline_state["progress"] = 4
        create_grading_sheets_from_folder(folder_safe)
        
        # Step 5: Grade all formula-based criteria
        pipeline_state["current_step"] = "Grading formulas..."
        pipeline_state["progress"] = 5
        phase1_grade_all_students(submissions_path, graded_path, pipeline_state)
        
        # Check for cancellation after grading phase
        if pipeline_state.get("cancel_requested"):
            pipeline_state["status"] = "cancelled"
            pipeline_state["current_step"] = "Cancelled"
            print("\n[CANCELLED] Pipeline cancelled by user after grading phase")
            return
        
        # Step 6: Export charts from student workbooks (Windows only)
        pipeline_state["current_step"] = "Exporting charts..."
        pipeline_state["progress"] = 6
        phase2_export_all_charts(submissions_path, pipeline_state)
        
        # Check for cancellation after chart export
        if pipeline_state.get("cancel_requested"):
            pipeline_state["status"] = "cancelled"
            pipeline_state["current_step"] = "Cancelled"
            print("\n[CANCELLED] Pipeline cancelled by user after chart export")
            return
        
        # Step 7: Insert exported charts into grading sheets
        pipeline_state["current_step"] = "Inserting charts into grading sheets..."
        pipeline_state["progress"] = 7
        phase3_insert_all_charts(graded_path)
        
        # Step 8: Build master summary workbook and cleanup
        pipeline_state["current_step"] = "Building instructor master workbook..."
        pipeline_state["progress"] = 8
        temp_charts_dir = ensure_dir("temp_charts")
        phase4_cleanup_temp(temp_charts_dir)
        build_instructor_master_workbook(graded_path)
        
        # Pipeline completed successfully
        pipeline_state["status"] = "completed"
        pipeline_state["current_step"] = "Complete!"
        pipeline_state["output_path"] = graded_path
        print(f"\n[SUCCESS] Grading complete! Output: {graded_path}")
        
    except Exception as e:
        # Pipeline failed - capture error for frontend display
        pipeline_state["status"] = "error"
        pipeline_state["current_step"] = "Error"
        # Sanitize error message to prevent encoding issues
        error_msg = _sanitize_for_windows(str(e))
        # Add diagnostic info for encoding errors (common on Windows)
        if "encode" in str(e).lower() or "codec" in str(e).lower():
            error_msg += " [Hint: Check student files for emoji/special characters]"
        pipeline_state["error"] = error_msg
        print(f"\n[ERROR] {error_msg}")
        
    finally:
        # Restore original stdout
        sys.stdout = old_stdout


@app.get("/folders/output")
async def get_output_folder() -> Dict[str, str]:
    """
    Get the path to the graded output folder.
    
    Returns the output path after a successful grading job completes.
    
    Returns:
        Dict with "path" key containing the output folder path
    
    Raises:
        HTTPException 404: If no grading job has completed yet
    """
    if pipeline_state["output_path"]:
        return {"path": pipeline_state["output_path"]}
    raise HTTPException(status_code=404, detail="No output folder yet")


@app.post("/folders/open")
async def open_folder(path: str) -> Dict[str, str]:
    """
    Open a folder in the system's native file browser.
    
    Cross-platform support for Windows (explorer), macOS (open), 
    and Linux (xdg-open).
    
    Args:
        path: Absolute path to the folder to open
    
    Returns:
        Dict with status "opened" and the path
    
    Raises:
        HTTPException 404: If the path doesn't exist
    """
    import subprocess
    import platform
    
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Path not found: {path}")
    
    # Use platform-appropriate command to open file browser
    system = platform.system()
    if system == "Darwin":      # macOS
        subprocess.run(["open", path])
    elif system == "Windows":   # Windows
        subprocess.run(["explorer", path])
    else:                       # Linux and others
        subprocess.run(["xdg-open", path])
    
    return {"status": "opened", "path": path}


# ============ Main Entry Point ============

if __name__ == "__main__":
    # Run the FastAPI server on localhost:8765
    # This port is also configured in the Electron frontend
    uvicorn.run(app, host="127.0.0.1", port=8765)
