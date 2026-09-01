from __future__ import annotations

from .geometry import mean
from .models import TurnAnalysis


def make_feedback(turns: list[TurnAnalysis], confidence: int) -> tuple[list[str], list[str]]:
    if not turns:
        return [], ["No complete turns were detected. Use a steady downhill/front view with the full skier visible."]
    feedback: list[str] = []
    warnings: list[str] = []
    left = [t for t in turns if t.direction == "left"]
    right = [t for t in turns if t.direction == "right"]
    rotation = mean(t.upper_body_rotation for t in turns)
    if rotation > 18:
        feedback.append("Keep your shoulders quieter and facing more consistently downhill.")
    else:
        feedback.append("Upper-body separation stays consistent through most turns.")
    if left and right:
        left_knee, right_knee = mean(t.knee_flex for t in left), mean(t.knee_flex for t in right)
        if abs(left_knee - right_knee) > 10:
            stiffer = "left" if left_knee > right_knee else "right"
            feedback.append(f"Your {stiffer} turns are noticeably less flexed; match the movement range of the other side.")
        else:
            feedback.append("Left/right knee flexion is well matched.")
    if mean(t.stance_ratio for t in turns) > 1.35:
        feedback.append("Your stance reads wide relative to your shoulders; try a slightly narrower platform.")
    if confidence < 65:
        warnings.append("Low pose confidence: treat scores as directional, not definitive.")
    warnings.append("Coaching aid only—scores do not certify safety or readiness for harder terrain.")
    return feedback[:3], warnings

