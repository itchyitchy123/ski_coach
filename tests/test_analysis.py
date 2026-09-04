from ski_coach.demo import demo_frames
from ski_coach.geometry import angle
from ski_coach.io import frames_from_dict
from ski_coach.models import Landmark, PoseFrame
from ski_coach.pipeline import analyze_landmarks
from ski_coach.evaluation import evaluate_report, validate_labels
from ski_coach.batch import evaluate_dataset
from ski_coach.sensors import SensorSample, align_timestamps, detect_sensor_turns
from ski_coach.tracking import GPSPoint, summarize_track
import pytest


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


def test_evaluation_compares_labels():
    report = analyze_landmarks(demo_frames())
    labels = {"turns": [{"direction": turn.direction, "score": turn.score} for turn in report.turns_analysis]}
    result = evaluate_report(report, labels)
    assert result.direction_accuracy == 1.0
    assert result.count_error == 0


def test_evaluation_reports_timing_error():
    report = analyze_landmarks(demo_frames())
    turn = report.turns_analysis[0]
    labels = {"turns": [{"direction": turn.direction, "start_time": turn.start_time + .1, "end_time": turn.end_time + .2}]}
    result = evaluate_report(report, labels)
    assert result.matched_turns == 1
    assert result.mean_start_error == .1
    assert result.mean_end_error == .2
    assert result.mean_timing_error == .15


def test_invalid_labels_are_rejected():
    try:
        validate_labels({"turns": [{"direction": "left", "start_time": 2, "end_time": 1}]})
    except ValueError as exc:
        assert "invalid" in str(exc)
    else:
        raise AssertionError("invalid labels should fail validation")


def test_batch_runner_processes_landmark_fixture(tmp_path):
    clip = tmp_path / "clip-001"
    clip.mkdir()
    import json
    (clip / "landmarks.json").write_text(json.dumps({"frames": [
        {"timestamp": frame.timestamp, "landmarks": {name: {"x": point.x, "y": point.y, "visibility": point.visibility} for name, point in frame.landmarks.items()}}
        for frame in demo_frames()
    ]}), encoding="utf-8")
    result = evaluate_dataset(tmp_path)
    assert result.completed == 1
    assert result.failed == 0


def test_sensor_turn_detection_and_alignment():
    samples = [SensorSample(i / 10, rotation_rate=(0, 0, .5 if i < 6 else -.5)) for i in range(12)]
    assert len(detect_sensor_turns(samples, minimum_duration=.4)) == 2
    assert align_timestamps(samples, .25)[0].timestamp == .25


def test_gps_track_classifies_lift_run_and_stop():
    points = [
        GPSPoint(0, 46.8, 8.0, 1800, 0),
        GPSPoint(60, 46.801, 8.0, 1900, 5),
        GPSPoint(120, 46.803, 8.0, 1600, 10),
        GPSPoint(180, 46.804, 8.001, 1600, 0),
    ]
    summary = summarize_track(points)
    assert summary.runs == 1
    assert summary.lifts == 1
    assert summary.stopped_seconds == 60
    assert summary.vertical_descent_m == 300


def test_json_boundary_rejects_non_finite_and_unordered_timestamps():
    with pytest.raises(ValueError, match="finite"):
        frames_from_dict({"frames": [{"timestamp": "nan", "landmarks": {}}]})
    with pytest.raises(ValueError, match="ordered"):
        frames_from_dict({"frames": [
            {"timestamp": 1, "landmarks": {}},
            {"timestamp": 0, "landmarks": {}},
        ]})


def test_json_boundary_rejects_invalid_visibility_and_coordinates():
    with pytest.raises(ValueError, match="visibility"):
        frames_from_dict({"frames": [{"timestamp": 0, "landmarks": {
            "left_hip": {"x": 0.5, "y": 0.5, "visibility": 2},
        }}]})
