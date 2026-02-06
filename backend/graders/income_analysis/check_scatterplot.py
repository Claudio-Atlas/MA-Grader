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
import re
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.chart import ScatterChart
from openpyxl.chart.series import XYSeries


def _extract_text_from_title(title_obj) -> str:
    """
    Extract plain text from an openpyxl chart title or axis title object.
    
    The title can be a simple string or a complex RichText object.
    This function handles both cases and extracts the actual text content.
    """
    if title_obj is None:
        return ""
    
    # If it's already a string, return it
    if isinstance(title_obj, str):
        return title_obj.strip()
    
    # Try to get text from RichText structure
    # The text is typically in nested Paragraph -> RegularTextRun -> t attributes
    title_str = str(title_obj)
    
    # Extract all t='...' values from the string representation
    texts = re.findall(r"t='([^']*)'", title_str)
    if texts:
        # Join the text parts and clean up
        result = ' '.join(t for t in texts if t.strip())
        return result.strip()
    
    # Fallback: try common attributes
    if hasattr(title_obj, 'text') and title_obj.text:
        return str(title_obj.text).strip()
    
    return ""


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
    title_text = _extract_text_from_title(scatter_chart.title)
    
    if title_text:
        has_title = True
        score += 1.0
        feedback.append(("IA_SCATTER_TITLE_PRESENT", {"title": title_text}))
    else:
        feedback.append(("IA_SCATTER_TITLE_MISSING", {}))
    
    # ============================================================
    # Step 4: Check X-Axis Label (1 point)
    # ============================================================
    has_x_label = False
    x_axis = scatter_chart.x_axis
    
    if x_axis is not None:
        x_label = _extract_text_from_title(x_axis.title)
        
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
    
    if y_axis is not None:
        y_label = _extract_text_from_title(y_axis.title)
        
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
    #
    # Based on real student data:
    #   - X-data typically ranges from ~10-20 years of education
    #   - Need to extend backward to 8 (about 2 years back)
    #   - Need to extend forward to 24 (about 4 years forward)
    
    extension_correct = False
    
    # Method 1: Check trendline backward/forward extension
    if trendline_obj is not None:
        backward = getattr(trendline_obj, 'backward', None)
        forward = getattr(trendline_obj, 'forward', None)
        
        # Student needs BOTH backward and forward extension
        # Typical data is 10-20, so:
        #   - backward >= 1 extends left toward year 8
        #   - forward >= 1 extends right toward year 24
        # Be generous: any non-zero extension in both directions counts
        has_backward = backward is not None and backward >= 1
        has_forward = forward is not None and forward >= 1
        
        if has_backward and has_forward:
            extension_correct = True
        elif has_forward and forward >= 3:
            # If only forward but it's substantial (reaches ~24), still count it
            extension_correct = True
    
    # Method 2: Check axis scaling (min/max) as fallback
    if not extension_correct and x_axis is not None:
        scaling = getattr(x_axis, 'scaling', None)
        if scaling is not None:
            x_min = getattr(scaling, 'min', None)
            x_max = getattr(scaling, 'max', None)
            
            # Check if axis covers the expected prediction range
            min_ok = x_min is not None and x_min <= 10
            max_ok = x_max is not None and x_max >= 22
            
            if min_ok and max_ok:
                extension_correct = True
            elif max_ok:
                # At least extended to show predictions on right
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
