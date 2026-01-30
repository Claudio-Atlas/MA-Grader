# utilities/json_loader.py

import json
import os
from functools import lru_cache

from utilities.paths import ensure_dir, ws_path


@lru_cache(maxsize=None)
def load_feedback(tab_name: str) -> dict:
    """
    Load feedback JSON for a given tab.

    Priority:
      1) Workspace (Documents/MA1_Autograder/feedback/<tab>.json)  <-- instructor-editable
      2) Packaged defaults (project_root/feedback/<tab>.json)

    If workspace file doesn't exist but defaults do, we auto-copy defaults
    into workspace on first run so instructors can edit them later.
    """

    # 1) Workspace path (instructor-editable)
    ensure_dir("feedback")
    workspace_path = ws_path("feedback", f"{tab_name}.json")

    if os.path.exists(workspace_path):
        with open(workspace_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # 2) Default path (bundled with app / repo)
    project_root = os.path.dirname(os.path.dirname(__file__))  # MA1_grader_beta/
    default_path = os.path.join(project_root, "feedback", f"{tab_name}.json")

    if not os.path.exists(default_path):
        raise FileNotFoundError(
            f"Feedback JSON not found.\n"
            f"- Workspace expected: {workspace_path}\n"
            f"- Default expected:   {default_path}\n"
            f"Fix: ensure feedback/{tab_name}.json exists in your project."
        )

    # Auto-copy defaults -> workspace so it's editable for instructors
    try:
        with open(default_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        with open(workspace_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return data

    except Exception as e:
        # If copy fails, still load defaults so the app runs
        with open(default_path, "r", encoding="utf-8") as f:
            return json.load(f)
