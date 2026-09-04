"""Turn analysis signals into practical, single-focus next-run drills."""
from __future__ import annotations

from typing import Any

from .models import TurnAnalysis


def recommendations(turns: list[TurnAnalysis], confidence: int, quality: int) -> list[dict[str, Any]]:
    if not turns or quality < 50:
        return [{
            "focus": "recording quality",
            "title": "Retake a clearer run",
            "drill": "Use a steady downhill/front view, keep the full skier visible, and record at least six linked turns.",
            "success_signal": "The app detects complete turns with data quality above 75%.",
            "priority": "high",
        }]

    result: list[dict[str, Any]] = []
    rotation = sum(turn.upper_body_rotation for turn in turns) / len(turns)
    stance = sum(turn.stance_ratio for turn in turns) / len(turns)
    balance = sum(turn.balance_offset for turn in turns) / len(turns)
    durations = [turn.duration for turn in turns]
    rhythm_spread = (max(durations) - min(durations)) / max(sum(durations) / len(durations), .01)

    if rotation > 18:
        result.append({
            "focus": "upper-body separation",
            "title": "Quiet the shoulders",
            "drill": "On an easy groomer, keep your hands in front and look downhill while your legs steer beneath a stable torso.",
            "success_signal": "Your shoulders stay aimed more consistently downhill through both sides of the turn.",
            "priority": "high",
        })
    if balance > .65:
        result.append({
            "focus": "fore-aft balance",
            "title": "Stay centered",
            "drill": "Make five slow turns with light hands and feel even pressure through the middle of both feet before increasing speed.",
            "success_signal": "Your hip-to-foot balance offset stays below 0.65 through the turn.",
            "priority": "high",
        })
    if stance > 1.35:
        result.append({
            "focus": "ski platform",
            "title": "Narrow the platform",
            "drill": "Traverse gently, bring the skis to a comfortable hip-width stance, then keep them parallel through five turns.",
            "success_signal": "Your stance ratio remains near or below 1.35 without the skis touching.",
            "priority": "medium",
        })
    if rhythm_spread > .75:
        result.append({
            "focus": "rhythm",
            "title": "Make the turns even",
            "drill": "Use a consistent count of ‘turn—two—three’ and begin the next turn as the previous one releases.",
            "success_signal": "Left and right turn durations become more consistent.",
            "priority": "medium",
        })
    if not result:
        result.append({
            "focus": "consistency",
            "title": "Repeat the movement",
            "drill": "Repeat the same run at a comfortable speed and focus on making every turn look like the best turn in the set.",
            "success_signal": "Your overall score and lowest turn score both improve on the next session.",
            "priority": "medium",
        })
    if confidence < 65:
        result.append({
            "focus": "confidence",
            "title": "Improve the camera view",
            "drill": "Move farther away and keep the skier centered so the full body remains visible throughout the run.",
            "success_signal": "Pose confidence reaches at least 65%.",
            "priority": "medium",
        })
    return result[:3]
