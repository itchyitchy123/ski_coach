from __future__ import annotations

import tempfile
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from ski_coach.demo import demo_frames
from ski_coach.pipeline import analyze_landmarks
from ski_coach.pose import extract_video_landmarks
from ski_coach.overlay import render_pose_overlay
from ski_coach.io import gps_points_from_dict

st.set_page_config(page_title="Ski Coach", page_icon="⛷️", layout="wide")
st.title("Ski Coach")
st.caption("Turn-by-turn technique feedback from a steady downhill/front-view video")

if "session_history" not in st.session_state:
    st.session_state.session_history = []

with st.sidebar:
    st.header("Session")
    level = st.selectbox("Skill level", ["beginner", "intermediate", "advanced", "expert"], index=1)
    terrain = st.selectbox("Terrain", ["groomer", "moguls", "powder", "steeps"])
    exercise = st.selectbox("Exercise", ["parallel turns", "carving", "short radius", "balance"])
    mode = st.radio("Input", ["Demo", "Upload video"])
    gps_upload = st.file_uploader("Optional GPS JSON", type=["json"])
    model_path = st.text_input("Pose model path", "models/pose_landmarker_lite.task", disabled=mode == "Demo")
    if st.session_state.session_history:
        st.divider()
        st.subheader("This session")
        for item in reversed(st.session_state.session_history[-5:]):
            st.caption(f"{item['label']}: {item['score']}/100 · {item['turns']} turns · quality {item['quality']}%")
        if st.button("Clear session history"):
            st.session_state.session_history = []
            st.rerun()

uploaded = None
if mode == "Upload video":
    uploaded = st.file_uploader("Ski video", type=["mp4", "mov", "m4v", "avi"])
    st.info("Best results: full skier visible, steady camera, downhill/front view, 6+ linked turns.")

run = st.button("Analyze run", type="primary", disabled=mode == "Upload video" and uploaded is None)
if run:
    try:
        with st.spinner("Tracking skier and comparing turns…"):
            if mode == "Demo":
                frames = demo_frames()
            else:
                max_upload_bytes = 200 * 1024 * 1024
                if uploaded.size > max_upload_bytes:
                    raise ValueError("Video is too large; maximum supported upload size is 200 MB.")
                suffix = Path(uploaded.name).suffix
                with tempfile.NamedTemporaryFile(suffix=suffix) as handle:
                    handle.write(uploaded.getbuffer())
                    handle.flush()
                    frames = extract_video_landmarks(handle.name, model_path)
                    overlay_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
                    overlay_file.close()
                    try:
                        render_pose_overlay(handle.name, frames, overlay_file.name)
                        st.subheader("Pose review")
                        st.video(overlay_file.name)
                    finally:
                        Path(overlay_file.name).unlink(missing_ok=True)
            gps_points = gps_points_from_dict(json.load(gps_upload)) if gps_upload else None
            report = analyze_landmarks(frames, level=level, terrain=terrain, exercise=exercise, gps_points=gps_points)
        st.session_state.session_history.append({
            "label": f"{terrain} · {exercise}",
            "score": report.overall_score,
            "turns": report.turns,
            "quality": report.data_quality,
        })
        cols = st.columns(5)
        for col, label, value in zip(cols, ["Overall", "Balance", "Symmetry", "Upper body", "Rhythm"], [report.overall_score, report.balance_score, report.symmetry_score, report.upper_body_score, report.rhythm_score]):
            col.metric(label, f"{value}/100")
        st.caption(f"Pose confidence: {report.confidence}% · Data quality: {report.data_quality}% · {report.turns} complete turns")
        st.subheader("Coach's notes")
        for note in report.feedback:
            st.write(f"• {note}")
        if report.feedback:
            st.info("Next-run focus: choose one coaching note above and repeat the run while tracking only that movement.")
        st.subheader("Next-run training plan")
        for item in report.recommendations:
            st.markdown(f"**{item['title']}** · {item['focus']} · {item['priority']} priority")
            st.write(item["drill"])
            st.caption(f"Success signal: {item['success_signal']}")
        for warning in report.warnings:
            st.warning(warning)
        if report.turns_analysis:
            st.subheader("Turn comparison")
            table = pd.DataFrame([vars(turn) for turn in report.turns_analysis])
            st.dataframe(table, hide_index=True, use_container_width=True)
            st.line_chart(table.set_index("turn")[["score", "knee_flex", "torso_angle"]])
        st.download_button("Download JSON report", json.dumps(report.to_dict(), indent=2), "ski-coach-report.json", "application/json")
    except Exception as exc:
        st.error(str(exc))
