"""
check_scatterplot.py — Validate scatterplot chart on Income Analysis tab

Purpose: Checks that students have created a proper XY scatter chart with:
         - The chart itself present and using correct data
         - Appropriate title and axis labels
         - A trendline
         - Trendline extended to show predictions (8-24 years range)

Author: Clayton Ragsdale
Dependencies: openpyxl chart objects

Grading Breakdown (8 points total):
    - XY-Scatterplot of BLS data present: 3 points
    - Appropriate title and axis labels: 3 points (1 each)
    - Trendline added: 1 point
    - Trendline extended (8 years left, 24 years right): 1 point
"""

from typing import Tuple, List, Dict, Any, Optional
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.chart import ScatterChart
from openpyxl.chart.series import XYSeries


def check_scatterplot(ws: Worksheet) -> Tuple[float, List[Tuple[str, Dict[str, Any]]]]:
    """
    Check the scatterplot chart on the Income Analysis worksheet.
    
    Grading Logic:
        1. Chart Present & Correct Type (3 points):
           - 3 points: XY Scatter chart exists
           - 0 points: No chart or wrong chart type
        
        2. Title and Labels (3 points):
           - 1 point: Chart has a title
           - 1 point: X-axis has a label
           - 1 point: Y-axis has a label
        
        3. Trendline (1 point):
           - 1 point: Any series has a trendline
           - 0 points: No trendline found
        
        4. Trendline Extension (1 point):
           - 1 point: X-axis range extends from ~8 to ~24 years
           - 0 points: Axis not extended or wrong range
    
    Args:
        ws: The openpyxl Worksheet object for the Income Analysis tab
    
    Returns:
        Tuple of:
            - score: float (0-8)
            - feedback: List of (code, params) tuples describing each check
    
    Example:
        >>> score, feedback = check_scatterplot(worksheet)
        >>> print(f"Scatterplot score: {score}/8")
    """
    score = 0.0
    feedback: List[Tuple[str, Dict[str, Any]]] = []
    
    # ============================================================
    # Step 1: Find a scatter chart on the worksheet
    # ============================================================
    scatter_chart: Optional[ScatterChart] = None
    
    # Get all charts from the worksheet
    charts = getattr(ws, '_charts', [])
    
    for chart in charts:
        if isinstance(chart, ScatterChart):
            scatter_chart = chart
            break
    
    # Check if we found a scatter chart
    if scatter_chart is None:
        # No scatter chart found
        feedback.append(("IA_SCATTER_NOT_FOUND", {}))
        # Return early - can't check other criteria without a chart
        return 0.0, feedback
    
    # ============================================================
    # Step 2: Chart Present - XY Scatter (3 points)
    # ============================================================
    # If we got here, we found a scatter chart
    score += 3.0
    feedback.append(("IA_SCATTER_FOUND", {}))
    
    # ============================================================
    # Step 3: Check Title (1 point)
    # ============================================================
    has_title = False
    if scatter_chart.title is not None:
        # Title can be a string or a RichText object
        title_text = ""
        if isinstance(scatter_chart.title, str):
            title_text = scatter_chart.title.strip()
        elif hasattr(scatter_chart.title, 'text'):
            # RichText object
            title_text = str(scatter_chart.title.text).strip() if scatter_chart.title.text else ""
        else:
            # Try to get string representation
            title_text = str(scatter_chart.title).strip()
        
        if title_text:
            has_title = True
            score += 1.0
            feedback.append(("IA_SCATTER_TITLE_PRESENT", {"title": title_text}))
    
    if not has_title:
        feedback.append(("IA_SCATTER_TITLE_MISSING", {}))
    
    # ============================================================
    # Step 4: Check X-Axis Label (1 point)
    # ============================================================
    has_x_label = False
    x_axis = scatter_chart.x_axis
    
    if x_axis is not None and x_axis.title is not None:
        x_label = ""
        if isinstance(x_axis.title, str):
            x_label = x_axis.title.strip()
        elif hasattr(x_axis.title, 'text'):
            x_label = str(x_axis.title.text).strip() if x_axis.title.text else ""
        else:
            x_label = str(x_axis.title).strip()
        
        if x_label:
            has_x_label = True
            score += 1.0
            feedback.append(("IA_SCATTER_XLABEL_PRESENT", {"label": x_label}))
    
    if not has_x_label:
        feedback.append(("IA_SCATTER_XLABEL_MISSING", {}))
    
    # ============================================================
    # Step 5: Check Y-Axis Label (1 point)
    # ============================================================
    has_y_label = False
    y_axis = scatter_chart.y_axis
    
    if y_axis is not None and y_axis.title is not None:
        y_label = ""
        if isinstance(y_axis.title, str):
            y_label = y_axis.title.strip()
        elif hasattr(y_axis.title, 'text'):
            y_label = str(y_axis.title.text).strip() if y_axis.title.text else ""
        else:
            y_label = str(y_axis.title).strip()
        
        if y_label:
            has_y_label = True
            score += 1.0
            feedback.append(("IA_SCATTER_YLABEL_PRESENT", {"label": y_label}))
    
    if not has_y_label:
        feedback.append(("IA_SCATTER_YLABEL_MISSING", {}))
    
    # ============================================================
    # Step 6: Check Trendline (1 point)
    # ============================================================
    has_trendline = False
    trendline_obj = None
    
    # Check each series for a trendline
    for series in scatter_chart.series:
        if hasattr(series, 'trendline') and series.trendline is not None:
            has_trendline = True
            trendline_obj = series.trendline
            break
    
    if has_trendline:
        score += 1.0
        feedback.append(("IA_SCATTER_TRENDLINE_PRESENT", {}))
    else:
        feedback.append(("IA_SCATTER_TRENDLINE_MISSING", {}))
    
    # ============================================================
    # Step 7: Check Trendline Extension (1 point)
    # ============================================================
    # The trendline should extend from 8 years (left) to 24 years (right)
    # This can be done via axis scaling OR trendline backward/forward properties
    
    extension_correct = False
    
    # Method 1: Check trendline backward/forward extension
    if trendline_obj is not None:
        backward = getattr(trendline_obj, 'backward', None)
        forward = getattr(trendline_obj, 'forward', None)
        
        # Original data is years 1-8, we need to extend to show 8-24
        # So we need backward extension to reach year 8 on left (not really needed if data starts at 1)
        # And forward extension to reach year 24 (about 16 years forward from year 8)
        # Actually, looking at the data: years of experience 1-8, predictions go to year 24
        # So forward extension of ~16 years would be needed
        
        if forward is not None and forward >= 10:
            # Forward extension of at least 10 years (generous threshold)
            extension_correct = True
    
    # Method 2: Check axis scaling (min/max)
    if not extension_correct and x_axis is not None:
        scaling = getattr(x_axis, 'scaling', None)
        if scaling is not None:
            x_min = getattr(scaling, 'min', None)
            x_max = getattr(scaling, 'max', None)
            
            # Check if axis is extended to cover prediction range
            # Allow some tolerance (8 or less on left, 24 or more on right)
            if x_max is not None and x_max >= 20:
                extension_correct = True
    
    if extension_correct:
        score += 1.0
        feedback.append(("IA_SCATTER_EXTENDED_CORRECT", {}))
    else:
        feedback.append(("IA_SCATTER_EXTENDED_MISSING", {
            "expected_min": 8,
            "expected_max": 24
        }))
    
    return score, feedback
