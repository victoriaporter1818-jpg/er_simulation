import streamlit as st
import random
import time
import math
import pandas as pd

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
    "entered_diagnosis": "",
    "handoff_decision": None,
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --------------------------------------
# PATIENT DATA
# --------------------------------------
patients = [
    {
        "name": "John Doe",
        "age": 45,
        "symptoms": "severe chest pain and shortness of breath",
        "diagnosis": "Heart attack",
        "vitals": {"BP": "90/60", "HR": 120, "O2": "85%", "Temp": "37.0°C"},
    },
    {
        "name": "Sarah Li",
        "age": 29,
        "symptoms": "high fever, cough, and low oxygen",
        "diagnosis": "Pneumonia",
        "vitals": {"BP": "110/70", "HR": 95, "O2": "88%", "Temp": "39.2°C"},
    },
    {
        "name": "Carlos Vega",
        "age": 60,
        "symptoms": "sudden weakness on one side and slurred speech",
        "diagnosis": "Stroke",
        "vitals": {"BP": "150/90", "HR": 82, "O2": "97%", "Temp": "36.8°C"},
    },
]

# --------------------------------------
# DIAGNOSTIC RESULTS
# --------------------------------------
diagnostic_results = {
    "Heart attack": {
        "X-Ray": "Chest X-ray shows mild pulmonary congestion.",
        "CT Scan": "CT chest shows coronary artery calcifications.",
        "MRI": "MRI reveals myocardial ischemia.",
        "Ultrasound": "Echocardiogram shows reduced left ventricular function.",
        "CBC": "CBC within normal limits.",
        "Blood Test": "Troponin markedly elevated — myocardial infarction confirmed.",
        "Urinalysis": "Normal urinalysis.",
        "Biopsy": "Not indicated for acute coronary syndrome.",
    },
    "Pneumonia": {
        "X-Ray": "Chest X-ray shows right lower lobe infiltrates.",
        "CT Scan": "CT chest shows consolidation consistent with pneumonia.",
        "MRI": "MRI not typically indicated for pneumonia.",
        "Ultrasound": "Lung ultrasound shows B-lines and consolidation.",
        "CBC": "Elevated white blood cell count — infection likely.",
        "Blood Test": "Inflammatory markers elevated.",
        "Urinalysis": "Normal urinalysis.",
        "Biopsy": "Not indicated — infection suspected.",
    },
    "Stroke": {
        "X-Ray": "Chest X-ray unremarkable.",
        "CT Scan": "CT head shows acute ischemic changes.",
        "MRI": "MRI brain confirms ischemic stroke.",
        "Ultrasound": "Carotid ultrasound shows reduced flow.",
        "CBC": "CBC within normal limits.",
        "Blood Test": "Glucose mildly elevated.",
        "Urinalysis": "Normal urinalysis.",
        "Biopsy": "Not indicated for acute stroke.",
    },
}

# --------------------------------------
# CORE FUNCTIONS
# --------------------------------------
def assign_patient():
    st.session_state.patient = random.choice(patients)
    st.session_state.inventory.clear()
    st.session_state.score = 0
    st.session_state.treatment_history.clear()
    st.session_state.diagnostic_history.clear()
    st.session_state.patient_status = "Stable"
    st.session_state.case_start_time = time.time()
    st.session_state.last_update = time.time()
    st.session_state.mistakes = 0
    st.session_state.case_complete = False


def restart_simulation():
    for k, v in defaults.items():
        st.session_state[k] = v


def update_vitals(effect):
    if st.session_state.paused:
        return
    v = st.session_state.patient["vitals"]
    hr = int(v["HR"])
    o2 = int(v["O2"].replace("%", ""))

    if effect == "improve":
        hr = max(55, hr - random.randint(2, 6))
        o2 = min(100, o2 + random.randint(3, 6))
    else:
        hr = min(170, hr + random.randint(5, 10))
        o2 = max(65, o2 - random.randint(4, 8))

    v["HR"] = hr
    v["O2"] = f"{o2}%"


def gradual_deterioration():
    if st.session_state.paused:
        return
    if time.time() - st.session_state.last_update > 45:
        update_vitals("worsen")
        st.session_state.last_update = time.time()


