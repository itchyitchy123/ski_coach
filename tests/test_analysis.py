from ski_coach.demo import demo_frames
from ski_coach.geometry import angle
from ski_coach.io import frames_from_dict
from ski_coach.models import Landmark, PoseFrame
from ski_coach.pipeline import analyze_landmarks


def test_right_angle():
    assert angle(Landmark(0, 1), Landmark(0, 0), Landmark(1, 0)) == 90


def test_demo_produces_alternating_turns_and_scores():
    report = analyze_landmarks(demo_frames())
    assert report.turns >= 8
    assert {turn.direction for turn in report.turns_analysis} == {"left", "right"}
    assert 0 <= report.overall_score <= 100
    assert report.confidence == 94
    assert report.feedback


def test_missing_landmarks_yields_actionable_warning():
    report = analyze_landmarks([PoseFrame(0, {})])
    assert report.turns == 0
    assert "No complete turns" in report.warnings[-1]


def test_json_boundary_round_trips_landmarks():
    frames = frames_from_dict({"frames": [{"timestamp": 1, "landmarks": {"left_hip": {"x": .2, "y": .3}}}]})
    assert frames[0].timestamp == 1
    assert frames[0].landmarks["left_hip"].x == .2


def test_quality_breakdown_is_exposed():
    report = analyze_landmarks(demo_frames())
    assert report.data_quality == 100
    assert report.quality_breakdown["single_subject"] == 100
