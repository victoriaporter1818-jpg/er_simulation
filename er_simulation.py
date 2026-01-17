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
# SESSION STATE
# --------------------------------------
if "inventory" not in st.session_state:
    st.session_state.inventory = []
if "room" not in st.session_state:
    st.session_state.room = "ER"
if "score" not in st.session_state:
    st.session_state.score = 0
if "patient" not in st.session_state:
    st.session_state.patient = None
if "treatment_history" not in st.session_state:
    st.session_state.treatment_history = []
if "last_update" not in st.session_state:
    st.session_state.last_update = time.time()
if "patient_status" not in st.session_state:
    st.session_state.patient_status = "Stable"
if "case_start_time" not in st.session_state:
    st.session_state.case_start_time = None
if "mistakes" not in st.session_state:
    st.session_state.mistakes = 0

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
# FUNCTIONS
# --------------------------------------
def assign_patient():
    p = random.choice(patients)
    st.session_state.patient = p
    st.session_state.inventory = []
    st.session_state.score = 0
    st.session_state.treatment_history = []
    st.session_state.patient_status = "Stable"
    st.session_state.case_start_time = time.time()
    st.session_state.last_update = time.time()
    st.session_state.mistakes = 0


def update_vitals(effect):
    p = st.session_state.patient
    v = p["vitals"]

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
    p["vitals"] = v


def gradual_deterioration():
    now = time.time()
    if now - st.session_state.last_update > 45:
        update_vitals("worsen")
        st.session_state.last_update = now


def check_patient_outcome():
    p = st.session_state.patient
    if not p:
        return

    hr = int(p["vitals"]["HR"])
    o2 = int(p["vitals"]["O2"].replace("%", ""))

    if hr > 130 or hr < 45 or o2 < 85:
        st.session_state.patient_status = "Critical"
    else:
        st.session_state.patient_status = "Stable"

    if o2 <= 70 or hr >= 160 or hr <= 35 or st.session_state.mistakes >= 5:
        st.session_state.patient_status = "Deceased"
        
def restart_simulation():
    st.session_state.patient = None
    st.session_state.inventory = []
    st.session_state.score = 0
    st.session_state.mistakes = 0
    st.session_state.patient_status = "Stable"
    st.session_state.case_start_time = None
    st.session_state.last_update = time.time()
    st.session_state.treatment_history = []
    st.session_state.room = "ER"

# --------------------------------------
# SIDEBAR
# --------------------------------------
with st.sidebar:
    st.header("🏥 ER Simulation")
    st.session_state.room = st.radio(
        "Select Room",
        ["ER", "Supply Room", "Medstation", "Diagnostic Lab"],
    )

    st.subheader("📦 Inventory")
    if st.session_state.inventory:
        for i in st.session_state.inventory:
            st.write(f"- {i}")
    else:
        st.info("Empty")

# --------------------------------------
# LAYOUT
# --------------------------------------
_, col2, col3 = st.columns([0.3, 3.4, 1.3])

# --------------------------------------
# CENTER COLUMN
# --------------------------------------
with col2:

    # ========= ER =========
    if st.session_state.room == "ER":

        if not st.session_state.patient:
            st.header("🏥 Emergency Room")
            if st.button("🆕 Generate Patient"):
                assign_patient()
                st.rerun()

        else:
            gradual_deterioration()
            check_patient_outcome()

            status_colors = {
                "Stable": "#2ecc71",
                "Critical": "#f1c40f",
                "Deceased": "#e74c3c",
            }

            st.markdown(
                f"<h3 style='color:{status_colors[st.session_state.patient_status]}'>"
                f"Patient Status: {st.session_state.patient_status}</h3>",
                unsafe_allow_html=True,
            )

            if st.session_state.patient_status == "Deceased":
                elapsed = int(time.time() - st.session_state.case_start_time)
                st.error("💀 Patient has died")
                st.write(f"⏱️ Time in care: {elapsed}s")
                st.write(f"❌ Mistakes: {st.session_state.mistakes}")
                st.write(f"🏆 Score: {st.session_state.score}")

                if st.button("🔄 Restart Simulation"):
                    restart_simulation()
                    st.rerun()
        

            p = st.session_state.patient
            vitals = p["vitals"]

            st.write(f"❤️ HR: {vitals['HR']} bpm")
            st.write(f"💨 O₂: {vitals['O2']}")

            df = pd.DataFrame(
                {"ECG": [math.sin(i / 5) for i in range(50)]}
            )
            st.line_chart(df, height=120)

            if st.session_state.inventory:
                item = st.selectbox("Use supply", st.session_state.inventory)
                if st.button("Use Item"):
                    correct = {
                        "Heart attack": ["Oxygen Mask"],
                        "Pneumonia": ["Oxygen Mask"],
                        "Stroke": ["Oxygen Mask"],
                    }
                    if item in correct.get(p["diagnosis"], []):
                        update_vitals("improve")
                        st.session_state.score += 5
                    else:
                        update_vitals("worsen")
                        st.session_state.mistakes += 1
                    st.session_state.inventory.remove(item)
                    st.session_state.last_update = time.time()
                    st.rerun()
            else:
                st.info("No supplies")

    # ========= SUPPLY ROOM =========
    elif st.session_state.room == "Supply Room":
        st.header("🛒 Supply Room")
        for item in ["Oxygen Mask", "IV Kit", "Defibrillator"]:
            if st.button(f"Add {item}"):
                st.session_state.inventory.append(item)
                st.rerun()

    # ========= MEDSTATION =========
    elif st.session_state.room == "Medstation":
        st.header("💊 Medstation")
        for med in ["Morphine", "Heparin"]:
            if st.button(f"Add {med}"):
                st.session_state.inventory.append(med)
                st.rerun()

    # ========= DIAGNOSTIC LAB =========
    elif st.session_state.room == "Diagnostic Lab":
        st.header("🧪 Diagnostic Lab")
        st.info("Diagnostics affect future versions")

# --------------------------------------
# RIGHT COLUMN
# --------------------------------------
with col3:
    st.subheader("👩‍⚕️ Patient Info")
    if st.session_state.patient:
        p = st.session_state.patient
        st.write(p["name"])
        st.write(p["symptoms"])

    st.subheader("🏆 Score")
    st.metric("Score", st.session_state.score)