def check_patient_outcome():
    if st.session_state.paused:
        return
    p = st.session_state.patient
    hr = int(p["vitals"]["HR"])
    o2 = int(p["vitals"]["O2"].replace("%", ""))

    if hr > 130 or hr < 45 or o2 < 85:
        st.session_state.patient_status = "Critical"
    else:
        st.session_state.patient_status = "Stable"

    if o2 <= 70 or hr >= 160 or hr <= 35 or st.session_state.mistakes >= 5:
        st.session_state.patient_status = "Deceased"
        st.session_state.case_complete = True

# --------------------------------------
# SIDEBAR
# --------------------------------------
with st.sidebar:
    st.header("⏸️ Game Control")

    if st.session_state.paused:
        if st.button("▶️ Resume"):
            st.session_state.paused = False
            st.session_state.last_update = time.time()
            st.rerun()
    else:
        if st.button("⏸️ Pause"):
            st.session_state.paused = True
            st.rerun()

    if st.session_state.paused:
        st.warning("Simulation Paused")

    st.divider()

    st.header("🏥 ER Simulation")
    st.session_state.room = st.radio(
        "Select Room",
        ["ER", "Supply Room", "Medstation", "Diagnostic Lab"]
    )

    st.subheader("📦 Inventory")
    if st.session_state.inventory:
        for i in st.session_state.inventory:
            st.write(f"- {i}")
    else:
        st.info("Inventory empty")

# --------------------------------------
# LAYOUT
# --------------------------------------
col2, col3 = st.columns([3.4, 1.3])

# --------------------------------------
# CENTER COLUMN
# --------------------------------------
with col2:

    # ================= ER =================
    if st.session_state.room == "ER":
        if not st.session_state.patient:
            st.header("🏥 Emergency Room")
            if st.button("🆕 Generate Patient"):
                assign_patient()
                st.rerun()
        else:
            gradual_deterioration()
            check_patient_outcome()

            p = st.session_state.patient
            st.subheader(f"Status: {st.session_state.patient_status}")
            st.write(f"❤️ HR: {p['vitals']['HR']} bpm")
            st.write(f"💨 O₂: {p['vitals']['O2']}")

            df = pd.DataFrame({"ECG": [math.sin(i / 5) for i in range(50)]})
            st.line_chart(df, height=120)

            st.divider()
            st.subheader("🧠 Clinical Reasoning")

            st.text_input(
                "Enter Working Diagnosis",
                key="entered_diagnosis",
                placeholder="e.g. Pneumonia, Stroke, Heart attack"
            )

            if st.button("Confirm Diagnosis"):
                if p["diagnosis"].lower() in st.session_state.entered_diagnosis.lower():
                    st.success("Correct diagnosis.")
                    st.session_state.score += 15
                else:
                    st.error("Incorrect diagnosis.")
                    st.session_state.mistakes += 1

            st.divider()
            st.subheader("📞 Patient Handoff")

            handoff = st.radio(
                "Choose Handoff Destination",
                ["Discharge", "Prep for Surgery", "Send to ICU"]
            )

            if st.button("Complete Handoff"):
                st.session_state.case_complete = True
                st.session_state.patient_status = "Stabilized"
                st.rerun()

            if st.session_state.case_complete:
                with st.expander("🏁 End-of-Case Summary", expanded=True):
                    st.metric("Final Score", st.session_state.score)
                    st.metric("Mistakes", st.session_state.mistakes)
                    if st.button("🔄 Start New Case"):
                        restart_simulation()
                        st.rerun()
                st.stop()

    # ================= SUPPLY ROOM =================
    elif st.session_state.room == "Supply Room":
        st.header("🛒 Supply Room")
        st.write("Supply room restored ✅")

    # ================= MEDSTATION =================
    elif st.session_state.room == "Medstation":
        st.header("💊 Medstation")
        st.write("Medstation restored ✅")

    # ================= DIAGNOSTIC LAB =================
    elif st.session_state.room == "Diagnostic Lab":
        st.header("🧪 Diagnostic Lab")
        st.write("Diagnostic lab restored ✅")

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
    if st.session_state.treatment_history:
        for entry in reversed(st.session_state.treatment_history):
            st.markdown(f"- {entry}")
    else:
        st.info("No actions taken yet.")

