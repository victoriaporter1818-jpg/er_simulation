import streamlit as st
import random
import time
import math
import pandas as pd
import altair as alt

# --------------------------------------
# PAGE CONFIGURATION
# --------------------------------------
st.set_page_config(
    page_title="Emergency Room Simulation",
    layout="wide",
    initial_sidebar_state="expanded"
)

from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=2000, key="ecg_refresh")

# --------------------------------------
# SESSION STATE INITIALIZATION
# --------------------------------------
defaults = {
    "inventory": [],
    "room": "ER",
    "score": 0,
    "patient": None,
    "treatment_history": [],
    "diagnostic_history": [],
    "last_update": time.time(),
    "patient_status": "Stable",
    "case_start_time": None,
    "mistakes": 0,
    "paused": False,
    "case_complete": False,
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

if "entered_diagnosis" not in st.session_state:
    st.session_state.entered_diagnosis = ""

if "handoff_decision" not in st.session_state:
    st.session_state.handoff_decision = None

# --------------------------------------
# PATIENT DATA
# --------------------------------------
patients = [
    {
        "name": "John Doe",
        "age": 45,
        "symptoms": "severe chest pain and shortness of breath",
        "diagnosis": "Heart attack",
        "vitals": {"BP": "90/60", "HR": 120, "O2": "85%", "RR": 28, "Temp": 37.0},
    },
    {
        "name": "Sarah Li",
        "age": 29,
        "symptoms": "high fever, cough, and low oxygen",
        "diagnosis": "Pneumonia",
        "vitals": {"BP": "110/70", "HR": 95, "O2": "88%", "RR": 26, "Temp": 39.2},
    },
    {
        "name": "Carlos Vega",
        "age": 60,
        "symptoms": "sudden weakness on one side and slurred speech",
        "diagnosis": "Stroke",
        "vitals": {"BP": "150/90", "HR": 82, "O2": "97%", "RR": 18, "Temp": 36.8},
    },
    {
        "name": "Emily Carter",
        "age": 34,
        "symptoms": "severe wheezing, chest tightness, difficulty speaking",
        "diagnosis": "Asthma exacerbation",
        "vitals": {"BP": "125/80", "HR": 118, "O2": "89%", "RR": 32, "Temp": 37.1},
    },
    {
        "name": "Robert Kim",
        "age": 72,
        "symptoms": "confusion, low body temperature, shivering",
        "diagnosis": "Hypothermia",
        "vitals": {"BP": "95/60", "HR": 54, "O2": "92%", "RR": 10, "Temp": 33.4},
    },
    {
        "name": "Aisha Hassan",
        "age": 26,
        "symptoms": "abdominal pain, vomiting, dizziness",
        "diagnosis": "Sepsis",
        "vitals": {"BP": "85/50", "HR": 135, "O2": "90%", "RR": 30, "Temp": 39.8},
    },
    {
        "name": "Mark Reynolds",
        "age": 58,
        "symptoms": "tearing chest pain radiating to the back",
        "diagnosis": "Aortic dissection",
        "vitals": {"BP": "190/110", "HR": 110, "O2": "96%", "RR": 24, "Temp": 36.9},
    },
]

# --------------------------------------
# ECG GENERATOR
# --------------------------------------
def generate_ecg(diagnosis, hr, length=120):
    ecg = []
    beat_interval = max(6, int(60 / max(hr, 40)))
    for i in range(length):
        baseline = random.uniform(-0.05, 0.05)
        if i % beat_interval == 0:
            spike = random.uniform(2.5, 4.0)
            ecg.append(spike + baseline)
        else:
            ecg.append(random.uniform(0.1, 0.3))
    return ecg

# --------------------------------------
# APPLY ITEM EFFECT (FIXED LOCATION)
# --------------------------------------
def apply_item_effect(item):
    p = st.session_state.patient
    dx = p["diagnosis"]
    v = p["vitals"]

    correct = False
    message = ""

    if item == "Oxygen Mask" and dx in ["Heart attack", "Pneumonia", "Asthma exacerbation", "Sepsis"]:
        v["O2"] = f"{min(100, int(v['O2'].replace('%','')) + 6)}%"
        correct = True
        message = "🫁 Oxygen improved oxygenation."

    elif item in ["Nebulizer", "Albuterol"] and dx == "Asthma exacerbation":
        v["RR"] = max(14, v["RR"] - 6)
        correct = True
        message = "🌬️ Bronchodilator relieved airway obstruction."

    elif item == "Broad-Spectrum Antibiotics" and dx == "Sepsis":
        v["Temp"] = max(36.5, v["Temp"] - 0.8)
        correct = True
        message = "🦠 Antibiotics improving infection control."

    elif item in ["Warming Blankets", "Blood Warmer"] and dx == "Hypothermia":
        v["Temp"] = min(37.0, v["Temp"] + 1.2)
        correct = True
        message = "🔥 Patient warmed successfully."

    elif item == "Beta Blocker" and dx == "Aortic dissection":
        v["HR"] = max(60, v["HR"] - 20)
        correct = True
        message = "🩺 Heart rate safely reduced."

    else:
        message = f"⚠️ {item} had limited effect."

    if correct:
        st.session_state.score += 8
    else:
        st.session_state.mistakes += 1

    st.session_state.treatment_history.append(message)
    st.session_state.last_update = time.time()
    return message

# --------------------------------------
# LAYOUT
# --------------------------------------
col2, col3 = st.columns([3.4, 1.3])

# --------------------------------------
# CENTER COLUMN
# --------------------------------------
with col2:

    if st.session_state.room == "ER":
        st.header("🏥 Emergency Room")

    elif st.session_state.room == "Supply Room":
        st.header("🛒 Supply Room")

    elif st.session_state.room == "Medstation":
        st.header("💊 Medstation")

    elif st.session_state.room == "Diagnostic Lab":
        st.header("🧪 Diagnostic Lab")

# --------------------------------------
# RIGHT COLUMN
# --------------------------------------
with col3:
    st.subheader("👩‍⚕️ Patient Info")
    if st.session_state.patient:
        st.write(st.session_state.patient["name"])
        st.write(st.session_state.patient["symptoms"])

    st.subheader("🏆 Score")
    st.metric("Total Score", st.session_state.score)

    st.divider()
    st.subheader("📋 Action Log")
    for entry in reversed(st.session_state.treatment_history):
        st.markdown(f"- {entry}")
