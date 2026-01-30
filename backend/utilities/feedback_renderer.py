# utilities/feedback_renderer.py

from utilities.json_loader import load_feedback


def render_feedback(feedback_items, tab_name: str) -> str:
    """
    Convert feedback codes + params into final instructor-facing text
    using feedback/<tab_name>.json.

    feedback_items can be:
      - list of (code, params)
      - list of strings (legacy support)
      - single string
      - None
    """

    if not feedback_items:
        return ""

    # Legacy string
    if isinstance(feedback_items, str):
        return feedback_items

    feedback_map = load_feedback(tab_name)
    lines = []

    # Legacy list of strings
    if isinstance(feedback_items, list) and isinstance(feedback_items[0], str):
        return "\n".join(feedback_items)

    for item in feedback_items:
        if isinstance(item, tuple) and len(item) == 2:
            code, params = item
            template = feedback_map.get(code)

            if template is None:
                # Safe fallback so grading never breaks
                lines.append(f"[{code}] {params}")
                continue

            try:
                lines.append(template.format(**(params or {})))
            except Exception:
                lines.append(f"[FORMAT ERROR] {code}: {params}")
        else:
            lines.append(str(item))

    return "\n".join(lines)
